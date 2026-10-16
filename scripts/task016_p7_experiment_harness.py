"""Frozen A/B/E runner contract and independent raw-cell metrics."""
from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path

from scripts.task016_p7_closure_harness import canonical
from scripts.task016_p7_orchestrate import ContractError, ROOT, require_fields, require_int, sha_file, sha_json, verify_hashes

CONTRACT_FIELDS = ("task","panels","scope_bank_sha","runtime_manifest_sha","code_sha",
                   "model_hashes","review_binding","stock_keys","search_parameters","budget",
                   "metrics_definition","arms","seeds","matrix","qualified_p7_scope_ids")
ARM_DEFINITION = {"A":"generic_all_task016_off","B":"frozen_p6_v6","E":"p7_v7"}
TRACE_STAGES = ("generated","after_truncation","filtered_accepted","filtered_rejected","mcts_action_created")


def freeze_contract(contract):
    require_fields(contract, CONTRACT_FIELDS)
    if contract["arms"]!=ARM_DEFINITION or contract["seeds"]!=[0,1,2]:
        raise ContractError("A/B/E arm or seed contract changed")
    if contract["task"]!="TASK-016-P7" or not contract["qualified_p7_scope_ids"]:
        raise ContractError("P7 scope-qualified matrix required")
    if len(contract["stock_keys"])!=17 or len(set(contract["stock_keys"]))!=17:
        raise ContractError("stock17 contract drift")
    if not contract["code_sha"] or not contract["model_hashes"] or not contract["review_binding"]:
        raise ContractError("experiment binding incomplete")
    for field in ("scope_bank_sha","runtime_manifest_sha","metrics_definition"):
        if not contract[field]:
            raise ContractError("experiment freeze missing "+field)
    seen=set()
    counts=Counter()
    for cell in contract["matrix"]:
        require_fields(cell,("family","target_id","arm","seed"))
        identity=(cell["family"],cell["target_id"],cell["arm"],cell["seed"])
        if identity in seen or cell["family"] not in ("C","SS") or cell["arm"] not in ARM_DEFINITION or cell["seed"] not in [0,1,2]:
            raise ContractError("invalid/duplicate experiment cell")
        seen.add(identity);counts[(cell["family"],cell["target_id"])]+=1
    if not counts or any(count!=9 for count in counts.values()):
        raise ContractError("matrix must be complete three-arm x three-seed per target")
    for family in {key[0] for key in counts}:
        n=sum(key[0]==family for key in counts)
        if not 6<=n<=9:
            raise ContractError("matrix family floor/budget failed")
        if family not in contract["panels"]:
            raise ContractError("matrix lacks frozen panel")
    frozen=copy.deepcopy(contract)
    return dict(contract=frozen,contract_sha=sha_json(frozen))


def validate_runner_inputs(frozen,consumed_contract,*,root=ROOT,check_files=True):
    require_fields(frozen,("contract","contract_sha"))
    if sha_json(frozen["contract"])!=frozen["contract_sha"] or sha_json(consumed_contract)!=frozen["contract_sha"]:
        raise ContractError("runner cannot modify frozen contract")
    contract=frozen["contract"]
    freeze_contract(contract)
    if check_files:
        verify_hashes(contract["code_sha"],root=root)
        verify_hashes(contract["model_hashes"],root=root)
        for row in contract["panels"].values():
            require_fields(row,("path","sha256"))
            verify_hashes({row["path"]:row["sha256"]},root=root)
        for key in ("scope_bank_sha","runtime_manifest_sha"):
            value=contract[key]
            if not isinstance(value,dict):
                raise ContractError("frozen asset needs file path/SHA bindings")
            verify_hashes(value,root=root)
    return True


def load_raw_cells(observations,*,root=ROOT):
    cells=[]
    for row in observations:
        require_fields(row,("family","target_id","arm","seed","status","run_id","result_path","result_sha256"))
        path=root/row["result_path"]
        if not path.is_file() or sha_file(path)!=row["result_sha256"]:
            raise ContractError("raw MCTS result missing/SHA drift")
        result=json.loads(path.read_text())
        if result.get("run_id")!=row["run_id"] or result.get("status")!=row["status"]:
            raise ContractError("raw result/observation identity mismatch")
        cells.append(dict(**row,raw_result=result))
    return cells


def _generic_protection_trace(trace):
    """Recompute protected accepted distinct signatures within each expansion.

    The production trace emits a contiguous generated block, followed by generic
    protection checks and the selected after_truncation block. A new generated
    block for the same canonical target therefore starts another expansion.
    A rejected protection probe is an ordinary filter result, not displacement.
    """
    states={}
    groups=[]
    for row in trace:
        stage=row.get("stage")
        if stage not in ("generated","generic_protection_checked","after_truncation"):
            continue
        require_fields(row,("target","signature","metadata"))
        target=canonical(row["target"])
        if not isinstance(row["signature"],str) or not row["signature"] or not isinstance(row["metadata"],dict):
            raise ContractError("generic protection trace signature/metadata malformed")
        previous=states.get(target)
        new_group=(previous is None
                   or (stage=="generated" and previous["phase"]!="generated")
                   or (stage=="generic_protection_checked" and previous["phase"]=="after_truncation"))
        if new_group:
            state=dict(target=target,expansion_index=sum(g["target"]==target for g in groups),
                       phase=stage,protected=[],retained=set(),rejected_probes=0)
            states[target]=state;groups.append(state)
        else:
            state=previous
        state["phase"]=stage
        policy=row.get("policy",row["metadata"].get("policy_name"))
        generic=policy!="glycoside" and not row["metadata"].get("library_template")
        if stage=="generic_protection_checked":
            require_fields(row,("rejected",))
            if type(row["rejected"]) is not bool or not generic:
                raise ContractError("generic protection trace rejected flag/policy malformed")
            if row["rejected"]:
                state["rejected_probes"]+=1
            elif row["signature"] not in state["protected"] and len(state["protected"])<3:
                state["protected"].append(row["signature"])
        elif stage=="after_truncation" and generic:
            state["retained"].add(row["signature"])
    details=[]
    for state in groups:
        missing=set(state["protected"])-state["retained"]
        details.append(dict(target=state["target"],expansion_index=state["expansion_index"],
                            protected_accepted_distinct_signatures=state["protected"],
                            after_truncation_generic_signatures=sorted(state["retained"]),
                            missing_protected_signatures=sorted(missing),
                            rejected_probes=state["rejected_probes"],violations=len(missing)))
    return dict(violations=sum(g["violations"] for g in details),expansions=details)


def _reference_trace(result,reference_precursors,p7_scope_ids,reference_product):
    require_fields(result,("status","execution_source","action_trace","run_id"))
    expected=sorted(canonical(p) for p in reference_precursors)
    product=canonical(reference_product)
    retained=False;node=False;p7_retained=False;p7_node=False
    action_counts=Counter()
    actions={stage:set() for stage in TRACE_STAGES}
    protection=_generic_protection_trace(result["action_trace"])
    for row in result["action_trace"]:
        require_fields(row,("stage",))
        stage=row["stage"]
        if stage not in TRACE_STAGES:
            continue
        require_fields(row,("precursor_smiles","signature","template_id","metadata","target"))
        action_counts[stage]+=1
        actions[stage].add(row["signature"])
        if canonical(row["target"])!=product or sorted(canonical(p) for p in row["precursor_smiles"])!=expected:
            continue
        metadata=row["metadata"]
        template=metadata.get("library_template",{})
        scope_id=template.get("scope_id",template.get("template_id",row["template_id"]))
        role=template.get("template_role")
        review=metadata.get("review",{})
        provenance=review.get("task016_p7",metadata.get("task016_p7",{}))
        exact=provenance.get("exact_seed_instance_match")
        p7=scope_id in p7_scope_ids and role=="scope_template" and exact is False
        if stage=="filtered_accepted":
            retained=True;p7_retained|=p7
        if stage=="mcts_action_created":
            require_fields(row,("created_node_count","created_node_index","created_child_slot","created_outcome_index"))
            require_int(row["created_node_count"],"created_node_count",minimum=1)
            require_int(row["created_node_index"],"created_node_index",minimum=1)
            require_int(row["created_child_slot"],"created_child_slot")
            require_int(row["created_outcome_index"],"created_outcome_index")
            # These fields are emitted at successful live tree-child creation,
            # rather than candidate-list construction.
            node=True;p7_node|=p7
    real=result["execution_source"]=="live_aizynthfinder_mcts"
    normal=result["status"]=="ok"
    return dict(normal=normal,real_mcts=real,retained=retained,node_created=node,
                p7_retained=p7_retained,p7_node_created=p7_node,
                counts=dict(action_counts),actions={key:sorted(value) for key,value in actions.items()},
                generic_top3_protection_violations=protection["violations"],
                generic_top3_protection_checks=protection["expansions"])


def validate_cells(frozen,raw_cells,*,allow_fixture=False,root=ROOT):
    contract=frozen["contract"]
    validate_runner_inputs(frozen,contract,check_files=False)
    expected=Counter((row["family"],row["target_id"],row["arm"],row["seed"]) for row in contract["matrix"])
    actual=Counter()
    run_ids=set()
    for cell in raw_cells:
        require_fields(cell,("family","target_id","arm","seed","raw_result","started","terminal",
                             "contract_sha","synthetic_fixture"))
        if cell["contract_sha"]!=frozen["contract_sha"]:
            raise ContractError("cell ran a different contract")
        if cell["started"] is not True or cell["terminal"] is not True:
            raise ContractError("cells planned != started != terminal")
        if cell["synthetic_fixture"] and not allow_fixture:
            raise ContractError("synthetic fixture cannot enter scientific metrics")
        result=cell["raw_result"]
        require_fields(result,("run_id","status","execution_source","action_trace"))
        if result["run_id"] in run_ids:
            raise ContractError("one raw run cannot satisfy multiple matrix cells")
        run_ids.add(result["run_id"])
        if not cell["synthetic_fixture"] and result["execution_source"]!="live_aizynthfinder_mcts":
            raise ContractError("cell has no live MCTS provenance")
        if not cell["synthetic_fixture"]:
            require_fields(cell,("result_path","result_sha256","run_id"))
            path=root/cell["result_path"]
            if not path.is_file() or sha_file(path)!=cell["result_sha256"] or json.loads(path.read_text())!=result:
                raise ContractError("scientific metrics require immutable raw result file")
            if result["run_id"]!=cell["run_id"]:
                raise ContractError("cell/run identity mismatch")
            require_fields(result,("request",))
            request=result["request"]
            if request.get("seed")!=cell["seed"]:
                raise ContractError("cell/raw seed mismatch")
            version=request.get("glycoside_library_version")
            enabled=request.get("glycoside_expansion",False)
            expected_version={"A":None,"B":"v6","E":"v7"}[cell["arm"]]
            if version!=expected_version or bool(enabled)!=(cell["arm"]!="A"):
                raise ContractError("cell/raw A/B/E arm mismatch")
            for parameter,value in contract["search_parameters"].items():
                if request.get(parameter)!=value:
                    raise ContractError("cell/raw search parameter mismatch: "+parameter)
        actual[(cell["family"],cell["target_id"],cell["arm"],cell["seed"])]+=1
    if expected!=actual:
        raise ContractError("A/B/E planned cells != unique terminal raw cells")
    if len(raw_cells)>162:
        raise ContractError("first matrix budget exceeded")
    return dict(planned=sum(expected.values()),started=len(raw_cells),terminal=len(raw_cells),
                real_mcts=sum(not cell["synthetic_fixture"] for cell in raw_cells),
                synthetic_fixture=sum(bool(cell["synthetic_fixture"]) for cell in raw_cells))


def recompute_metrics(frozen,raw_cells,references,*,allow_fixture=False):
    accounting=validate_cells(frozen,raw_cells,allow_fixture=allow_fixture)
    contract=frozen["contract"]
    ref_index={}
    for ref in references:
        require_fields(ref,("family","target_id","reference_precursors","closure_group","product_smiles"))
        key=(ref["family"],ref["target_id"])
        if key in ref_index:
            raise ContractError("duplicate frozen reference")
        ref_index[key]=ref
    checks={}
    for cell in raw_cells:
        key=(cell["family"],cell["target_id"])
        if key not in ref_index:
            raise ContractError("matrix target lacks frozen complete reference")
        checks[(key[0],key[1],cell["arm"],cell["seed"])]=_reference_trace(
            cell["raw_result"],ref_index[key]["reference_precursors"],contract["qualified_p7_scope_ids"],ref_index[key]["product_smiles"])
    out={}
    for family in sorted({key[0] for key in ref_index}):
        targets=sorted(key[1] for key in ref_index if key[0]==family)
        gaps=[];gains=[];nodes=[];losses=[];coverage=Counter();target_details=[];displacements=[]
        for target in targets:
            arms={arm:[checks[(family,target,arm,seed)] for seed in (0,1,2)] for arm in ARM_DEFINITION}
            all_normal={arm:all(row["normal"] for row in rows) for arm,rows in arms.items()}
            all_retained={arm:all_normal[arm] and all(row["retained"] for row in rows) for arm,rows in arms.items()}
            for arm,retained in all_retained.items():
                coverage[arm]+=int(retained)
            gap=all_normal["A"] and all_normal["B"] and all(not row["retained"] for arm in ("A","B") for row in arms[arm])
            gain=gap and all_normal["E"] and all(row["p7_retained"] for row in arms["E"])
            node=all(all_normal.values()) and all(not row["node_created"] for arm in ("A","B") for row in arms[arm]) and all(row["p7_node_created"] for row in arms["E"])
            if gap:gaps.append(target)
            if gain:gains.append(target)
            if node:nodes.append(target)
            if any(arms[base][seed]["normal"] and arms[base][seed]["retained"] and (not arms["E"][seed]["normal"] or not arms["E"][seed]["retained"])
                   for base in ("A","B") for seed in (0,1,2)):
                losses.append(target)
            for seed in (0,1,2):
                e=set(arms["E"][seed]["actions"]["filtered_accepted"])
                for base in ("A","B"):
                    b=set(arms[base][seed]["actions"]["filtered_accepted"])
                    displacements.append(dict(target_id=target,seed=seed,baseline=base,
                                              added=sorted(e-b),removed=sorted(b-e),
                                              unknown_nonreference_action_value=True))
            target_details.append(dict(target_id=target,arms=arms,gap=gap,gain=gain,node_transfer=node))
        gain_groups={ref_index[(family,target)]["closure_group"] for target in gains}
        node_groups={ref_index[(family,target)]["closure_group"] for target in nodes}
        groups={ref_index[(family,target)]["closure_group"] for target in targets}
        ratio=len(gains)/len(gaps) if gaps else None
        protection=sum(row["generic_top3_protection_violations"] for key,row in checks.items() if key[0]==family)
        scientific=accounting["synthetic_fixture"]==0
        passed=(len(targets)>=6 and len(groups)>=2 and len(gains)>=3 and ratio is not None and ratio>=0.5
                and len(gain_groups)>=2 and len(nodes)>=3 and len(node_groups)>=2
                and coverage["E"]>coverage["A"] and coverage["E"]>coverage["B"]
                and not losses and protection==0 and scientific)
        out[family]=dict(N=len(targets),closure_groups=len(groups),N_gap=len(gaps),G=len(gains),
                         G_over_N_gap=ratio,successful_transfer_groups=len(gain_groups),
                         node_transfer_targets=len(nodes),node_transfer_groups=len(node_groups),
                         complete_reference_coverage=dict(coverage),
                         net_complete_reference_vs_A=coverage["E"]-coverage["A"],
                         net_complete_reference_vs_B=coverage["E"]-coverage["B"],
                         reference_loss=len(losses),reference_loss_targets=losses,
                         generic_top3_protection_violations=protection,
                         action_changes=displacements,target_checks=target_details,
                         completion_passed=passed,scientific_metrics=scientific)
    return dict(accounting=accounting,metrics_by_family=out,
                overall_completion_passed=set(out)=={"C","SS"} and all(row["completion_passed"] for row in out.values()),
                metrics_source="independent recomputation from immutable raw action_trace",
                raw_cells_sha=sha_json(raw_cells))

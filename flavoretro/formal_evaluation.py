"""TASK-017 research admission and one-attempt evaluation.

Task-local scientific evidence is separate from legacy preflight and release.
Independent labels are imported evidence; this module never generates gold.
"""
import fcntl
import hashlib
import json
import os
import random
from collections import Counter
from pathlib import Path

from rdkit import Chem
from .contracts import SearchRequest
from .service import search
from .workspace import root

PARAMETERS = dict(engine="optimized", mode="quick", candidate_stock=True,
                  top_k=5, seconds=30.0, iterations=100, depth=6,
                  branching=12, nodes=2000)
ARMS = {"A": dict(glycoside_expansion=False, glycoside_library_version="v1"),
        "B": dict(glycoside_expansion=True, glycoside_library_version="v3"),
        "E": dict(glycoside_expansion=True, glycoside_library_version="v6")}
SEEDS = (0, 1, 2)
DOCUMENTS = ("approval.json", "approved_task.md", "method.json",
             "preparation_plan.json", "panel.json", "labels.json",
             "closure.json", "protocol.json", "protocol_review.json",
             "implementation_validation.json", "schedule.json")
REQUIRED_TESTS = ("preparation_without_gold", "vendor_nonblocking",
                  "missing_labels", "missing_protocol", "closure_leakage",
                  "hash_drift", "test_feedback", "fixed_denominator",
                  "component_multiplicity", "real_result_binding",
                  "legacy_compatibility", "one_attempt")
PROFILE = "task017_research"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_json(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def multiset(values):
    """Canonical fragments retain chirality, isotope, charge and multiplicity."""
    pieces = []
    if not isinstance(values, list) or not values:
        raise ValueError("empty precursor collection")
    for value in values:
        mol = Chem.MolFromSmiles(value)
        if mol is None or not mol.GetNumAtoms() or any(
                a.GetAtomicNum() == 0 or a.GetNumRadicalElectrons()
                for a in mol.GetAtoms()):
            raise ValueError("invalid or incomplete structure")
        if any(label == "?" for _, label in
               Chem.FindMolChiralCenters(mol, includeUnassigned=True)):
            raise ValueError("unassigned stereochemistry")
        for atom in mol.GetAtoms():
            atom.SetAtomMapNum(0)
        pieces.extend(Chem.MolToSmiles(fragment, isomericSmiles=True)
                      for fragment in Chem.GetMolFrags(mol, asMols=True))
    return tuple(sorted(pieces))


def reaction_key(product, precursors):
    return ".".join(multiset(precursors)) + ">>" + ".".join(multiset([product]))


def contains_fixture(value):
    if isinstance(value,dict):
        return bool(value.get("synthetic_fixture") or value.get("fixture_only")) or any(
            contains_fixture(x) for x in value.values())
    return isinstance(value,list) and any(contains_fixture(x) for x in value)


def safe_file(workspace, value):
    path = (Path(workspace) / value).resolve()
    if not path.is_relative_to(Path(workspace).resolve()) or not path.is_file():
        raise ValueError("missing or out-of-workspace evidence: " + str(value))
    return path


def evidence(workspace, record):
    path = safe_file(workspace, record["file"])
    if sha(path) != record["sha256"] or not record.get("locator"):
        raise ValueError("unbound source evidence")
    return path


def make_schedule(panel):
    cells = [dict(target_id=t["target_id"], arm=a, seed=s)
             for t in sorted(panel, key=lambda t: t["target_id"])
             for s in SEEDS for a in ARMS]
    random.Random(20261013).shuffle(cells)
    return cells


def check_bundle(folder, workspace=None, synthetic=False):
    """Inspect real files and relations. synthetic results never authorize run."""
    folder = Path(folder).resolve()
    workspace = Path(workspace or root()).resolve()
    checks = []
    docs = {}
    def verify(name, stage, callback):
        try:
            passed = bool(callback())
            error = None
        except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
            passed, error = False, str(exc)
        checks.append(dict(check=name, stage=stage, passed=passed, error=error))
        return passed
    def doc(name):
        if name not in docs:
            docs[name] = read(folder/name)
        return docs[name]
    def authority():
        a = doc("approval.json")
        return (a["task"] == "TASK-017" and a["version"] == "v0.2"
                and a["authority"] == "agent_delegated"
                and a["human_reviewed"] is False
                and a["contract_sha256"] == sha(folder/"approved_task.md")
                and bool(a["owner_instruction"]))
    verify("execution_authority", "preparation", authority)

    def method_ok():
        m = doc("method.json")
        if (m["parameters"] != PARAMETERS or m["arms"] != ARMS
                or m["seeds"] != list(SEEDS) or m["schedule_seed"] != 20261013
                or m["candidate_stock_keys"] != 17
                or not m["frozen_before_new_metadata"]):
            return False
        files = m["files_sha256"]
        required = {"flavoretro/search.py", "flavoretro/worker.py",
                    "flavoretro/service.py", "flavoretro/contracts.py",
                    "configs/search.json", "metadata/active.json",
                    "configs/glycoside-library-v3.json",
                    "configs/glycoside-library-v6.json"}
        if not required.issubset(files):
            return False
        if not all(sha(safe_file(workspace, p)) == h for p, h in files.items()):
            return False
        for cfg in ("configs/glycoside-library-v3.json",
                    "configs/glycoside-library-v6.json"):
            config = read(workspace/cfg)
            manifest = safe_file(workspace, config["manifest"])
            if sha(manifest) != config["manifest_sha256"]:
                return False
            for p,h in read(manifest)["files_sha256"].items():
                if sha(manifest.parent/p) != h:
                    return False
        request = SearchRequest(smiles="CCO", seed=0, **PARAMETERS, **ARMS["A"])
        return request.phases() == [{k: PARAMETERS[k] for k in
                                    ("seconds","iterations","depth","branching","nodes")}]
    verify("method_assets_and_single_phase", "preparation", method_ok)

    def plan_ok():
        p = doc("preparation_plan.json")
        queries = p["queries"]
        return (p["contract_sha256"] == sha(folder/"approved_task.md")
                and p["method_sha256"] == sha(folder/"method.json")
                and len(queries) == 12
                and Counter(q["axis"] for q in queries) == {"C":6, "SS":6}
                and len({q["id"] for q in queries}) == 12
                and all(q["metadata_only"] and 0 < q["limit"] <= 8 for q in queries)
                and p["query_rounds"] == 1
                and p["roles"]["engineering_executor"] == "Cano"
                and p["handoff"]["prohibit_test_to_method"]
                and p["handoff"]["prohibit_model_output_to_reviewer"]
                and not p["stopped_content_policy"]["reopen_epochs"]
                and not p["stopped_content_policy"]["read_Liu2021_R73_R80"])
    verify("bounded_legal_plan_and_isolation", "preparation", plan_ok)

    def budget_ok():
        a = doc("approval.json")
        limits = a["budgets"]
        usage = doc("budget_current.json")
        journal=workspace/"operations/events.jsonl"
        actual_commands=usage["local_commands"]
        if journal.is_file() and a.get("original_operation_start_line"):
            rows=journal.read_text().splitlines()[a["original_operation_start_line"]-1:]
            actual_commands=sum(json.loads(line).get("action")=="command_start"
                and json.loads(line).get("task","").startswith("TASK-017")
                for line in rows)+a["unjournalled_bootstrap_commands"]
        return (limits["local_commands"] == 120
                and limits["queries"] == 12 and limits["http_attempts"] == 120
                and limits["all_run_attempts"] == 345
                and usage["local_commands"] <= 120 and actual_commands <= 120 and usage["queries"] <= 12
                and usage["http_attempts"] <= 120
                and usage["download_bytes"] <= 536870912
                and usage["all_run_attempts"] <= 345
                and usage["science_attempts"] <= 270
                and usage["engineering_attempts"] <= 24)
    verify("cumulative_budget", "preparation", budget_ok)

    def roles_ok():
        a = doc("approval.json")
        for reviewer in a["permitted_label_reviewers"]:
            evidence(workspace, reviewer["authority_evidence"])
            if reviewer.get("agent") or not reviewer["id"]:
                return False
        # Preparation can remain restricted to metadata/fixtures before nomination.
        return bool(doc("preparation_plan.json")["allowed_operations"])
    verify("role_plan", "preparation", roles_ok)

    def panel_ok():
        rows = doc("panel.json")
        if not isinstance(rows,list) or len(rows)>30:
            return False
        ids, products = set(), set()
        counts = Counter()
        for row in rows:
            product = multiset([row["product_smiles"]])
            if (row["target_id"] in ids or product in products
                    or row["axis"] not in ("C","SS","O")
                    or not row["references"]
                    or not all(row["strata"].get(k) for k in
                               ("core","site","sugar","donor","catalysis","source"))):
                return False
            ids.add(row["target_id"]); products.add(product); counts[row["axis"]] += 1
            for ref in row["references"]:
                full = Counter(multiset(ref["precursors"]))
                needed = Counter(multiset([ref["acceptor"],ref["donor"]]))
                if needed-full or not ref["primary_evidence"]:
                    return False
                key = reaction_key(row["product_smiles"],ref["precursors"])
                for ev in ref["primary_evidence"]:
                    evidence(workspace,ev)
                    if ev["reaction_key"] != key:
                        return False
        return 6<=counts["C"]<=12 and 6<=counts["SS"]<=12 and counts["O"]<=6
    verify("complete_panel_and_primary_references", "research", panel_ok)

    def closure_ok():
        c = doc("closure.json")
        rows = doc("panel.json")
        nodes = {n["id"]:n for n in c["nodes"]}
        parent = {key:key for key in nodes}
        def find(key):
            while parent[key] != key:
                parent[key] = parent[parent[key]]
                key = parent[key]
            return key
        def union(a,b):
            a,b=find(a),find(b)
            parent[max(a,b)] = min(a,b)
        aliases = {}
        for key,node in nodes.items():
            if not node["aliases"]:
                return False
            for alias in node["aliases"]:
                alias=alias.strip().lower()
                if alias in aliases:
                    union(key,aliases[alias])
                aliases[alias]=key
        for edge in c["edges"]:
            if edge["basis"] not in ("doi","patent_family","assay","cohort",
                                     "parent_instance","exact_reaction","source_identity"):
                return False
            evidence(workspace,edge["evidence"])
            union(edge["left"],edge["right"])
        for ev in c["development_inventory_evidence"]:
            evidence(workspace,ev)
        if not c["development_inventory_evidence"] or not c["development_coverage_reviewed"]:
            return False
        inventories=[read(evidence(workspace,ev)) for ev in c["development_inventory_evidence"]]
        expected_nodes={key for inv in inventories for key in inv["source_nodes"]}
        expected_products={multiset([p]) for inv in inventories for p in inv["products"]}
        expected_reactions={key for inv in inventories for key in inv["reaction_keys"]}
        if (set(c["development_nodes"])!=expected_nodes
                or {multiset([p]) for p in c["development_products"]}!=expected_products
                or set(c["development_reaction_keys"])!=expected_reactions):
            return False
        development = {find(key) for key in expected_nodes}
        dev_products = expected_products
        dev_reactions = expected_reactions
        groups = {"C":set(),"SS":set()}
        for row in rows:
            if (find(row["source_node"]) in development
                    or multiset([row["product_smiles"]]) in dev_products
                    or any(reaction_key(row["product_smiles"],r["precursors"])
                           in dev_reactions for r in row["references"])
                    or row["target_id"] in c["development_exposed_targets"]
                    or row["target_id"] in c["unresolved_independence_targets"]):
                return False
            if row["source_group"] != find(row["source_node"]):
                return False
            for ref in row["references"]:
                if any(find(ev["source_node"])!=find(row["source_node"])
                       for ev in ref["primary_evidence"]):
                    return False
            if row["axis"] in groups:
                groups[row["axis"]].add(find(row["source_node"]))
        return all(len(value)>=2 for value in groups.values())
    verify("actual_source_closure_and_exposure", "research", closure_ok)

    def labels_ok():
        a = doc("approval.json")
        authorized = {r["id"] for r in a["permitted_label_reviewers"] if not r["agent"]}
        labels = doc("labels.json")
        rows = doc("panel.json")
        if len(labels)!=len(rows) or len({x["target_id"] for x in labels})!=len(rows):
            return False
        by_id = {r["target_id"]:r for r in rows}
        for label in labels:
            row=by_id[label["target_id"]]
            if (label["reviewer_id"] not in authorized
                    or not all(label[k] is True for k in
                               ("domain_confirmed","stereochemistry_confirmed","primary_reference_confirmed"))
                    or label.get("method_feedback") or label.get("agent_generated_gold")
                    or label.get("exposure_role")!="evaluation_labeling"
                    or multiset([label["product_smiles"]])!=multiset([row["product_smiles"]])
                    or {multiset(r) for r in label["references"]} !=
                       {multiset(r["precursors"]) for r in row["references"]}):
                return False
            verdict=read(evidence(workspace,label["approval_evidence"]))
            if not synthetic and contains_fixture(verdict):
                return False
            owner_rows={x["target_id"]:x for x in verdict["decisions"]}
            owner=owner_rows[label["target_id"]]
            if (verdict["reviewer_id"]!=label["reviewer_id"] or not verdict["reviewed_at"]
                    or multiset([owner["product_smiles"]])!=multiset([label["product_smiles"]])
                    or {multiset(r) for r in owner["references"]} !=
                       {multiset(r) for r in label["references"]}
                    or any(owner[k] is not True for k in
                           ("domain_confirmed","stereochemistry_confirmed","primary_reference_confirmed"))):
                return False
            if label["origin"] == "literature_double_source":
                chains=label["independent_chains"]
                if len({x["source_group"] for x in chains})<2:
                    return False
                for chain in chains:
                    evidence(workspace,chain)
                    if chain["reaction_keys"]!=sorted(
                            reaction_key(row["product_smiles"],r["precursors"])
                            for r in row["references"]):
                        return False
            elif label["origin"]!="owner_verified":
                return False
        return bool(labels)
    verify("independent_labels_and_role_provenance", "research", labels_ok)

    def protocol_ok():
        p = doc("protocol.json")
        review=doc("protocol_review.json")
        authorized={r["id"] for r in doc("approval.json")["permitted_label_reviewers"]}
        actual_review=read(evidence(workspace,review["approval_evidence"]))
        if (actual_review["reviewer_id"]!=review["reviewer_id"]
                or actual_review["status"]!="approved"
                or actual_review["protocol_sha256"]!=sha(folder/"protocol.json")
                or actual_review["panel_sha256"]!=sha(folder/"panel.json")
                or actual_review["labels_sha256"]!=sha(folder/"labels.json")
                or actual_review["reviewed_at"]!=review["reviewed_at"]
                or actual_review["scope"]!="frozen_panel_labels_method_execution"):
            return False
        legacy=read(evidence(workspace,p["legacy_protection"]["evidence"]))
        expected_code={name:h for name,h in doc("method.json")["files_sha256"].items()
                       if name.startswith("flavoretro/") and name.endswith(".py")}
        if (legacy["method_sha256"]!=sha(folder/"method.json")
                or legacy["code_sha256"]!=expected_code or not legacy["source_evidence"]):
            return False
        for source in legacy["source_evidence"]:
            evidence(workspace,source)
        return (p["parameters"]==PARAMETERS and p["arms"]==ARMS
                and p["seeds"]==list(SEEDS) and p["schedule_seed"]==20261013
                and p["primary"]=="E-A" and p["secondary"]=="E-B"
                and p["denominator"]=="all_registered_targets"
                and p["bootstrap_replicates"]==2000
                and p["bootstrap_seed"]==20261013 and p["interval_percent"]==97.5
                and p["panel_sha256"]==sha(folder/"panel.json")
                and p["method_sha256"]==sha(folder/"method.json")
                and review["protocol_sha256"]==sha(folder/"protocol.json")
                and review["contract_sha256"]==sha(folder/"approved_task.md")
                and review["reviewer_id"] in authorized
                and review["status"]=="approved" and bool(review["reviewed_at"])
                and review["scope"]=="frozen_panel_labels_method_execution"
                and p["legacy_protection"]["verified"] is True)
    verify("frozen_protocol_actual_review_and_legacy_protection", "research", protocol_ok)

    verify("fixed_schedule_and_denominator","research",
           lambda: doc("schedule.json")==make_schedule(doc("panel.json"))
           and len(doc("schedule.json"))<=270)

    def implementation_ok():
        v=doc("implementation_validation.json")
        actual_tests=read(evidence(workspace,v["test_evidence"]))
        if (actual_tests["failures"] or actual_tests["errors"]
                or not all(actual_tests["requirements"].get(k) is True for k in REQUIRED_TESTS)
                or actual_tests["tests_run"] < len(REQUIRED_TESTS)):
            return False
        for p,h in v["code_sha256"].items():
            if sha(safe_file(workspace,p))!=h:
                return False
        return (not v["failures"] and v["synthetic_only"] is True
                and all(v["requirements"].get(key) is True for key in REQUIRED_TESTS)
                and "flavoretro/formal_evaluation.py" in v["code_sha256"]
                and "scripts/task017_formal.py" in v["code_sha256"]
                and "tests/test_task017_formal.py" in v["code_sha256"])
    verify("executor_synthetic_validation_bound_to_code","research",implementation_ok)

    def seal_ok():
        seal=doc("frozen_inputs.json")
        required=set(DOCUMENTS)|{"budget_current.json"}
        if not required.issubset(seal["files_sha256"]):
            return False
        if seal["contract_sha256"]!=sha(folder/"approved_task.md"):
            return False
        return all(sha(folder/p)==h for p,h in seal["files_sha256"].items())
    verify("frozen_input_seal","research",seal_ok)
    verify("no_synthetic_evidence_in_actual_run","research",
           lambda: synthetic or not any(contains_fixture(value) for value in docs.values()))
    preparation=all(c["passed"] for c in checks if c["stage"]=="preparation")
    research=preparation and all(c["passed"] for c in checks)
    release = read(workspace/"metadata/release.json") if (workspace/"metadata/release.json").exists() else {}
    legacy_path=workspace/"outputs/evaluation/formal-task017-v1/preflight.json"
    legacy=read(legacy_path) if legacy_path.is_file() else {}
    production=legacy.get("engineering",{}).get("production_projection_counts",{})
    return dict(profile=PROFILE, contract_sha256=(
                    sha(folder/"approved_task.md") if (folder/"approved_task.md").exists() else None),
                preparation_ready=preparation, research_run_ready=research,
                evidence_scope="synthetic_logic_only" if synthetic else "actual_task_evidence",
                inputs_sha256={name:sha(folder/name) for name in
                               (*DOCUMENTS,"budget_current.json") if (folder/name).is_file()},
                checks=checks,
                blocking_reasons=[c["check"] for c in checks if not c["passed"]],
                preparation_scope=doc("preparation_plan.json").get("allowed_operations",[])
                    if (folder/"preparation_plan.json").exists() else [],
                nonblocking_status={k:release.get(k,"unresolved") for k in
                                    ("primary_source_review","current_vendor_evidence")},
                production_projection_counts=production,
                production_certification="not_granted",
                legacy_formal_run_ready=legacy.get("formal_run_ready"),
                release_ready=False)


def freeze_bundle(folder):
    folder=Path(folder)
    if (folder/"panel.json").is_file() and not (folder/"schedule.json").exists():
        write_json(folder/"schedule.json",make_schedule(read(folder/"panel.json")),exclusive=True)
    report=check_bundle(folder)
    blockers=set(report["blocking_reasons"])-{"frozen_input_seal"}
    if blockers:
        raise ValueError("cannot freeze: "+", ".join(sorted(blockers)))
    if (folder/"frozen_inputs.json").exists():
        raise ValueError("sealed bundle already exists")
    write_json(folder/"frozen_inputs.json",
               dict(contract_sha256=sha(folder/"approved_task.md"),
                    files_sha256={p:sha(folder/p) for p in
                                  (*DOCUMENTS,"budget_current.json")}),exclusive=True)
    result=check_bundle(folder)
    if not result["research_run_ready"]:
        raise ValueError("sealed bundle failed admission")
    return result


def parse_result(folder, target, cell, method):
    folder=Path(folder)
    manifest=read(folder/"manifest.json")
    result=read(folder/"result.json")
    request=SearchRequest(smiles=target["product_smiles"], seed=cell["seed"],
                          **method["parameters"], **method["arms"][cell["arm"]]).payload()
    if read(folder/"request.json")!=request:
        raise ValueError("request/result binding mismatch")
    if (result.get("run_id")!=manifest.get("run_id")
            or result.get("status")!=manifest.get("status")
            or not {"request.json","result.json","worker.log"}.issubset(manifest["files"])):
        raise ValueError("incomplete actual run manifest")
    for name,h in manifest["files"].items():
        p=(folder/name).resolve()
        if not p.is_relative_to(folder.resolve()) or sha(p)!=h:
            raise ValueError("run file hash drift")
    base=dict(**cell,run_id=result["run_id"],status=result["status"],
              full_reference_created=None, stage_matches={}, search_seconds=None,
              created_nodes=None, reference_gain_loss=None,
              run_folder=str(folder),manifest_sha256=sha(folder/"manifest.json"))
    if result["status"]!="ok":
        return dict(base,error=result.get("error",{"code":"worker_error"}))
    if (result.get("execution_source")!="live_aizynthfinder_mcts"
            or result.get("request")!=request or "action_trace" not in result):
        raise ValueError("normal result lacks live MCTS request/trace evidence")
    if result["review_binding"]["manifest_sha256"]!=method["review_manifest_sha256"]:
        raise ValueError("actual review binding mismatch")
    if cell["arm"]!="A":
        domain=method["domains"][0 if cell["arm"]=="B" else 1]
        if result["domain_binding"]["manifest_sha256"]!=domain["manifest_sha256"]:
            raise ValueError("actual domain binding mismatch")
    for path,h in method.get("files_sha256",{}).items():
        if path.startswith("flavoretro/") and path.endswith(".py") and result.get("code",{}).get(path)!=h:
            raise ValueError("actual worker code binding mismatch")
    for field,path in (("config_sha256","configs/search.json"),
                       ("source_manifest_sha256","metadata/sources.json"),
                       ("resources_sha256","data/derived/v3/records.json")):
        if path in method.get("files_sha256",{}) and result.get(field)!=method["files_sha256"][path]:
            raise ValueError("actual worker asset binding mismatch: "+field)
    if method.get("external_models") and Counter(result.get("assets",{}).values())!=Counter(
            x["sha256"] for x in method["external_models"]):
        raise ValueError("actual worker model binding mismatch")
    refs={multiset(r["precursors"]) for r in target["references"]}
    stages={}
    created=False
    for event in result["action_trace"]:
        if "precursor_smiles" not in event:
            continue
        if multiset([event["target"]])!=multiset([target["product_smiles"]]):
            continue
        try:
            match=multiset(event["precursor_smiles"]) in refs
        except ValueError:
            match=False  # Incomplete generated candidates cannot match complete gold.
        stages.setdefault(event["stage"],[]).append(dict(
            matches=match,policy=event.get("policy"),template_id=event.get("template_id"),
            signature=event.get("signature"),node_index=event.get("created_node_index")))
        index=event.get("created_node_index")
        if (match and event["stage"]=="mcts_action_created"
                and type(index) is int and index>=1
                and type(event.get("created_node_count")) is int
                and event["created_node_count"]>0):
            created=True
    base.update(full_reference_created=int(created), stage_matches=stages,
                full_action_trace=result["action_trace"],phase_costs=result.get("phases",[]),
                search_seconds=sum(p.get("search_seconds",0) for p in result.get("phases",[])),
                route_partial=[r.get("partial") for r in result.get("routes",[])],
                surrogate_stock_closure=[r.get("native_solved") for r in result.get("routes",[])],
                evidence_closed=[r.get("evidence_closed") for r in result.get("routes",[])])
    return base


def run_bundle(folder):
    folder=Path(folder).resolve()
    if os.environ.get("FLAVORETRO_TASK016_LEDGER"):
        raise ValueError("historical TASK016 ledger environment must be absent")
    with (folder/"run.lock").open("a") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        gate=check_bundle(folder)
        if not gate["research_run_ready"] or gate["evidence_scope"]!="actual_task_evidence":
            raise ValueError("research admission failed: "+", ".join(gate["blocking_reasons"]))
        if (folder/"attempts.jsonl").exists():
            raise ValueError("matrix already attempted; no retry or implicit restart")
        panel={t["target_id"]:t for t in read(folder/"panel.json")}
        method=read(folder/"method.json")
        schedule=read(folder/"schedule.json")
        previous=os.environ.get("FLAVORETRO_TASK016_TRACE")
        os.environ["FLAVORETRO_TASK016_TRACE"]="1"
        try:
            with (folder/"attempts.jsonl").open("x") as ledger:
                for cell in schedule:
                    if not check_bundle(folder)["research_run_ready"]:
                        raise ValueError("scientific evidence changed during execution")
                    ledger.write(json.dumps(dict(cell,phase="reserved"))+"\n")
                    ledger.flush(); os.fsync(ledger.fileno())
                    target=panel[cell["target_id"]]
                    before=set((folder/"runs").iterdir()) if (folder/"runs").exists() else set()
                    try:
                        result=search(SearchRequest(smiles=target["product_smiles"],
                                      seed=cell["seed"],**PARAMETERS,**ARMS[cell["arm"]]),
                                      run_root=folder/"runs")
                        record=parse_result(folder/"runs"/result["run_id"],target,cell,method)
                    except Exception as exc:
                        after=set((folder/"runs").iterdir()) if (folder/"runs").exists() else set()
                        record=dict(cell,status="error",full_reference_created=None,
                                    error={"code":"execution_or_binding_error","message":str(exc)},
                                    retained_run_folders=sorted(str(p) for p in after-before))
                    key=hashlib.sha256(json.dumps(cell,sort_keys=True).encode()).hexdigest()
                    write_json(folder/"cells"/(key+".json"),record,exclusive=True)
                    ledger.write(json.dumps(dict(cell,phase="finished",cell_file=key+".json"))+"\n")
                    ledger.flush(); os.fsync(ledger.fileno())
        finally:
            if previous is None:
                os.environ.pop("FLAVORETRO_TASK016_TRACE",None)
            else:
                os.environ["FLAVORETRO_TASK016_TRACE"]=previous
        return verify_results(folder)


def summarize(panel, cells, legacy_verified=False):
    index={}
    for cell in cells:
        key=(cell["target_id"],cell["seed"],cell["arm"])
        if key in index:
            raise ValueError("duplicate result cell")
        index[key]=cell
    expected={(t["target_id"],s,a) for t in panel for s in SEEDS for a in ARMS}
    if set(index)-expected:
        raise ValueError("unregistered result cell")
    def hit(t,s,a):
        c=index.get((t,s,a),{})
        return c.get("full_reference_created") if c.get("status")=="ok" else None
    output={}
    for axis in ("C","SS"):
        rows=[t for t in panel if t["axis"]==axis]
        n=len(rows); groups={t["source_group"] for t in rows}
        complete=bool(n) and all(hit(t["target_id"],s,a) in (0,1)
                                for t in rows for s in SEEDS for a in ARMS)
        metrics=dict(registered_targets=n,source_groups=len(groups),
                     complete=complete,comparisons={},N_gap=None,G=None,
                     G_over_N_gap=None,effect_pass=None,missing_cells=0)
        metrics["missing_cells"]=sum(hit(t["target_id"],s,a) not in (0,1)
                                    for t in rows for s in SEEDS for a in ARMS)
        for baseline in ("A","B"):
            differences=[]; target_effects={}; gains=losses=0
            for t in rows:
                values=[]
                for s in SEEDS:
                    x,y=hit(t["target_id"],s,"E"),hit(t["target_id"],s,baseline)
                    if x in (0,1) and y in (0,1):
                        values.append(x-y); differences.append(x-y)
                        gains+=x==1 and y==0; losses+=x==0 and y==1
                if len(values)==3:
                    target_effects[t["target_id"]]=sum(values)/3
            interval=None
            if complete and len(groups)>=5:
                rng=random.Random(20261013); samples=[]
                names=sorted(groups)
                for _ in range(2000):
                    selected=rng.choices(names,k=len(names))
                    values=[target_effects[t["target_id"]] for group in selected
                            for t in rows if t["source_group"]==group]
                    samples.append(sum(values)/len(values))
                import numpy as np
                interval=[float(v) for v in np.percentile(samples,[1.25,98.75])]
            metrics["comparisons"]["E-"+baseline]=dict(
                effect=sum(differences)/(n*3) if complete else None,
                paired_cell_diagnostic=sum(differences)/len(differences) if differences else None,
                valid_pair_cells=len(differences),registered_pair_cells=n*3,
                observed_reference_gain=gains,observed_reference_loss=losses,
                reference_loss=losses if complete else None,
                three_seed_gain_targets=sum(value==1 for value in target_effects.values()),
                three_seed_loss_targets=sum(value==-1 for value in target_effects.values()),
                bootstrap_interval=interval)
        metrics["operational_E_hit_lower_bound"]=(
            sum(hit(t["target_id"],s,"E")==1 for t in rows for s in SEEDS)/(n*3)
            if n else None)
        if complete:
            gaps=[t for t in rows if all(hit(t["target_id"],s,a)==0
                                        for s in SEEDS for a in ("A","B"))]
            gained=[t for t in gaps if all(hit(t["target_id"],s,"E")==1 for s in SEEDS)]
            metrics.update(N_gap=len(gaps),G=len(gained),
                           G_over_N_gap=len(gained)/len(gaps) if gaps else None)
            if legacy_verified:
                metrics["effect_pass"]=bool(n>=6 and len(groups)>=2
                    and len(gained)>=3 and len(gained)/len(gaps)>=0.5
                    and len({t["source_group"] for t in gained})>=2
                    and all(c["effect"]>0 and c["reference_loss"]==0
                            for c in metrics["comparisons"].values()))
        output[axis]=metrics
    return dict(axes=output,registered_cells=len(expected),observed_cells=len(index),
                missing_cells=len(expected-set(index)),
                evaluation_complete=all(x["complete"] for x in output.values()),
                claim_scope="frozen_registered_panel_only",release_ready=False)


def verify_results(folder):
    folder=Path(folder)
    gate=check_bundle(folder)
    if not gate["research_run_ready"]:
        raise ValueError("cannot verify scientific results against invalid bundle")
    panel=read(folder/"panel.json"); method=read(folder/"method.json")
    records=[]
    ledger=[json.loads(line) for line in (folder/"attempts.jsonl").read_text().splitlines()]
    reserved=[(x["target_id"],x["seed"],x["arm"]) for x in ledger if x["phase"]=="reserved"]
    finished=[(x["target_id"],x["seed"],x["arm"]) for x in ledger if x["phase"]=="finished"]
    schedule={(x["target_id"],x["seed"],x["arm"]) for x in read(folder/"schedule.json")}
    if len(reserved)!=len(set(reserved)) or len(finished)!=len(set(finished)) or not set(finished)<=set(reserved)<=schedule:
        raise ValueError("cell ledger conservation failure")
    for entry in (x for x in ledger if x["phase"]=="finished"):
        stored=read(folder/"cells"/entry["cell_file"])
        if stored["status"]=="ok":
            target=next(t for t in panel if t["target_id"]==entry["target_id"])
            rebuilt=parse_result(stored["run_folder"],target,
                                 {k:entry[k] for k in ("target_id","arm","seed")},method)
            if rebuilt!=stored:
                raise ValueError("stored score differs from independently parsed result")
        records.append(stored)
    report=summarize(panel,records,read(folder/"protocol.json")["legacy_protection"]["verified"])
    write_json(folder/"summary.json",report)
    return report

"""Permanent P7 adversarial contracts. Fixtures are engineering evidence only."""
import copy
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import unittest

from scripts.task016_p7_orchestrate import (
    BudgetLedger, ContractError, EpochState, ROOT, STAGES, require_fields, sha_json,
)
from scripts.task016_p7_closure_harness import assert_fresh, assert_zero_leakage, canonical, closure_tokens, closure_groups
from scripts.task016_p7_source_harness import validate_query_accounting, saturated
from scripts.task016_p7_identity_harness import verify_identity
from scripts.task016_p7_structure_harness import reconcile
from scripts.task016_p7_panel_harness import validate_panel
from scripts.task016_p7_experiment_harness import freeze_contract, validate_runner_inputs, recompute_metrics


def advance(epoch,until):
    for stage in STAGES[1:STAGES.index(until)+1]:
        if STAGES.index(stage)<=STAGES.index(epoch.stage):
            continue
        manifest=dict(family=epoch.family,epoch_id=epoch.epoch_id,stage=stage,
                      input_manifest_sha=epoch.manifest_sha,files={"fixture":"a"*64})
        epoch.transition(stage,manifest,expected_previous_sha=epoch.manifest_sha,validate_files=False)
    return epoch


def frozen_epoch(family="C"):
    epoch=advance(EpochState(family),"G4_SCOPE_FREEZE")
    bank=dict(family=family,epoch_id=epoch.epoch_id,scopes=[
        dict(scope_id="p7-test-scope",scope_sha="scope-digest",qualified=True)])
    epoch.freeze_scope(bank,stage_manifest_sha=epoch.manifest_sha)
    advance(epoch,"G5_FRESH_HOLDOUT_ACQUIRE")
    return epoch,bank


def chemical(reaction_id="r1",product="CCOO",source="PMC9000001"):
    return dict(reaction_id=reaction_id,product_smiles=product,acceptor_smiles="CCO",
                donor_smiles="O",reference_precursors=["CCO","O"],site="fixture_site",
                source=source,closure_group="closure:"+source)


def extraction(role="A4"):
    return dict(reaction_id="fixture",acceptor_smiles="CCO",donor_smiles="O",product_smiles="CCOO",
                bond_atoms=dict(acceptor_atom="source:A3",donor_atom="source:D1",
                                product_atoms=["source:A3","source:D1"]),
                site="source:A3",sugar_identity="fixture",anomer_stereo="source_explicit_fixture",
                direction="acceptor+donor->product",step_count=1,evidence_location="fixture paragraph",
                structure_origin="original_machine_readable",
                structure_evidence_pointer=dict(path="fixture.xml",sha256="a"*64),
                reference_precursors=["CCO","O"],agent_role=role,input_manifest_sha="same-input",
                read_other_extractor_output=False,extraction_id=role+":independent")


def query_fixture():
    plan=dict(task="TASK-016-P7",epoch_id="C-E01",preregistered_at="2026-10-07T00:00:00+00:00",
              queries=[dict(query_id="q1",query="fixture query",route="publisher",database="publisher",
                            family="C",scope_id="s1",reason="fixture",max_pages=1,max_objects=3)])
    execution=dict(query_id="q1",status="executed",returned_count=2,deduplicated_count=1,
                   pending_identity_count=1,admitted=0,deferred=1,rejected=0,metadata_only=0,
                   new_closure_groups=0)
    discovery=dict(record_id="d1",query_id="q1",disposition="deferred",source_hint="fixture",
                   metadata_only=False,evidence_eligible=False)
    return plan,[execution],[discovery]


def matrix_fixture(*,exact=False,node=True):
    matrix=[dict(family="C",target_id=f"T{i}",arm=arm,seed=seed)
            for i in range(6) for arm in ("A","B","E") for seed in (0,1,2)]
    contract=dict(task="TASK-016-P7",panels={"C":dict(path="fixture-panel",sha256="a"*64)},
                  scope_bank_sha={"scope.json":"b"*64},runtime_manifest_sha={"runtime.json":"c"*64},
                  code_sha={"code.py":"d"*64},model_hashes={"model.onnx":"e"*64},
                  review_binding={"manifest_sha":"f"*64},stock_keys=[f"stock{i}" for i in range(17)],
                  search_parameters=dict(iterations=20),budget=dict(search_attempts=600),
                  metrics_definition="all-three-seed, complete full donor+acceptor reference",
                  arms={"A":"generic_all_task016_off","B":"frozen_p6_v6","E":"p7_v7"},seeds=[0,1,2],
                  matrix=matrix,qualified_p7_scope_ids=["p7-scope"])
    frozen=freeze_contract(contract)
    refs=[dict(family="C",target_id=f"T{i}",reference_precursors=["CCO","O"],
               closure_group=f"group{i%2}",product_smiles="CCOO") for i in range(6)]
    cells=[]
    for idx,identity in enumerate(matrix):
        trace=[]
        if identity["arm"]=="E":
            metadata=dict(library_template=dict(template_id="p7-scope",template_role="scope_template"),
                          review=dict(task016_p7=dict(exact_seed_instance_match=exact)))
            base=dict(target="CCOO",precursor_smiles=["O","CCO"],signature="CCO.O>>CCOO",template_id="p7-scope",metadata=metadata)
            trace.append(dict(stage="filtered_accepted",**base))
            if node:
                trace.append(dict(stage="mcts_action_created",created_node_count=1,created_node_index=1,
                                  created_child_slot=0,created_outcome_index=0,**base))
        result=dict(status="ok",execution_source="synthetic_engineering_fixture",
                    action_trace=trace,run_id=f"fixture-{idx}")
        cells.append(dict(**identity,raw_result=result,started=True,terminal=True,
                          contract_sha=frozen["contract_sha"],synthetic_fixture=True))
    return frozen,cells,refs


class P7HarnessContracts(unittest.TestCase):
    def test_p7_historical_exposure_cannot_enter_fresh_holdout(self):
        # This fail-closed contract always runs, including an asset-free checkout.
        historical=chemical("historical-fixture",source="PMC9000001")
        exposed=dict(development_exposed=True,exposure_type="historical_development_exposure",
                     eligible_for_fresh_holdout=False,closure_tokens=sorted(closure_tokens(historical)))
        with self.assertRaisesRegex(ContractError,"exposure"):
            assert_fresh(historical,[exposed])
        with self.assertRaisesRegex(ContractError,"exposure"):
            assert_fresh(dict(product_smiles=historical["product_smiles"],source="PMC9000002"),[exposed])
        with self.assertRaisesRegex(ContractError,"exposure"):
            assert_fresh(dict(product_smiles="CCCOO",source="PMC9000001"),[exposed])
        ledger=ROOT/"outputs/task016-p7/v1/exposure_ledger.jsonl"
        if ledger.is_file():
            rows=[json.loads(line) for line in ledger.read_text().splitlines()]
            assert len(rows)==1789
            assert all(row["eligible_for_fresh_holdout"] is False for row in rows)
            assert all("field_completeness" in row and row["origins"] for row in rows)
            historical_graph=next(row["target_graph"] for row in rows if row.get("target_graph"))
            with self.assertRaisesRegex(ContractError,"exposure"):
                assert_fresh(dict(product_smiles=historical_graph),rows)
            old_path=ROOT/"outputs/task016-p6/v1/c_heldout_references.jsonl"
            if old_path.is_file():
                old=json.loads(old_path.read_text().splitlines()[0])
                with self.assertRaisesRegex(ContractError,"exposure"):
                    assert_fresh(old,rows)


    def test_p7_scope_frozen_before_fresh_holdout_extraction(self):
        epoch=EpochState("C")
        with self.assertRaisesRegex(ContractError,"freeze"):
            epoch.record_extraction("new",scope_sha="unfrozen")
        epoch,bank=frozen_epoch()
        assert epoch.record_extraction("new",scope_sha=epoch.scope_sha)["epoch_id"]=="C-E01"


    def test_p7_epoch_mutation_invalidates_prior_holdout(self):
        epoch,bank=frozen_epoch()
        epoch.record_extraction("target1",scope_sha=epoch.scope_sha)
        with self.assertRaises(ContractError):
            epoch.freeze_scope(dict(bank,scopes=[]),stage_manifest_sha=epoch.manifest_sha)
        successor=epoch.invalidate("scientific scope change")
        assert epoch.status=="development_epoch_incomplete"
        assert successor.scope_sha is None and successor.epoch_id=="C-E02"


    def test_p7_doi_only_exposure_blocks_renamed_reaction(self):
        # E01's real DOI-only historical reread had no product or reaction graph.
        doi = "10.1080/09168451.2018.1491286"
        exposure = dict(source_support=[dict(source_id="DOI:" + doi)],
                        development_exposed=True, target_graph=None,
                        reaction_signature=None, closure_tokens=[])
        tokens = closure_tokens(exposure)
        self.assertEqual(tokens, {"doi:" + doi})
        exposure.update(exposure_type="development_exposed",
                        closure_tokens=sorted(tokens))
        for alias in [dict(doi=doi), dict(source_id="DOI:" + doi),
                      dict(source="https://doi.org/" + doi),
                      dict(source_id=doi.upper())]:
            candidate = dict(alias, reaction_id="new-id", product_smiles="CO")
            with self.subTest(alias=alias), self.assertRaisesRegex(ContractError, "intersects holdout"):
                assert_fresh(candidate, [exposure])
        assert_fresh(dict(doi="10.1234/unexposed", reaction_id="new-id",
                          product_smiles="CO"), [exposure])


    def test_p7_source_only_null_reaction_ids_keep_closure_membership(self):
        # Source inspection and unresolved database identities legitimately have
        # explicit null reaction IDs; they must remain permanent source closure.
        rows = [dict(exposure_id="source-one", reaction_id=None,
                     doi="10.1234/source-one"),
                dict(reaction_id="source-one-reaction", doi="10.1234/source-one",
                     product_smiles="CO"),
                dict(exposure_id="source-two", reaction_id=None, target_id=None,
                     doi="10.1234/source-two")]
        groups = closure_groups(rows)
        self.assertEqual(len(groups), 2)
        self.assertEqual(sorted(groups.values()),
                         [["source-one", "source-one-reaction"], ["source-two"]])


    def test_p7_prior_epoch_holdout_becomes_exposed(self):
        epoch,bank=frozen_epoch()
        epoch.record_extraction("target1",scope_sha=epoch.scope_sha)
        successor=epoch.invalidate("insufficient panel")
        advance(successor,"G4_SCOPE_FREEZE")
        next_bank=dict(bank,epoch_id=successor.epoch_id)
        successor.freeze_scope(next_bank,stage_manifest_sha=successor.manifest_sha)
        advance(successor,"G5_FRESH_HOLDOUT_ACQUIRE")
        with self.assertRaisesRegex(ContractError,"historical"):
            successor.record_extraction("target1",scope_sha=successor.scope_sha)


    def test_p7_query_plan_and_execution_counts_conserve(self):
        plan,executions,discoveries=query_fixture()
        assert validate_query_accounting(plan,executions,discoveries)["conserved"]
        with self.assertRaisesRegex(ContractError,"query plan"):
            validate_query_accounting(plan,[],discoveries)
        mutated=copy.deepcopy(executions);mutated[0]["deferred"]=0
        with self.assertRaisesRegex(ContractError,"discovered"):
            validate_query_accounting(plan,mutated,discoveries)


    def test_p7_missing_schema_field_cannot_default_to_zero(self):
        plan,executions,discoveries=query_fixture()
        del executions[0]["admitted"]
        with self.assertRaisesRegex(ContractError,"missing"):
            validate_query_accounting(plan,executions,discoveries)
        with self.assertRaisesRegex(ContractError,"missing"):
            require_fields(dict(canonical_acceptor_signatures=[]),("canonical_acceptor_count",))


    def test_p7_agent_source_hint_is_not_evidence(self):
        with self.assertRaisesRegex(ContractError,"hint"):
            verify_identity(dict(pmcid="PMC123",title="Agent asserts"),[])
        plan,executions,discoveries=query_fixture()
        discoveries[0]["evidence_eligible"]=True
        with self.assertRaisesRegex(ContractError,"hint"):
            validate_query_accounting(plan,executions,discoveries)


    def test_p7_source_metadata_identity_must_match(self):
        claim=dict(pmcid="PMC123",doi="10.1234/fixture",title="Flavonoid transfer",
                   journal="Fixture Journal",year="2026",volume="2",pages="1-9")
        authority=dict(provider="PMC JATS",authoritative=True,metadata=copy.deepcopy(claim),
                       evidence_pointer=dict(path="fixture.xml",sha256="a"*64))
        assert verify_identity(claim,[authority],validate_files=False)["source_identity_verified"]
        period_authority=copy.deepcopy(authority)
        period_authority["metadata"]["title"]+="."
        same=verify_identity(claim,[authority,period_authority],validate_files=False)
        assert same["source_identity_verified"]
        assert same["field_checks"]["title"]["authoritative_values"][1]["value"].endswith(".")
        hyphen_claim=dict(claim,title="Flavonoid β-(1,6) transfer")
        hyphen_authority=copy.deepcopy(authority)
        hyphen_authority["metadata"]["title"]="Flavonoid β‐(1,6) transfer."
        assert verify_identity(hyphen_claim,[hyphen_authority],validate_files=False)["source_identity_verified"]
        hyphen_authority["metadata"]["journal"]="Fixture‐Journal"
        assert not verify_identity(hyphen_claim,[hyphen_authority],validate_files=False)["source_identity_verified"]
        false_claim=dict(claim,title="Dental virtual reality")
        result=verify_identity(false_claim,[authority],validate_files=False)
        assert not result["evidence_eligible"] and result["conflict_fields"]==["title"]


    def test_p7_dual_structure_extractors_must_reconcile(self):
        a,b=extraction("A4"),extraction("A5")
        assert reconcile(a,b,validate_files=False)["structure_complete"]
        b["product_smiles"]="CCOC"
        result=reconcile(a,b,validate_files=False)
        assert result["status"]=="reconciliation_required" and not result["structure_complete"]
        b["read_other_extractor_output"]=True
        with self.assertRaisesRegex(ContractError,"each other"):
            reconcile(a,b,validate_files=False)


    def test_p7_handwritten_complex_structure_rejected(self):
        a,b=extraction("A4"),extraction("A5")
        a["structure_origin"]="handwritten_from_name_or_memory"
        with self.assertRaisesRegex(ContractError,"handwritten"):
            reconcile(a,b,validate_files=False)


    def test_p7_build_and_holdout_have_zero_reaction_leakage(self):
        build=chemical(source="PMC9000001")
        hold=chemical(source="PMC9000002")
        with self.assertRaisesRegex(ContractError,"leakage"):
            assert_zero_leakage([build],[hold])


    def test_p7_build_and_holdout_have_zero_source_closure_leakage(self):
        build=chemical("build","CCOO","PMC9000001")
        hold=chemical("fresh","CCCOO","PMC9000001")
        with self.assertRaisesRegex(ContractError,"article"):
            assert_zero_leakage([build],[hold])


    def test_p7_holdout_not_in_runtime_instances(self):
        hold=chemical("fresh","CCCOO","PMC9000002")
        instance=dict(target="CCCOO",template_role="development_build")
        with self.assertRaisesRegex(ContractError,"exact runtime"):
            assert_zero_leakage([], [hold],runtime_instances=[instance])


    def test_p7_scope_bank_replays_all_build_supports(self):
        from scripts.task016_p7_scope_harness import validate_scope_bank
        bank=[dict(template_id="s1",scope_sha256="a"*64,exact_sha256="b"*64,
                   template_role="scope_template",support_instances=["b1","b2"],
                   scope=dict(family="C",site="fixture"),scope_transformation=dict(function="exact_to_scope"))]
        supports=[dict(instance_id="b1",acceptor="CCO"),
                  dict(instance_id="b2",acceptor="CCCO")]
        replay=[dict(template_id="s1",instance_id="b1",passed=True),dict(template_id="s1",instance_id="b2",passed=True)]
        boundaries=[dict(template_id="s1",control_id=f"c{i}",preregistered=True,violated=False) for i in range(6)]
        assert validate_scope_bank(bank,supports,replay,boundaries)
        with self.assertRaises(ContractError):
            validate_scope_bank(bank,supports,replay[:1],boundaries)


    def test_p7_scope_has_minimum_boundary_controls(self):
        from scripts.task016_p7_scope_harness import validate_scope_bank
        bank=[dict(template_id="s1",scope_sha256="a"*64,exact_sha256="b"*64,
                   template_role="scope_template",support_instances=["b1","b2"],
                   scope=dict(family="C",site="fixture"),scope_transformation=dict(function="exact_to_scope"))]
        supports=[dict(instance_id="b1",acceptor="CCO"),
                  dict(instance_id="b2",acceptor="CCCO")]
        replay=[dict(template_id="s1",instance_id="b1",passed=True),dict(template_id="s1",instance_id="b2",passed=True)]
        boundaries=[dict(template_id="s1",control_id=f"c{i}",preregistered=True,violated=False) for i in range(5)]
        with self.assertRaises(ContractError):
            validate_scope_bank(bank,supports,replay,boundaries)


    def test_p7_scope_applicability_required_for_panel(self):
        epoch,bank=frozen_epoch()
        row=dict(chemical(),target_id="fresh",family="C",epoch_id=epoch.epoch_id,
                 extracted_at=(datetime.now(timezone.utc)+timedelta(seconds=1)).isoformat(),
                 extraction_scope_sha=epoch.scope_sha,leakage=False,exact_seed_instance_match=False,
                 runtime_complete=True,source_identity_verified=True,structure_complete=True,
                 reference_precursor_complete=True,scope_applicability=False,scope_applicability_records=[])
        with self.assertRaisesRegex(ContractError,"applicability"):
            validate_panel([row],epoch,bank,enforce_floor=False)


    def test_p7_invalid_product_cannot_be_hidden_by_complete_flags(self):
        epoch,bank=frozen_epoch()
        row=dict(chemical(product="invalid name"),target_id="fresh",family="C",epoch_id=epoch.epoch_id,
                 extracted_at=(datetime.now(timezone.utc)+timedelta(seconds=1)).isoformat(),
                 extraction_scope_sha=epoch.scope_sha,leakage=False,exact_seed_instance_match=False,
                 runtime_complete=True,source_identity_verified=True,structure_complete=True,
                 reference_precursor_complete=True,scope_applicability=True,scope_applicability_records=[])
        with self.assertRaisesRegex(ContractError,"invalid molecular"):
            validate_panel([row],epoch,bank,enforce_floor=False)

    def test_p7_raw_result_file_required_for_scientific_metrics(self):
        frozen,cells,refs=matrix_fixture()
        for cell in cells:
            cell["synthetic_fixture"]=False
            cell["raw_result"]["execution_source"]="live_aizynthfinder_mcts"
        with self.assertRaisesRegex(ContractError,"missing"):
            recompute_metrics(frozen,cells,refs)

    def test_p7_c_and_ss_epochs_are_independent(self):
        c=advance(EpochState("C"),"G3_SCOPE_BUILD")
        ss=EpochState("SS")
        assert c.stage=="G3_SCOPE_BUILD" and ss.stage=="G0_BASELINE"
        with self.assertRaisesRegex(ContractError,"different epoch"):
            ss.transition("G1_EXPOSURE_LEDGER",dict(family="C",epoch_id="C-E01",stage="G1_EXPOSURE_LEDGER",
                          input_manifest_sha=None,files={"f":"a"*64}),expected_previous_sha=None)


    def test_p7_family_failure_does_not_block_other_family(self):
        c,bank=frozen_epoch()
        ss,ssbank=frozen_epoch("SS")
        c.invalidate("no fresh groups")
        assert ss.record_extraction("ss_new",scope_sha=ss.scope_sha)["epoch_id"]=="SS-E01"
        assert ss.status=="active"


    def test_p7_runner_cannot_modify_frozen_contract(self):
        frozen,cells,refs=matrix_fixture()
        consumed=copy.deepcopy(frozen["contract"])
        consumed["search_parameters"]["iterations"]=21
        with self.assertRaisesRegex(ContractError,"cannot modify"):
            validate_runner_inputs(frozen,consumed,check_files=False)


    def test_p7_exact_replay_not_counted_as_transfer(self):
        frozen,cells,refs=matrix_fixture(exact=True)
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["N_gap"]==6 and result["G"]==0 and result["node_transfer_targets"]==0


    def test_p7_node_transfer_requires_real_tree_trace(self):
        frozen,cells,refs=matrix_fixture(node=False)
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["G"]==6 and result["node_transfer_targets"]==0
        frozen,cells,refs=matrix_fixture(node=True)
        for cell in cells:
            for row in cell["raw_result"]["action_trace"]:
                if row["stage"]=="mcts_action_created":
                    del row["created_node_index"]
        with self.assertRaisesRegex(ContractError,"missing"):
            recompute_metrics(frozen,cells,refs,allow_fixture=True)


    def test_p7_metrics_recomputed_from_raw_cells(self):
        frozen,cells,refs=matrix_fixture()
        for row in cells:
            row["runner_summary"]=dict(reference_retained=False,node_transfer=False,G=999)
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)
        assert result["metrics_by_family"]["C"]["G"]==6
        assert result["metrics_by_family"]["C"]["node_transfer_targets"]==6
        assert result["overall_completion_passed"] is False  # fixtures never scientific evidence


    def test_p7_generic_top3_protection(self):
        frozen,cells,refs=matrix_fixture()
        base=dict(target="CCOO",precursor_smiles=["CCO","O"],template_id="generic",policy="generic",
                  metadata={"policy_name":"generic"})
        trace=cells[0]["raw_result"]["action_trace"]
        for sig in ("accepted-1","accepted-2","accepted-3"):
            trace.append(dict(base,stage="generated",signature=sig))
        for sig in ("accepted-1","accepted-2","accepted-3"):
            trace.append(dict(base,stage="generic_protection_checked",signature=sig,rejected=False))
        for sig in ("accepted-1","accepted-2"):
            trace.append(dict(base,stage="after_truncation",signature=sig))
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["generic_top3_protection_violations"]==1
        check=result["target_checks"][0]["arms"]["A"][0]["generic_top3_protection_checks"][0]
        assert check["missing_protected_signatures"]==["accepted-3"]

    def test_p7_generic_top3_filter_rejections_are_not_displacement(self):
        frozen,cells,refs=matrix_fixture()
        base=dict(target="CCOO",precursor_smiles=["CCO","O"],template_id="generic",policy="generic",
                  metadata={"policy_name":"generic"})
        trace=cells[0]["raw_result"]["action_trace"]
        trace.append(dict(base,stage="generated",signature="rejected"))
        trace.append(dict(base,stage="generic_protection_checked",signature="rejected",rejected=True))
        for sig in ("accepted-1","accepted-1","accepted-2","accepted-3"):
            trace.append(dict(base,stage="generic_protection_checked",signature=sig,rejected=False))
        for sig in ("accepted-1","accepted-2","accepted-3"):
            trace.append(dict(base,stage="after_truncation",signature=sig))
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["generic_top3_protection_violations"]==0
        check=result["target_checks"][0]["arms"]["A"][0]["generic_top3_protection_checks"][0]
        assert len(check["protected_accepted_distinct_signatures"])==3 and check["rejected_probes"]==1

    def test_p7_generic_top3_other_expansion_cannot_hide_displacement(self):
        frozen,cells,refs=matrix_fixture()
        base=dict(target="CCOO",precursor_smiles=["CCO","O"],template_id="generic",policy="generic",
                  metadata={"policy_name":"generic"})
        trace=cells[0]["raw_result"]["action_trace"]
        trace.extend([dict(base,stage="generated",signature="protected"),
                      dict(base,stage="generic_protection_checked",signature="protected",rejected=False),
                      dict(base,stage="after_truncation",signature="other"),
                      dict(base,stage="generated",signature="protected"),
                      dict(base,stage="generic_protection_checked",signature="protected",rejected=False),
                      dict(base,stage="after_truncation",signature="protected")])
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["generic_top3_protection_violations"]==1
        checks=result["target_checks"][0]["arms"]["A"][0]["generic_top3_protection_checks"]
        assert [r["violations"] for r in checks]==[1,0]


    def test_p7_generic_top3_other_target_or_library_action_cannot_hide_displacement(self):
        frozen,cells,refs=matrix_fixture()
        base=dict(target="CCOO",precursor_smiles=["CCO","O"],template_id="generic",policy="generic",
                  metadata={"policy_name":"generic"})
        trace=cells[0]["raw_result"]["action_trace"]
        trace.extend([dict(base,stage="generated",signature="protected"),
                      dict(base,stage="generic_protection_checked",signature="protected",rejected=False),
                      dict(base,stage="after_truncation",signature="other"),
                      dict(base,stage="after_truncation",signature="protected",target="CCCOO"),
                      dict(base,stage="after_truncation",signature="protected",policy="glycoside",
                           metadata={"policy_name":"glycoside","library_template":{"template_id":"scope"}})])
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["generic_top3_protection_violations"]==1

    def test_p7_budget_hard_cap_includes_failed_attempts(self):
        budget=BudgetLedger()
        budget.reserve("C_first_matrix",81,"matrix")
        with self.assertRaisesRegex(ContractError,"budget"):
            budget.reserve("C_first_matrix",1,"failed-too")
        budget.reserve("HTTP",8000,"http")
        with self.assertRaisesRegex(ContractError,"budget"):
            budget.reserve("HTTP",1,"extra-http")


    def test_p7_stage_manifest_sha_mismatch_fails_closed(self):
        epoch=EpochState("C")
        manifest=dict(family="C",epoch_id="C-E01",stage="G1_EXPOSURE_LEDGER",
                      input_manifest_sha="changed",files={"f":"a"*64})
        with self.assertRaisesRegex(ContractError,"chain"):
            epoch.transition("G1_EXPOSURE_LEDGER",manifest,expected_previous_sha=None)


    def test_p7_no_gain_denominator_is_null(self):
        frozen,cells,refs=matrix_fixture()
        for row in cells:
            if row["arm"] in ("A","B"):
                row["raw_result"]["action_trace"]=[dict(stage="filtered_accepted",
                    target="CCOO",precursor_smiles=["CCO","O"],signature="CCO.O>>CCOO",template_id="generic",metadata={})]
        result=recompute_metrics(frozen,cells,refs,allow_fixture=True)["metrics_by_family"]["C"]
        assert result["N_gap"]==0 and result["G_over_N_gap"] is None


    def test_p7_saturation_requires_three_routes_two_complete_rounds(self):
        base=dict(family="C",complete=True,new_qualified_closure_groups=0)
        assert not saturated([dict(base,round_id=1,routes=["pmc"])])
        assert not saturated([dict(base,round_id=1,routes=["pmc"]),
                              dict(base,round_id=2,routes=["pmc","crossref"])])
        assert saturated([dict(base,round_id=1,routes=["pmc","crossref"]),
                          dict(base,round_id=2,routes=["publisher"])])


    def test_independent_verify_preserves_charged_target(self):
        from scripts.task016_p7_verify import created_actions, reaction_signature
        entry=dict(stage="mcts_action_created",phase=0,created_node_count=1,
                   created_node_index=1,precursor_smiles=["CO"],target="C[O-]",
                   signature=reaction_signature(["CO"],"C[O-]"))
        raw=dict(phases=[dict(index=0,node_count=2,
                             engine_class="flavoretro.search.SearchTree")],
                 action_trace=[entry])
        self.assertEqual(created_actions(raw)[0]["signature"],"CO>>C[O-]")
        neutralized=copy.deepcopy(raw)
        neutralized["action_trace"][0]["signature"]="CO>>CO"
        with self.assertRaises(ContractError):
            created_actions(neutralized)

    def test_independent_verify_rejects_phantom_created_child(self):
        from scripts.task016_p7_verify import created_actions
        raw=dict(phases=[dict(index=0,node_count=2,
                             engine_class="flavoretro.search.SearchTree")],
                 action_trace=[dict(stage="mcts_action_created",phase=0,
                                    created_node_count=1,created_node_index=2,
                                    precursor_smiles=["CO"],target="CO",
                                    signature="CO>>CO")])
        with self.assertRaises(ContractError):
            created_actions(raw)

    def test_independent_verify_requires_physical_raw_file(self):
        from scripts.task016_p7_verify import PhysicalAudit
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            audit=PhysicalAudit(directory)
            with self.assertRaises(ContractError):
                audit.bind("a_claimed_result.json","a"*64)

if __name__ == "__main__":
    unittest.main()

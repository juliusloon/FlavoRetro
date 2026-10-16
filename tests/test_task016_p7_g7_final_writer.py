"""P7 real G7 writer integration: pre-write hard rejection and v4 call-path tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import task016_p7_g7_final_writer as w
from scripts.task016_p7_orchestrate import ContractError
from scripts.operate import ROOT

def pointer(p):
    return {"path":str(p),"sha256":"a"*64}

def nominal():
    d={k:pointer("fixtures/"+k+".json") for k in w.POINTER_FIELDS}
    d.update(schema_version=1,task=w.TASK,family="SS",epoch_id="SS-E02",
      no_model_outcome_read=True,no_scope_or_panel_change_after_results=True)
    d["g4_stage"]=pointer(w.BASE/"SS/E02/stages/G4_SCOPE_FREEZE.json")
    d["g6_stage"]=pointer(w.BASE/"SS/E02/stages/batches/SS-E02-R12-original-science-review/G6_IDENTITY_STRUCTURE_ADMIT.json")
    d["scope_manifest"]=pointer(w.BASE/"SS/E02/scope_manifest.json")
    d["requirement"]=pointer(w.REQ)
    d["historical_exposure"]=pointer(w.SOURCE_LEDGER)
    d["prior_exposure"]=pointer(w.PRIOR_LEDGER)
    return d

class G7FinalWriterRejects(unittest.TestCase):
    def test_no_bypass_omitted_or_extra_field(self):
        for alteration in ("missing","extra","set_disable"):
            d=nominal()
            if alteration=="missing":d.pop("prior_exposure")
            elif alteration=="extra":d["enforce_floor"]=False
            else:d["no_model_outcome_read"]=False
            with self.subTest(alteration=alteration),self.assertRaises(ContractError):
                w.validate_contract(d)

    def test_scope_and_previous_epoch_cannot_be_swapped(self):
        for key,new in [("family","O"),("epoch_id","SS-E03"),
              ("g4_stage",pointer("outputs/other_scope.json")),
              ("g6_stage",pointer("outputs/task016-p7/v1/SS/E02/stages/G6_IDENTITY_STRUCTURE_ADMIT.json"))]:
            d=nominal();d[key]=new
            with self.subTest(key=key),self.assertRaises(ContractError):
                w.validate_contract(d)

    def test_historical_and_named_review_universe_cannot_be_substituted(self):
        for key in ("requirement","historical_exposure","prior_exposure"):
            d=nominal();d[key]=pointer("outputs/task016-p7/v1/fake.jsonl")
            with self.subTest(key=key),self.assertRaises(ContractError):
                w.validate_contract(d)

    def test_missing_sha_bindings_rejected_before_outputs(self):
        d=nominal();d["records"]["sha256"]="short"
        with self.assertRaises(ContractError):w.validate_contract(d)
        self.assertFalse((ROOT/w.BASE/"SS/E02/stages/G7_CLOSURE_PANEL_FREEZE.json").exists())

    def test_freeze_never_writes_after_failed_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"case.json").write_text(json.dumps(nominal()))
            with patch.object(w,"ROOT",root),patch.object(w,"validate_contract",side_effect=ContractError("rejected")),patch.object(w,"write") as writer:
                with self.assertRaisesRegex(ContractError,"rejected"):
                    w.freeze("case.json")
                writer.assert_not_called()
            self.assertEqual(sorted(x.name for x in root.iterdir()),["case.json"])

    def test_v4_validator_is_the_actual_panel_entry(self):
        d=nominal()
        req={"validator_path":"scripts/task016_p7_named_exposure_gate_v4.py",
             "validator_sha256":"e8e15f349dd4b522d9536d9b82dfd2ea5c9c5d8f812e798142e48a859158fa4c",
             "call":"validate_final_panel","production_floor_cannot_be_disabled":True,
             "permanent_name_record_count":28,"registry_files_sha256":{"f":"z"},
             "implementation_files_sha256":{}}
        sm={"family":"SS","epoch_id":"SS-E02","scope_bank_sha256":"banksha"}
        state={"status":"active","family":"SS","epoch_id":"SS-E02","scope_sha":"scopehash"}
        scope={"family":"SS","epoch_id":"SS-E02","scopes":[]}
        panel=[{"target_id":str(i)} for i in range(6)]
        stage=lambda s:{"stage":s,"family":"SS","epoch_id":"SS-E02"}
        record={"epoch_id":"SS-E02","stage":"G6_IDENTITY_STRUCTURE_ADMIT","status":"active",
           "stage_manifest_path":d["g6_stage"]["path"],
           "stage_manifest_sha256":d["g6_stage"]["sha256"]}
        def obj(ptr,root,t):
            key=ptr["path"]
            if key==d["requirement"]["path"]:return req
            if key==d["scope_manifest"]["path"]:return sm
            if key==d["epoch_state"]["path"]:return state
            if key==d["scope_bank"]["path"]:return scope
            if key==d["records"]["path"]:return panel
            if key==d["build"]["path"]:return [{"a":1}]
            if key==d["exposures"]["path"]:return [{"b":2}]
            if key==d["runtime_instances"]["path"]:return []
            if key==d["historical_exposure"]["path"]:return [{"history":"complete"}]
            if key==d["prior_exposure"]["path"]:return [{"prior":"complete"}]
            raise AssertionError(key)
        def file_hash(path):
            return req["validator_sha256"] if str(path).endswith("gate_v4.py") else "banksha"
        with patch.object(w,"bound_file",return_value=Path("unused")),patch.object(w,"_data",side_effect=obj),patch.object(w,"sha_file",side_effect=file_hash),patch.object(w,"sha_json",return_value="scopehash"),patch.object(w,"verify_stage_chain",side_effect=[stage("G4_SCOPE_FREEZE"),stage("G6_IDENTITY_STRUCTURE_ADMIT")]),patch.object(w,"rows",return_value=[record]),patch.object(w,"verify_current_exposure_receipt",return_value=1) as receipt_check,patch.object(w,"assert_alias_zero_leakage",return_value={"reaction_leakage":0,"source_assay_closure_leakage":0,"exact_runtime_instance_leakage":0,"scope_design_leakage":0}) as alias_check,patch.object(w.named_gate,"validate_final_panel",return_value={"N":6,"closure_groups":2,"completion_floor_passed":True,"named_exposure_documentary_checks":[{}]*6}) as validator:
            result=w.validate_contract(d)
        self.assertEqual(result["N"],6)
        args,kwargs=validator.call_args
        self.assertEqual(kwargs["enforce_floor"],True)
        self.assertEqual(kwargs["registry_files_sha256"],{"f":"z"})
        self.assertEqual(args[3],[{"history":"complete"},{"prior":"complete"},{"b":2}])
        self.assertEqual(args[0],panel)
        alias_check.assert_called_once()
        receipt_check.assert_called_once()

    def test_current_exposure_receipt_cannot_omit_registered_g5_g6(self):
        d=nominal()
        receipt={"task":w.TASK,"family":"SS","epoch_id":"SS-E02",
                 "epoch_ledger_sha256":"ledgerhash",
                 "effective_exposure_sha256":d["exposures"]["sha256"],
                 "closure_complete":True,"source_alias_unresolved":0,
                 "disposition_pending":0,"registered_stage_sha256":{}}
        stages=[{"epoch_id":"SS-E02","status":"active","stage":"G5_FRESH_HOLDOUT_ACQUIRE",
                  "stage_manifest_path":"stages/G5_FRESH_HOLDOUT_ACQUIRE.json",
                  "stage_manifest_sha256":"X"},
                {"epoch_id":"SS-E02","status":"active","stage":"G6_IDENTITY_STRUCTURE_ADMIT",
                  "stage_manifest_path":"stages/G6_IDENTITY_STRUCTURE_ADMIT.json",
                  "stage_manifest_sha256":"Y"}]
        with patch.object(w,"_data",return_value=receipt),patch.object(w,"sha_file",return_value="ledgerhash"):
            with self.assertRaisesRegex(ContractError,"skips G5/G6"):
                w.verify_current_exposure_receipt(d,root=ROOT,ledger=stages)

    def test_cannot_freeze_when_panel_empty_even_with_mocked_named_gate(self):
        d=nominal()
        req={"validator_path":"scripts/task016_p7_named_exposure_gate_v4.py",
            "validator_sha256":"X","call":"validate_final_panel",
            "production_floor_cannot_be_disabled":True,"permanent_name_record_count":28,
            "registry_files_sha256":{"a":"b"},"implementation_files_sha256":{}}
        def data(ptr,root,kind):
            key=ptr["path"]
            if key==d["requirement"]["path"]:return req
            if key==d["scope_manifest"]["path"]:return {"family":"SS","epoch_id":"SS-E02","scope_bank_sha256":"X"}
            if key==d["epoch_state"]["path"]:return {"status":"active","family":"SS","epoch_id":"SS-E02","scope_sha":"S"}
            if key==d["scope_bank"]["path"]:return {"scope":"dummy"}
            if key==d["records"]["path"]:return []
            raise AssertionError("unexpected data load "+key)
        stage=lambda s:{"stage":s,"family":"SS","epoch_id":"SS-E02"}
        record={"epoch_id":"SS-E02","stage":"G6_IDENTITY_STRUCTURE_ADMIT","status":"active",
            "stage_manifest_path":d["g6_stage"]["path"],"stage_manifest_sha256":d["g6_stage"]["sha256"]}
        with patch.object(w,"bound_file",return_value=Path("unused")),patch.object(w,"_data",side_effect=data),patch.object(w,"sha_file",return_value="X"),patch.object(w,"sha_json",return_value="S"),patch.object(w,"verify_stage_chain",side_effect=[stage("G4_SCOPE_FREEZE"),stage("G6_IDENTITY_STRUCTURE_ADMIT")]),patch.object(w,"rows",return_value=[record]),patch.object(w.named_gate,"validate_final_panel") as validator:
            with self.assertRaisesRegex(ContractError,"6-9"):w.validate_contract(d)
            validator.assert_not_called()

if __name__=="__main__":unittest.main()


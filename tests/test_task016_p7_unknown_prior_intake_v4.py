"""Unknown source history can be investigated but cannot silently pass admission."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from scripts import task016_p7_full_qualification_harness_v4 as fq
from scripts.task016_p7_orchestrate import ContractError

class UnknownPriorAdmission(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.pre=self.file("pre.json", {"prior_scientific_read":None,"known_matches":0})
        self.src={"source_id":"source-one","official_aliases":["article:PMC123456","doi:10.1234/example"],"prior_scientific_read":None,"prior_read_status":"unknown","prior_uncertainty_blocks_qualification":True,"prior_read_precheck_evidence":[self.pre]}
        self.spec={"epoch_id":"C-E02","prior_exposure_snapshot":self.file("prior.json",{}),"prior_current_evaluation_ledger":self.file("current.jsonl",{}),"late_prior_design_files":[self.file("late.jsonl",{})]}
        self.evidence=self.file("complete-audit.json", {"coverage":"fixture_only"})
        self.clear={"task":fq.TASK,"agent_role":"A6","epoch_id":"C-E02","source_id":"source-one","approval_type":"agent_delegated","human_reviewed":False,"timestamp":fq.now(),"prior_scientific_read":False,"coverage_complete":True,"source_first_scientific_read_after_G4":True,"historical_design_overlap":False,"unresolved":[],"read_model_outcome":False,"official_aliases":self.src["official_aliases"],"prior_exposure_snapshot":self.spec["prior_exposure_snapshot"],"prior_current_evaluation_ledger":self.spec["prior_current_evaluation_ledger"],"late_prior_design_files":self.spec["late_prior_design_files"],"evidence":[self.evidence]}
        ptrs=[self.spec["prior_exposure_snapshot"],self.spec["prior_current_evaluation_ledger"],*self.spec["late_prior_design_files"],self.pre,self.evidence]
        self.role={"input_manifest_sha":{p["path"]:p["sha256"] for p in ptrs}}
    def file(self,name,obj):
        p=self.root/name;p.write_text(json.dumps(obj)+"\n")
        return {"path":name,"sha256":fq.digest(p)}
    def validate_clearance(self,obj,role=None):
        ptr=self.file("clearance.json",obj)
        return fq._prior_clearance(self.spec,self.src,{"prior_source_clearance":ptr},role or self.role,{ptr["path"]:ptr["sha256"]},self.root)
    def test_unknown_intake_remains_unknown(self):
        before=copy.deepcopy(self.src)
        fq._prior_intake(self.src,self.root)
        self.assertEqual(self.src,before)
        self.assertIsNone(self.src["prior_scientific_read"])
    def test_known_prior_or_untyped_read_flag_rejected(self):
        for state in [True,0,1,"false","unknown"]:
            with self.subTest(state=state),self.assertRaises(ContractError):
                fq._prior_intake({**self.src,"prior_scientific_read":state},self.root)
    def test_unknown_cannot_drop_uncertainty_or_precheck_binding(self):
        for field in ["prior_scientific_read","prior_read_status","prior_uncertainty_blocks_qualification","prior_read_precheck_evidence"]:
            src=copy.deepcopy(self.src);src.pop(field)
            with self.subTest(field=field),self.assertRaises(ContractError):fq._prior_intake(src,self.root)
        (self.root/"pre.json").write_text("changed")
        with self.assertRaises(ContractError):fq._prior_intake(self.src,self.root)
    def test_unknown_intake_cannot_qualify_without_prior_clearance(self):
        with self.assertRaisesRegex(ContractError,"lacks independent"):
            fq._prior_clearance(self.spec,self.src,{},self.role,{},self.root)
    def test_zero_known_matches_does_not_clear_unknown(self):
        for field,value in [("prior_scientific_read",None),("coverage_complete",False),("unresolved",["legacy_read_unknown"]),("source_first_scientific_read_after_G4",False),("historical_design_overlap",True)]:
            obj={**self.clear,field:value}
            with self.subTest(field=field),self.assertRaises(ContractError):self.validate_clearance(obj)
    def test_clearance_must_cover_current_ledger_and_alias_union(self):
        obj={**self.clear,"official_aliases":["doi:10.1234/example"]}
        with self.assertRaises(ContractError):self.validate_clearance(obj)
        obj=copy.deepcopy(self.clear);obj.pop("prior_current_evaluation_ledger")
        with self.assertRaises(ContractError):self.validate_clearance(obj)
        role=copy.deepcopy(self.role);role["input_manifest_sha"].pop(self.spec["prior_current_evaluation_ledger"]["path"])
        with self.assertRaises(ContractError):self.validate_clearance(self.clear,role)
    def test_full_independent_fixture_clearance_is_required_without_mutating_intake(self):
        self.validate_clearance(self.clear)
        self.assertIsNone(self.src["prior_scientific_read"])
        ptr=self.file("clearance.json",self.clear)
        with self.assertRaises(ContractError):fq._prior_clearance(self.spec,self.src,{"prior_source_clearance":ptr},self.role,{},self.root)

if __name__=="__main__":unittest.main()

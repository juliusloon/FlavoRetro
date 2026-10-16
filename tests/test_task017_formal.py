"""Synthetic TASK017 contracts only; no labels, sources or MCTS are real."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from flavoretro import formal_evaluation as f
from flavoretro.contracts import SearchRequest

def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n")

class ResearchGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ws=Path(self.temp.name);self.out=self.ws/"bundle";self.out.mkdir()
        self.proof=self.ws/"proof.json"
        dump(self.proof,{"fixture_only":True,"text":"synthetic independent review evidence"})
        self.ev=dict(file="proof.json",sha256=f.sha(self.proof),locator="synthetic")
        for name in ("flavoretro/search.py","flavoretro/worker.py","flavoretro/service.py",
                     "flavoretro/contracts.py","flavoretro/formal_evaluation.py",
                     "scripts/task017_formal.py","tests/test_task017_formal.py",
                     "configs/search.json","metadata/active.json"):
            p=self.ws/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text("{}")
        for v in ("v3","v6"):
            folder=self.ws/v
            dump(folder/"payload.json",{})
            dump(folder/"manifest.json",{"files_sha256":{"payload.json":f.sha(folder/"payload.json")}})
            dump(self.ws/("configs/glycoside-library-"+v+".json"),
                 {"manifest":v+"/manifest.json","manifest_sha256":f.sha(folder/"manifest.json")})
        dump(self.ws/"metadata/release.json",{"status":"research_candidate",
              "primary_source_review":"unresolved","current_vendor_evidence":"unresolved",
              "production_template_count":0,"production_stock_count":0})
        (self.out/"approved_task.md").write_text("Synthetic TASK017 v0.2\n")
        files=[p for p in self.ws.rglob("*") if p.is_file() and p!=self.proof and self.out not in p.parents]
        method=dict(parameters=f.PARAMETERS,arms=f.ARMS,seeds=list(f.SEEDS),
                    schedule_seed=20261013,candidate_stock_keys=17,
                    frozen_before_new_metadata=True,files_sha256={
                        str(p.relative_to(self.ws)):f.sha(p) for p in files},
                    review_manifest_sha256="review-fixture",
                    domains=[{"manifest_sha256":"v3-fixture"},{"manifest_sha256":"v6-fixture"}])
        dump(self.out/"method.json",method)
        approval=dict(task="TASK-017",version="v0.2",authority="agent_delegated",
                      human_reviewed=False,owner_instruction="synthetic authorization",
                      contract_sha256=f.sha(self.out/"approved_task.md"),
                      budgets=dict(local_commands=120,queries=12,http_attempts=120,all_run_attempts=345),
                      permitted_label_reviewers=[dict(id="fixture-owner",agent=False,authority_evidence=self.ev)],
                      synthetic_fixture=True)
        dump(self.out/"approval.json",approval)
        plan=dict(contract_sha256=approval["contract_sha256"],
                  method_sha256=f.sha(self.out/"method.json"),
                  queries=[dict(id=str(i),axis="C" if i<6 else "SS",metadata_only=True,limit=8)
                           for i in range(12)],query_rounds=1,
                  roles=dict(engineering_executor="Cano"),
                  handoff=dict(prohibit_test_to_method=True,prohibit_model_output_to_reviewer=True),
                  stopped_content_policy=dict(reopen_epochs=False,read_Liu2021_R73_R80=False),
                  allowed_operations=["synthetic_engineering_validation"])
        dump(self.out/"preparation_plan.json",plan)
        dump(self.out/"budget_current.json",dict(local_commands=1,queries=0,http_attempts=0,
             download_bytes=0,all_run_attempts=0,science_attempts=0,engineering_attempts=0))
        self.panel=[]
        for i in range(12):
            row=dict(target_id=str(i),axis="C" if i<6 else "SS",
                     product_smiles="C"*(i+3),source_node="s"+str(i%2),
                     source_group="s"+str(i%2),
                     references=[dict(precursors=["C","O"],acceptor="C",donor="O",
                                     primary_evidence=[dict(self.ev,source_node="s"+str(i%2),reaction_key=f.reaction_key("C"*(i+3),["C","O"]))])],
                     strata={key:"synthetic" for key in ("core","site","sugar","donor","catalysis","source")})
            self.panel.append(row)
        dump(self.out/"panel.json",self.panel)
        labels=[dict(target_id=r["target_id"],reviewer_id="fixture-owner",
              domain_confirmed=True,stereochemistry_confirmed=True,primary_reference_confirmed=True,
              exposure_role="evaluation_labeling",product_smiles=r["product_smiles"],
              references=[x["precursors"] for x in r["references"]],
              approval_evidence=self.ev,origin="owner_verified") for r in self.panel]
        dump(self.out/"labels.json",labels)
        reviewproof=self.ws/"label_review.json"
        dump(reviewproof,dict(reviewer_id="fixture-owner",reviewed_at="synthetic",
                             decisions=copy.deepcopy(labels)))
        label_ev=dict(file="label_review.json",sha256=f.sha(reviewproof),locator="decisions")
        for label in labels:label["approval_evidence"]=label_ev
        dump(self.out/"labels.json",labels)
        inventory=self.ws/"inventory.json"
        dump(inventory,dict(source_nodes=["dev"],products=["C"*30],reaction_keys=[]))
        inventory_ev=dict(file="inventory.json",sha256=f.sha(inventory),locator="source_nodes")
        closure=dict(nodes=[dict(id=x,aliases=[x]) for x in ("s0","s1","dev")],edges=[],
             development_inventory_evidence=[inventory_ev],development_coverage_reviewed=True,
             development_nodes=["dev"],development_products=["C"*30],development_reaction_keys=[],
             development_exposed_targets=[],unresolved_independence_targets=[])
        dump(self.out/"closure.json",closure)
        legacyproof=self.ws/"legacyproof.json"
        dump(legacyproof,dict(method_sha256=f.sha(self.out/"method.json"),
             code_sha256={p:h for p,h in method["files_sha256"].items()
                          if p.startswith("flavoretro/") and p.endswith(".py")},
             source_evidence=[self.ev]))
        legacy_ev=dict(file="legacyproof.json",sha256=f.sha(legacyproof),locator="source_evidence")
        protocol=dict(parameters=f.PARAMETERS,arms=f.ARMS,seeds=list(f.SEEDS),
             schedule_seed=20261013,primary="E-A",secondary="E-B",denominator="all_registered_targets",
             bootstrap_replicates=2000,bootstrap_seed=20261013,interval_percent=97.5,
             panel_sha256=f.sha(self.out/"panel.json"),method_sha256=f.sha(self.out/"method.json"),
             legacy_protection=dict(verified=True,evidence=legacy_ev))
        dump(self.out/"protocol.json",protocol)
        dump(self.out/"protocol_review.json",dict(protocol_sha256=f.sha(self.out/"protocol.json"),
             contract_sha256=approval["contract_sha256"],reviewer_id="fixture-owner",status="approved",
             reviewed_at="synthetic",scope="frozen_panel_labels_method_execution",approval_evidence=self.ev))
        protocolproof=self.ws/"protocolproof.json"
        dump(protocolproof,dict(reviewer_id="fixture-owner",status="approved",
             protocol_sha256=f.sha(self.out/"protocol.json"),panel_sha256=f.sha(self.out/"panel.json"),
             labels_sha256=f.sha(self.out/"labels.json"),reviewed_at="synthetic",
             scope="frozen_panel_labels_method_execution"))
        proof_ev=dict(file="protocolproof.json",sha256=f.sha(protocolproof),locator="protocol_sha256")
        review=f.read(self.out/"protocol_review.json");review["approval_evidence"]=proof_ev
        dump(self.out/"protocol_review.json",review)
        dump(self.out/"schedule.json",f.make_schedule(self.panel))
        testproof=self.ws/"testproof.json"
        dump(testproof,dict(failures=[],errors=[],tests_run=34,
                           requirements={key:True for key in f.REQUIRED_TESTS}))
        test_ev=dict(file="testproof.json",sha256=f.sha(testproof),locator="requirements")
        dump(self.out/"implementation_validation.json",dict(test_evidence=test_ev,failures=[],
             synthetic_only=True,requirements={key:True for key in f.REQUIRED_TESTS},
             code_sha256={p:f.sha(self.ws/p) for p in ("flavoretro/formal_evaluation.py",
                        "scripts/task017_formal.py","tests/test_task017_formal.py")}))
        self.seal()

    def seal(self):
        dump(self.out/"frozen_inputs.json",dict(contract_sha256=f.sha(self.out/"approved_task.md"),
             files_sha256={p:f.sha(self.out/p) for p in (*f.DOCUMENTS,"budget_current.json")}))

    def change(self,name,change,reseal=True):
        value=f.read(self.out/name);change(value);dump(self.out/name,value)
        if reseal:self.seal()

    def gate(self):
        return f.check_bundle(self.out,workspace=self.ws,synthetic=True)

    def test_vendor_nonblocking(self):
        result=self.gate()
        self.assertTrue(result["preparation_ready"],result)
        self.assertTrue(result["research_run_ready"],result)
        self.assertEqual(result["nonblocking_status"]["current_vendor_evidence"],"unresolved")
        self.assertFalse(result["release_ready"])
        self.assertEqual(result["evidence_scope"],"synthetic_logic_only")

    def test_preparation_without_gold(self):
        for name in ("panel.json","labels.json","protocol.json","protocol_review.json","frozen_inputs.json"):
            (self.out/name).unlink()
        result=self.gate()
        self.assertTrue(result["preparation_ready"],result)
        self.assertFalse(result["research_run_ready"])

    def test_missing_labels(self):
        (self.out/"labels.json").unlink()
        self.assertFalse(self.gate()["research_run_ready"])

    def test_missing_protocol(self):
        (self.out/"protocol_review.json").unlink()
        self.assertFalse(self.gate()["research_run_ready"])

    def test_closure_leakage(self):
        self.change("closure.json",lambda x:x["development_nodes"].append("s0"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_exact_product_leakage(self):
        self.change("closure.json",lambda x:x["development_products"].append(self.panel[0]["product_smiles"]))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_unknown_independence(self):
        self.change("closure.json",lambda x:x["unresolved_independence_targets"].append("0"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_transitive_alias_leakage(self):
        self.change("closure.json",lambda x:x["nodes"][0]["aliases"].append("dev"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_hash_drift(self):
        (self.ws/"flavoretro/search.py").write_text("changed")
        result=self.gate()
        self.assertFalse(result["preparation_ready"])
        self.assertFalse(result["research_run_ready"])

    def test_test_feedback(self):
        self.change("labels.json",lambda x:x[0].update(method_feedback=True))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_missing_evidence_file(self):
        self.proof.unlink()
        self.assertFalse(self.gate()["research_run_ready"])

    def test_agent_gold_rejected(self):
        self.change("labels.json",lambda x:x[0].update(agent_generated_gold=True))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_unauthorized_reviewer(self):
        self.change("labels.json",lambda x:x[0].update(reviewer_id="Cano"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_denominator_change(self):
        self.change("schedule.json",lambda x:x.pop())
        self.assertFalse(self.gate()["research_run_ready"])

    def test_inventory_omission_rejected(self):
        self.change("closure.json",lambda x:x.update(development_products=[]))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_primary_source_node_mismatch(self):
        self.change("panel.json",lambda x:x[0]["references"][0]["primary_evidence"][0].update(source_node="s1"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_label_approval_content_mismatch(self):
        self.change("labels.json",lambda x:x[0].update(product_smiles="CCO"))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_input_hash_drift(self):
        self.change("panel.json",lambda x:x.pop(),reseal=False)
        self.assertFalse(self.gate()["research_run_ready"])

    def test_minimum_groups(self):
        self.change("closure.json",lambda x:x["edges"].append(dict(left="s0",right="s1",basis="assay",evidence=self.ev)))
        self.assertFalse(self.gate()["research_run_ready"])

    def test_budget_not_reset(self):
        self.change("budget_current.json",lambda x:x.update(local_commands=121))
        self.assertFalse(self.gate()["preparation_ready"])

    def test_actual_gate_rejects_fixture(self):
        self.assertFalse(f.check_bundle(self.out,workspace=self.ws)["research_run_ready"])

    def test_one_attempt(self):
        (self.out/"attempts.jsonl").write_text("already reserved")
        with patch.object(f,"check_bundle",return_value=dict(research_run_ready=True,evidence_scope="actual_task_evidence")),patch.object(f,"search") as run:
            with self.assertRaisesRegex(ValueError,"already attempted"):
                f.run_bundle(self.out)
            run.assert_not_called()

    def test_run_gate_blocks_before_search(self):
        with patch.object(f,"search") as run:
            with self.assertRaisesRegex(ValueError,"admission failed"):
                f.run_bundle(self.out)
            run.assert_not_called()

    def test_schedule_is_stable_and_complete(self):
        first=f.make_schedule(self.panel)
        self.assertEqual(first,f.make_schedule(list(reversed(self.panel))))
        self.assertEqual(len(first),108)
        self.assertEqual(len({tuple(sorted(x.items())) for x in first}),108)

class ResultTests(unittest.TestCase):
    def panel(self,groups=2):
        return [dict(target_id=str(i),axis="C" if i<6 else "SS",
                     source_group=str(i%groups),product_smiles="CCC",
                     references=[dict(precursors=["CCO","O"])]) for i in range(12)]

    def cells(self,panel):
        return [dict(target_id=t["target_id"],seed=s,arm=a,status="ok",
                     full_reference_created=int(a=="E"))
                for t in panel for s in f.SEEDS for a in f.ARMS]

    def test_fixed_denominator(self):
        panel=self.panel();cells=self.cells(panel)
        cells[-1].update(status="error",full_reference_created=None)
        result=f.summarize(panel,cells,legacy_verified=True)
        self.assertEqual(result["axes"]["SS"]["registered_targets"],6)
        self.assertIsNone(result["axes"]["SS"]["comparisons"]["E-A"]["effect"])
        self.assertIsNone(result["axes"]["SS"]["comparisons"]["E-A"]["reference_loss"])
        self.assertFalse(result["evaluation_complete"])

    def test_zero_gap_ratio_null(self):
        panel=self.panel();cells=self.cells(panel)
        for cell in cells:cell["full_reference_created"]=1
        result=f.summarize(panel,cells,legacy_verified=True)
        self.assertEqual(result["axes"]["C"]["N_gap"],0)
        self.assertIsNone(result["axes"]["C"]["G_over_N_gap"])
        self.assertFalse(result["axes"]["C"]["effect_pass"])
        self.assertTrue(result["evaluation_complete"])

    def test_empty_panel_is_not_zero_performance(self):
        result=f.summarize([],[])
        self.assertFalse(result["evaluation_complete"])
        self.assertIsNone(result["axes"]["C"]["comparisons"]["E-A"]["effect"])

    def test_positive_effect_and_low_group_uncertainty(self):
        panel=self.panel();result=f.summarize(panel,self.cells(panel),legacy_verified=True)
        self.assertEqual(result["axes"]["C"]["G"],6)
        self.assertTrue(result["axes"]["C"]["effect_pass"])
        self.assertIsNone(result["axes"]["C"]["comparisons"]["E-A"]["bootstrap_interval"])

    def test_cluster_bootstrap(self):
        panel=self.panel(groups=6)
        result=f.summarize(panel,self.cells(panel),legacy_verified=True)
        self.assertEqual(result["axes"]["C"]["comparisons"]["E-A"]["bootstrap_interval"],[1.0,1.0])

    def test_duplicate_and_unregistered_cells_rejected(self):
        panel=self.panel();cells=self.cells(panel)
        with self.assertRaises(ValueError):f.summarize(panel,cells+[cells[0]])
        with self.assertRaises(ValueError):f.summarize(panel,[dict(cells[0],target_id="unknown")])

    def test_component_multiplicity(self):
        self.assertNotEqual(f.multiset(["CCO","O"]),f.multiset(["CCO","O","O"]))
        self.assertEqual(f.multiset(["O.CCO","O"]),f.multiset(["CCO","O","O"]))
        self.assertNotEqual(f.multiset(["[13CH4]"]),f.multiset(["C"]))
        self.assertNotEqual(f.multiset(["F[C@H](Cl)Br"]),f.multiset(["F[C@@H](Cl)Br"]))

    def test_undefined_stereochemistry_rejected(self):
        with self.assertRaises(ValueError):f.multiset(["CC(O)Cl"])

    def result_files(self,folder,stage="mcts_action_created",precursors=None,node_count=1):
        target=self.panel()[0];cell=dict(target_id="0",arm="A",seed=0)
        method=dict(parameters=f.PARAMETERS,arms=f.ARMS,review_manifest_sha256="r")
        request=SearchRequest(smiles=target["product_smiles"],seed=0,**f.PARAMETERS,**f.ARMS["A"]).payload()
        result=dict(run_id="fixture-live-shape",status="ok",execution_source="live_aizynthfinder_mcts",
                    request=request,review_binding=dict(manifest_sha256="r"),
                    action_trace=[dict(stage=stage,target=target["product_smiles"],
                                      precursor_smiles=precursors or ["CCO","O"],
                                      created_node_index=1,created_node_count=node_count)],
                    phases=[],routes=[])
        dump(folder/"request.json",request);dump(folder/"result.json",result)
        (folder/"worker.log").write_text("synthetic result schema only")
        dump(folder/"manifest.json",dict(run_id=result["run_id"],status="ok",
             files={p.name:f.sha(p) for p in folder.iterdir() if p.is_file() and p.name!="manifest.json"}))
        return target,cell,method

    def test_real_result_binding(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);target,cell,method=self.result_files(folder)
            self.assertEqual(f.parse_result(folder,target,cell,method)["full_reference_created"],1)
            (folder/"worker.log").write_text("changed")
            with self.assertRaises(ValueError):f.parse_result(folder,target,cell,method)

    def test_candidate_and_zero_nodes_are_not_created(self):
        for stage,count in [("generated_generic",1),("mcts_action_created",0)]:
            with tempfile.TemporaryDirectory() as td:
                folder=Path(td);target,cell,method=self.result_files(folder,stage=stage,node_count=count)
                self.assertEqual(f.parse_result(folder,target,cell,method)["full_reference_created"],0)

    def test_extra_reference_component_does_not_match(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);target,cell,method=self.result_files(folder,precursors=["CCO","O","O"])
            self.assertEqual(f.parse_result(folder,target,cell,method)["full_reference_created"],0)

    def test_error_result_is_null(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td);target,cell,method=self.result_files(folder)
            r=f.read(folder/"result.json");r["status"]="error";r["error"]={"code":"timeout"}
            dump(folder/"result.json",r)
            m=f.read(folder/"manifest.json");m["status"]="error";m["files"]["result.json"]=f.sha(folder/"result.json")
            dump(folder/"manifest.json",m)
            self.assertIsNone(f.parse_result(folder,target,cell,method)["full_reference_created"])

    def test_legacy_compatibility(self):
        from flavoretro.evaluation import preflight
        with patch("flavoretro.evaluation.active_data",side_effect=ValueError("synthetic missing asset")):
            result=preflight()
        self.assertIn("formal_run_ready",result)
        self.assertFalse(result["release_ready"])
        self.assertNotIn("research_run_ready",result)

if __name__=="__main__":
    unittest.main()

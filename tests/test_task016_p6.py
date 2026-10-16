"""P6 regression tests; all synthetic records are engineering fixtures only."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from rdkit import Chem
from rdkit.Chem import rdChemReactions
from flavoretro.contracts import SearchRequest
from flavoretro.workspace import config, AssetError, root
from flavoretro.reviewed_resources import canonical_side, reaction_signature
from flavoretro.glycoside_scope import (apply_c_scope, runtime_complete, panel_preflight,
    independently_runnable, source_identity_eligible, transfer_trace_eligible)
from scripts import task016_p6_c_scope as builder
from scripts.task016_p6_c_probe import probe_frozen
from scripts.task016_p6_common import sha

ASSETS = (root()/"outputs/task016-p6/v1/template_source_manifest.json").is_file()
ACC = ["O=c1c(O)c(-c2ccccc2)oc2ccccc12", "O=c1c(O)c(-c2ccc(O)cc2)oc2cc(O)cc(O)c12",
       "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12", "O=c1c(O)c(-c2cc(O)c(O)c(O)c2)oc2cc(O)cc(O)c12",
       "O=c1c(O)c(-c2ccc(OC)cc2)oc2cc(O)cc(O)c12", "O=c1c(O)c(-c2ccc(O)c(OC)c2)oc2cc(O)cc(O)c12"]

def fixture_support(acceptor):
    return dict(acceptor=acceptor,donor=builder.UDP_GLC,target=builder.source_product(acceptor))

def fixture_template():
    seed=fixture_support(ACC[1]);exact,scoped,_=builder.construct_scope(seed)
    return dict(template_role="scope_template",scope_template=scoped,smarts=scoped,donor=canonical_side([builder.UDP_GLC]),
                required_context=dict(mode="enzymatic",donor_name="UDP-glucose")),exact

def fixture_records():
    out=[]
    for i,acc in enumerate(ACC):
        s=fixture_support(acc); refs=[acc,builder.UDP_GLC]
        out.append(dict(reaction_id=f"FIXTURE-{i}",product_smiles=s["target"],reference_precursors=refs,
            canonical_reaction_signature=reaction_signature([canonical_side(refs)],[canonical_side([s["target"]])]),
            closure_group="fixture-group-"+str(i%2),source_binding=dict(metadata_verified=True,fixture_only=True),
            structure_origin="original_source_explicit_graph_and_stereochemistry",structure_complete=True,
            inferred=False,deferred=False,fixture_only=True))
    return out

def fixture_cells():
    cells=[]
    for arm in ("A","B","E"):
        for seed in (0,1,2):
            cells.append(dict(arm=arm,seed=seed,status="ok",exact_seed_instance_match=False,
                 reference_node_created=arm=="E",reference_signature="fixture-reference",
                 node_trace=[dict(stage="mcts_action_created",signature="fixture-reference",created_node_count=1,created_node_index=1)] if arm=="E" else [],fixture_only=True))
    return cells

class P6PureContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template,cls.exact=fixture_template();cls.records=fixture_records()

    def test_exact_template_and_scope_are_distinct_artifacts(self):
        self.assertNotEqual(self.exact["smarts"],self.template["scope_template"])
        ex=rdChemReactions.ReactionFromSmarts(self.exact["smarts"])
        sc=rdChemReactions.ReactionFromSmarts(self.template["scope_template"])
        self.assertGreater(ex.GetReactantTemplate(0).GetNumAtoms(),sc.GetReactantTemplate(0).GetNumAtoms())

    def test_scope_pipeline_calls_scoped_smarts(self):
        with patch.object(builder,"scoped_smarts",wraps=builder.scoped_smarts) as transform:
            builder.construct_scope(fixture_support(ACC[1]))
        transform.assert_called_once()

    def test_scope_fires_all_declared_build_supports(self):
        for acc in ACC[1:3]:
            s=fixture_support(acc)
            expected=canonical_side([acc,builder.UDP_GLC])
            self.assertIn(expected,[o["precursors"] for o in apply_c_scope(self.template,s["target"])])

    def test_second_build_support_is_scope_canary(self):
        second=fixture_support(ACC[2]);rxn=rdChemReactions.ReactionFromSmarts(self.exact["smarts"])
        rxn.GetSubstructParams().useChirality=True
        self.assertEqual(rxn.RunReactants((Chem.MolFromSmiles(second["target"]),)),())
        self.assertTrue(apply_c_scope(self.template,second["target"]))

    def test_scope_negative_controls_do_not_fire(self):
        mol=Chem.MolFromSmiles(fixture_support(ACC[1])["target"])
        site=next(iter(builder.c8_sites(mol)));ano=next(n for n in mol.GetAtomWithIdx(site).GetNeighbors() if not n.GetIsAromatic())
        ano.InvertChirality()
        self.assertFalse(apply_c_scope(self.template,Chem.MolToSmiles(mol,True)))
        self.assertFalse(apply_c_scope(self.template,ACC[1]))
        self.assertFalse(apply_c_scope(self.template,fixture_support(ACC[1])["target"],dict(mode="chemical")))

    def test_scope_hash_frozen_before_holdout_probe(self):
        with tempfile.TemporaryDirectory() as d:
            s=Path(d)/"scope.json";p=Path(d)/"panel.jsonl"
            s.write_text(json.dumps(self.template));p.write_text(json.dumps(self.records[0])+"\n")
            old=sha(s);s.write_text(json.dumps(dict(self.template,donor="CCO")))
            with self.assertRaises(ValueError):probe_frozen(s,p,old,sha(p))

    def test_holdout_probe_cannot_mutate_scope(self):
        with tempfile.TemporaryDirectory() as d:
            s=Path(d)/"scope.json";p=Path(d)/"panel.jsonl"
            s.write_text(json.dumps(self.template));p.write_text(json.dumps(self.records[0])+"\n")
            before=(sha(s),sha(p));probe_frozen(s,p,*before)
            self.assertEqual((sha(s),sha(p)),before)

    def test_holdout_target_requires_runtime_complete_structure(self):
        r=copy.deepcopy(self.records[0]);self.assertTrue(runtime_complete(r))
        for field,value in (("product_smiles",None),("reference_precursors",[]),("canonical_reaction_signature","wrong")):
            self.assertFalse(runtime_complete(dict(r,**{field:value})))
        self.assertFalse(runtime_complete(dict(r,source_binding=dict(metadata_verified=False))))

    def test_deferred_target_not_in_runtime_panel(self):
        rows=copy.deepcopy(self.records);rows[0]["deferred"]=True
        result=panel_preflight(rows,[],[])
        self.assertEqual(result["targets"],5);self.assertFalse(result["passed"])

    def test_build_holdout_zero_reaction_leakage(self):
        result=panel_preflight(self.records,[self.records[0]["canonical_reaction_signature"]],[])
        self.assertFalse(result["passed"]);self.assertEqual(len(result["reaction_leakage"]),1)

    def test_build_holdout_zero_closure_leakage(self):
        result=panel_preflight(self.records,[],[self.records[0]["closure_group"]])
        self.assertFalse(result["passed"]);self.assertEqual(len(result["closure_leakage"]),1)

    def test_c_and_ss_preflights_are_independent(self):
        self.assertEqual(independently_runnable(dict(C=dict(passed=False),SS=dict(passed=True))),["SS"])

    def test_ss_failure_does_not_block_qualified_c_runs(self):
        self.assertEqual(independently_runnable(dict(C=dict(passed=True),SS=dict(passed=False))),["C"])

    def test_exact_seed_replay_not_counted_as_transfer(self):
        cells=fixture_cells();self.assertTrue(transfer_trace_eligible(cells))
        cells[-1]["exact_seed_instance_match"]=True;self.assertFalse(transfer_trace_eligible(cells))

    def test_node_transfer_requires_real_node_trace(self):
        cells=fixture_cells();cells[-1]["node_trace"][0]["stage"]="filtered_domain"
        self.assertFalse(transfer_trace_eligible(cells))
        cells=fixture_cells();cells[-1]["node_trace"][0]["created_node_count"]=0
        self.assertFalse(transfer_trace_eligible(cells))
        self.assertFalse(transfer_trace_eligible(fixture_cells()[:-1]))

    def test_source_identity_requires_metadata_match(self):
        fields=dict(pmcid="PMC-fixture",title="Fixture",doi="10.fixture/x",journal="Fixture journal")
        self.assertTrue(source_identity_eligible(fields,dict(fields,publication_metadata_verified=True)))
        self.assertFalse(source_identity_eligible(fields,dict(fields,title="Different",publication_metadata_verified=True)))

    def test_unverified_agent_citation_not_evidence_eligible(self):
        fields=dict(pmcid="PMC-fixture",title="Fixture",doi="10.fixture/x",journal="Fixture journal")
        self.assertFalse(source_identity_eligible(fields,fields))

    def test_inferred_handwritten_structure_not_structure_complete(self):
        self.assertFalse(runtime_complete(dict(self.records[0],inferred=True)))
        self.assertFalse(runtime_complete(dict(self.records[0],structure_origin="handwritten_from_name")))

    def test_v6_default_off(self):
        self.assertFalse(config("glycoside-library-v6.json")["default_enabled"])
        self.assertNotIn("glycoside_library_version",SearchRequest(smiles="CCO").payload())
        with self.assertRaises(ValueError):SearchRequest(smiles="CCO",glycoside_library_version="v6")

    def test_v6_manifest_drift_fails_closed(self):
        from flavoretro.glycoside_library_v6 import Registry
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"manifest.json";p.write_text("{}")
            with self.assertRaises(AssetError):Registry(p,"wrong")

    def test_missing_sugar_anomer_is_incomplete(self):
        r=copy.deepcopy(self.records[0]);mol=Chem.MolFromSmiles(r["product_smiles"])
        site=next(iter(builder.c8_sites(mol)));ano=next(n for n in mol.GetAtomWithIdx(site).GetNeighbors() if not n.GetIsAromatic())
        ano.SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED);r["product_smiles"]=Chem.MolToSmiles(mol,True)
        self.assertFalse(runtime_complete(r))

    def test_duplicate_reactions_and_panel_cap_are_rejected(self):
        self.assertFalse(panel_preflight(self.records+[self.records[0]],[],[])["passed"])
        self.assertFalse(panel_preflight(self.records*2,[],[])["passed"])

    def test_phosphate_source_representation_is_preserved(self):
        self.assertTrue(runtime_complete(self.records[0]))
        donor=Chem.MolFromSmiles(builder.UDP_GLC)
        self.assertTrue(any(donor.GetAtomWithIdx(i).GetAtomicNum()==15 and c=="?" for i,c in Chem.FindMolChiralCenters(donor,includeUnassigned=True)))

class P6AssetContractTests(unittest.TestCase):
    @unittest.skipUnless(ASSETS,"P6 local immutable source payload required")
    def test_v6_runtime_replays_all_build_supports(self):
        from flavoretro.glycoside_library_v6 import load_registry,apply_template
        registry=load_registry()
        self.assertEqual(len(registry.increment_instances),4)
        for inst in registry.increment_instances.values():
            self.assertIn(canonical_side(inst["reference_precursors"]),[o["precursors"] for t in registry.increment_templates
                          if inst["instance_id"] in t["support_instances"] for o in apply_template(t,inst["target"])])

    @unittest.skipUnless(ASSETS,"P6 local immutable source payload required")
    def test_v3_v4_v5_legacy_loading_unchanged(self):
        from flavoretro import glycoside_library_v3 as v3,glycoside_library_v4 as v4,glycoside_library_v5 as v5
        self.assertEqual([len(m.load_registry().templates) for m in (v3,v4,v5)],[54,57,55])

    @unittest.skipUnless(ASSETS,"P6 local immutable source payload required")
    def test_holdout_not_in_v6_runtime(self):
        from flavoretro.glycoside_library_v6 import load_registry
        registry=load_registry();hold=[]
        for n in ("c_heldout_references.jsonl","ss_heldout_references.jsonl"):
            hold += [json.loads(s)["canonical_reaction_signature"] for s in (root()/"outputs/task016-p6/v1"/n).read_text().splitlines()]
        self.assertFalse(set(hold)&{r["reference_signature"] for r in registry.instances.values()})

if __name__=="__main__":unittest.main()

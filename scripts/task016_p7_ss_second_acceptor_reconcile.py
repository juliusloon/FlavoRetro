"""A6 final bounded reconciliation of SS second-acceptor source drawings and claim gaps."""
import json,hashlib
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
B=ROOT/"outputs/task016-p7/v1/SS/E02_design";O=B/"second_acceptor_A6_final_reconciliation_v1"
inputs={}
def bind(p,h=None):
 p=Path(p);p=p if p.is_absolute() else ROOT/p
 if h is not None:assert sha_file(p)==h,str(p)
 inputs[str(p.relative_to(ROOT))]=sha_file(p);return p
def js(p):return json.loads(bind(p).read_text())
def role(p):
 d=js(p);assert d["human_reviewed"] is False and d["approval_type"]=="agent_delegated"
 if "outputs" in d:
  for x in d["outputs"]:bind(x["path"],x["sha256"])
 else:
  for p,h in d["output_files_sha256"].items():bind(p,h)
 return d
def mol(s):
 m=Chem.MolFromSmiles(s);assert m is not None;return m
def compare(a,b):
 x,y=mol(a),mol(b);assert Chem.MolToSmiles(x,isomericSmiles=True)==Chem.MolToSmiles(y,isomericSmiles=True)
 assert Chem.MolToInchi(x)==Chem.MolToInchi(y)
 assert Chem.MolToInchi(x,options="/FixedH")==Chem.MolToInchi(y,options="/FixedH")
 return dict(canonical_graph_equal=True,standard_InChI_equal=True,FixedH_InChI_equal=True,formula=rdMolDescriptors.CalcMolFormula(x),full_InChIKey=Chem.MolToInchiKey(x),assigned_carbon_centers=sum(1 for a in Chem.FindMolChiralCenters(x,includeUnassigned=True) if x.GetAtomWithIdx(a[0]).GetSymbol()=="C" and a[1]!="?"))
def main():
 bind(Path(__file__))
 common=js(B/"second_acceptor_database_v1/common_raw_only_second_acceptor_input.v2.json")
 for p,h in common["raw_input_files_sha256"].items():bind(p,h)
 roles=[role(B/"second_acceptor_A4_v1/A4_role_manifest.json"),role(B/"second_acceptor_A4_donor_supplement_v1/A4_role_manifest.json"),role(B/"second_acceptor_A4_PMC106_donor_v2/A4_role_manifest.json"),role(B/"second_acceptor_A5_v1/A5_role_manifest_v2.json")]
 assert roles[-1]["source_qualification_granted"] is False and roles[-1]["unprocessed_raw_or_focus"]==0
 a4=js(B/"second_acceptor_A4_v1/A4_independent_source_graph_candidates.json")
 a5={x["graph_id"]:x for x in js(B/"second_acceptor_A5_v1/A5_independent_graph_transcriptions.json")["graphs"]}
 graphs=[]
 for x in a4:
  label="L7Glc" if x["candidate_id"].endswith(":L7Glc") else "Ch7Glc"
  gid="PMC106_"+label+("_acceptor" if x["object_role"]=="acceptor" else "_pathway_product")
  graphs.append(dict(candidate_id=x["candidate_id"],object_role=x["object_role"],A5_graph_id=gid,comparison=compare(x["canonical_isomeric_smiles"],a5[gid]["isomeric_SMILES"])))
 assert len(graphs)==4
 donors=[]
 for source,a,b in [
  ("PMC10602602",B/"second_acceptor_A4_PMC106_donor_v2/A4_PMC106_UDPApi_neutral_representation_candidate.json",B/"second_acceptor_A5_v1/A5_PMC106_donor_source_transcription_v2.json"),
  ("PMC13140228",B/"second_acceptor_A4_donor_supplement_v1/A4_PMC131_S6_UDPApi_neutral_drawing_candidate.json",B/"second_acceptor_A5_v1/A5_PMC131_donor_source_transcription.json")]:
  x,y=js(a),js(b);c=compare(x["canonical_isomeric_smiles"],y["isomeric_SMILES"]);assert c["assigned_carbon_centers"]==7
  assert x["actual_salt_unknown"] is True and y["experimental_reagent_full_species_resolved"] is False
  donors.append(dict(source_id=source,A4_pointer=pointer(a),A5_pointer=pointer(b),comparison=c,actual_salt_counterions_hydration=None,neutral_representation_not_physical_species=True,cross_source_substitution_used=False))
 disp4=js(B/"second_acceptor_A4_v1/A4_three_focus_dispositions.json")
 disp5=js(B/"second_acceptor_A5_v1/A5_focus_dispositions_v2.json")["records"]
 assert {x["candidate_id"] for x in disp4}=={x["candidate_id"] for x in disp5} and len(disp5)==3
 originals=js(B/"second_acceptor_A4_PMC106_donor_v2/A4_second_acceptor_claim_source_clarity.json")
 decisions=[]
 for x in disp5:
  cid=x["candidate_id"];is106=cid.startswith("PMC106")
  assert x["product"]["specific_assay_product_identity_confirmed"] is False
  decisions.append(dict(candidate_id=cid,status="deferred",A4_and_A5_positive_reactivity_retained=True,complete_source_pathway_graph=is106,complete_observed_assay_product_identity=False,complete_source_specific_donor_covalent_representation=True,actual_donor_physical_species_unknown=True,
   author_general_Glc2_site_claim_retained=is106,source_specific_assay_product_linkage_chain_unresolved=True,
   reason="S1 pathway product drawings and general Glc2 conclusion are explicit, but Figure4B activity does not link this exact acceptor to a product peak/label/structure; no substitution of pathway graph for measured product identity" if is106 else "2a positive enzyme-dependent HPLC and source HRMS retained; complete2a product graph/site/anomer absent, no cross-source assignment",
   measured_product_mz=None if is106 else x["product"]["source_measured_mass"]["value"],measured_mass_is_missing=is106,
   source_supported_reference_added=False,future_fresh_eligible=False,human_reviewed=False,no_new_universal_NMR_or_standard_gate=True))
 db=js(B/"second_acceptor_graph_identity_v1/four_official_graph_identity_comparisons.json")
 assert len(db["comparisons"])==4 and db["all_four_full_graphs_equal"] is True
 old=js(B/"A6_source_qualification_v1/A6_source_qualification_summary.v2.json")
 assert old["source_build_supported_contexts"]==2 and old["distinct_eligible_canonical_acceptors"]==1
 immutable_json(O/"four_source_graphs_final_dual_comparison.json",graphs)
 immutable_json(O/"two_source_specific_donor_final_dual_comparison.json",donors)
 immutable_json(O/"three_focus_source_qualification_dispositions.json",decisions)
 summary=dict(task=TASK,approval_type="agent_delegated",at=now(),human_reviewed=False,independent_chemical_validation=False,completed_extractor_roles=2,raw_inputs_verified=17,complete_acceptor_and_pathway_product_graph_matches=4,source_specific_donor_representation_matches=2,graph_disagreements=0,official_database_full_graph_matches=4,focus_processed=3,new_source_qualified_reactions=0,new_deferred_focus=3,current_source_build_supported_contexts=2,current_distinct_eligible_acceptors=1,SS_scope_floor_passed=False,no_SS_E02_G2_G3_G4_advanced=True,new_HTTP=0,new_MCTS=0,scientific_ABE_cells=0,metrics=None,actual_salt_or_assay_identity_unknown_preserved=True,new_universal_NMR_standard_gate=False,entire_assay_universe_denominator_resolution="pending",complete_source_saturation=False,overall_completed=False,upstream_source_claim_clarity_pointer=pointer(B/"second_acceptor_A4_PMC106_donor_v2/A4_second_acceptor_claim_source_clarity.json"))
 immutable_json(O/"A6_final_reconciliation_summary.json",summary)
 immutable_json(O/"role_A6_final_reconciliation_manifest.json",dict(task=TASK,approval_type="agent_delegated",human_reviewed=False,role="A6 root-authorized comparison and source claim reconciliation after fixed A4/A5",blind_reextraction=False,input_files_sha256=inputs,output_files_sha256={str(p.relative_to(ROOT)):sha_file(p) for p in O.glob("*.json")},new_source_qualification=0,originals_or_frozen_assets_modified=False))
 print(json.dumps({k:summary[k] for k in ["graph_disagreements","new_source_qualified_reactions","new_deferred_focus","current_distinct_eligible_acceptors","SS_scope_floor_passed"]}))
if __name__=="__main__":main()

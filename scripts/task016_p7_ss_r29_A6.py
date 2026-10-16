"""SS R29 A6: independent reconciliation of TWO direct primary enzyme O2 sources.

Soybean Fg3 and Arabidopsis UGT79B6; archived source-level direct enzymatic
groups, NEVER fresh from historical exposure and not complete stereograph admission.
"""
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,freeze_stage_manifest
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G6_IDENTITY_STRUCTURE_ADMIT.json"
A4=R/"A4/first_independent_original_O2_evidence.json"
A5=R/"A5/second_independent_catalytic_site_screen.json"
A3=R/"A3_original_front_verified.json"
EPOCH=B/"epoch_ledger.jsonl";SCOPE=B/"SS/E02/scope_manifest.json"
PREV=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1/A6/source_O2_scope_positive_reconciliation.json"
def sha(p):return sha_file(ROOT/p)
def j(p):return json.loads((ROOT/p).read_text())
def txt(p):return " ".join("".join(p.itertext()).split())
def save(p,v):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE")
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G6).exists():raise RuntimeError("IMMUTABLE_G6")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 a4=j(A4);a5=j(A5);a3=j(A3)
 assert a4["source_count"]==a5["original_count"]==a3["front_identity_verified"]==2
 d4={r["PMCID"]:r for r in a4["sources"]}
 d5={r["PMCID"]:r for r in a5["results"]}
 d3={r["PMCID"]:r for r in a3["sources"]}
 assert set(d4)==set(d5)==set(d3)=={"PMC4494776","PMC4282749"}
 spec={
 "PMC4494776":dict(anchor="body/p-30",confirm_anchor="body/p-42",
  expected=["GmF3G2","kaempferol 3-O-glucoside","sophoroside","UDP-glucose"],
  representative="GmF3G2\u2033Gt (UGT79B30) recombinant; UDP-glucose donor + kaempferol 3-O-glucoside -> kaempferol 3-O-sophoroside; accepts also kaempferol/quercetin 3-O-glucoside/galactoside in assays",
  source_group="Soybean_GmF3G2doubleprimeGt_Fg3_2015",
  parent_domain=["3O_betaD_Glcp","3O_betaD_Galp"],
  product="kaempferol 3-O-sophoroside (Glc beta1->2 Glc) and other compatible Glc/Galp cases",
  DOI="10.1186/s12870-015-0504-7"),
 "PMC4282749":dict(anchor="body/p-20",confirm_anchor="body/p-28",
  expected=["UGT79B6","kaempferol 3-O-glucoside","1→2","enzymatic assays"],
  representative="UGT79B6 recombinant; UDP-glucose donor + kaempferol 3-O-glucoside -> kaempferol 3-O-glucosyl(1->2)glucoside; source figure/MS standards and 2-doubleprime site",
  source_group="Arabidopsis_UGT79B6_2014",
  parent_domain=["3O_betaD_Glcp"],product="kaempferol 3-O-beta-D-glucopyranosyl-(1->2)-beta-D-glucopyranoside",
  DOI="10.1111/tpj.12580")
 }
 notes=[]
 for sid,x in spec.items():
  raw=Path(d3[sid]["raw_source_path"]);rsha=d3[sid]["raw_source_SHA"]
  assert sha(raw)==rsha==d4[sid]["original_SHA"]==d5[sid]["raw_SHA"]
  body=ET.fromstring((ROOT/raw).read_bytes()).find("./body");assert body is not None
  paragraph=txt(body.findall(".//p")[int(x["anchor"].split("-")[-1])-1])
  confirms=txt(body.findall(".//p")[int(x["confirm_anchor"].split("-")[-1])-1])
  a4paragraph=next(r for r in d4[sid]["selected_original_paragraphs"] if r["anchor"]==x["anchor"])
  a5paragraph=next(r for r in d5[sid]["original_candidate_reaction_evidence"] if r["anchor"]==x["anchor"])
  h=hashlib.sha256(paragraph.encode()).hexdigest()
  assert h==a4paragraph["sha256"]==a5paragraph["literal_sha256"]
  for term in x["expected"]:
   assert term.casefold() in paragraph.casefold(),(sid,term)
  if sid=="PMC4494776":
   assert "UDP-glucose" in confirms and "kaempferol 3-O-sophoroside" in confirms
   assert "UDP-glucose" in paragraph and "UDP-galactose" in paragraph
  if sid=="PMC4282749":
   assert "UDP-glucose" in confirms and "UDP-galactose" in confirms
   assert "UDP-glucose" in paragraph or "kaempferol 3-O-glucosyl" in paragraph
  notes.append(dict(PMCID=sid,DOI=x["DOI"],
    original_SHA=rsha,original_path=str(raw),source_group=x["source_group"],
    independently_A4_A5_reconciled_reaction_paragraph=x["anchor"],
    A4_A5_original_paragraph_SHA=h,
    corroborating_original_paragraph=x["confirm_anchor"],
    corroborating_SHA=hashlib.sha256(confirms.encode()).hexdigest(),
    demonstration=x["representative"],parent_domain=x["parent_domain"],
    named_product=x["product"],glycosidic_site="parent 3O-glycoside sugar O2; (1->2) linkage",
    transferred_donor="UDP-glucose",
    same_scope_enzymatic_sugarO2_source_positive=True,
    source_scope_not_full_stereochemical_graph=True,
    original_pub_and_preprint_same_group=False,
    permanently_historical_exposed=True,
    independent_full_stereo_atomgraph=False,
    structure_complete=False,runtime_complete=False,fresh=False))
 prev=j(PREV)
 assert prev["source_science_reaction_supported"] and prev["representative_primary_published_PMCID"]=="PMC12611259"
 group_universe=["Tomato_SlUGT79B-B_2025"]+[r["source_group"] for r in notes]
 assert len(set(group_universe))==3
 out=dict(task=T,epoch_id="SS-E02",family="SS",role="A6_source_chemical_O2_evidence_reconciliation",
  at=datetime.now(timezone.utc).isoformat(),
  two_original_primary_O2_sources=notes,
  independent_O2_groups_newly_verified_this_round=2,
  independent_O2_groups_including_prior_tomato=3,
  group_universe=group_universe,
  same_frozen_scope_source_positive=True,
  original_direct_enzyme_reaction_qualification_source_level=2,
  same_source_preprint_alias_counted_once=True,
  no_new_full_structure_graph_admission=True,
  complete_reaction_atomgraphs_admitted=0,
  current_epoch_fresh_holdout_admitted=0,
  historical_exposure_fails_fresh=True,
  formal_G7_panel_not_created=True,
  scientific_A_B_E_cells_added=0,
  no_reinterpretation_of_frozen_scope=True,
  no_model_read=True,approval_type="agent_delegated",human_reviewed=False,
  different_species_cultures_genes_and_published_original_experiment_groups=True)
 dest=R/"A6/two_original_O2_scientific_group_closure.json"
 save(dest,out)
 inp=[A3,A4,A5,PREV,R/"A0_science_read_precontract.json",
  R/"before_original_science_permanent_exposure.json",dest,SCOPE,
  Path("scripts/task016_p7_ss_r29_A0_A3.py"),
  Path("scripts/task016_p7_ss_r29_A4.py"),
  Path("scripts/task016_p7_ss_r29_A5.py"),
  Path("scripts/task016_p7_ss_r29_A6.py")]+[Path(z["original_path"]) for z in notes]
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",inp,G5,
   expected_previous_sha=sha(G5),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 event_row=dict(task=T,epoch_id="SS-E02",family="SS",stage="G6_IDENTITY_STRUCTURE_ADMIT",
  status="active",event_type="R29_2_distinct_recombinant_O2_source_groups_reconciled",
  stage_manifest_path=str(G6),stage_manifest_sha256=sha(G6),
  independently_qualified_source_groups_this_round=2,
  three_groups_with_prior_tomato=3,
  complete_reaction_graphs_admitted=0,fresh_admitted=0,
  model_replay=False,human_reviewed=False,approval_type="agent_delegated")
 write(T,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(event_row,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"SS_E02_R29_A6_primary_recombinant_O2_groups",G6_SHA=sha(G6),
  independent_groups_current=2,including_tomato=3,fresh=0)
 print(json.dumps(dict(SS_originals_newly_reconciled=2,independent_source_groups_total=3,G6=sha(G6),fresh=0)))
if __name__=="__main__":main()


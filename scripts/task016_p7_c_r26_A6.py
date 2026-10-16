"""P7 C-E02 R26 A6 reconcile independent A4/A5 on three actual JATS originals.

Enforce exact matching source paragraph SHA and identify *this paper's* tested
reaction, not a cited external primary reaction. No C6 fresh admission.
"""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,freeze_stage_manifest
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
G5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
G6=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G6_IDENTITY_STRUCTURE_ADMIT.json"
A4=R/"A4/first_original_C_reaction_screen.json"
A5=R/"A5/second_independent_canonical_site_screen.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
SCOPE=B/"C/E02/scope_manifest.json"
EPOCH=B/"epoch_ledger.jsonl"
def sha(p):return sha_file(ROOT/p)
def j(p):return json.loads((ROOT/p).read_text())
def text(n):return " ".join("".join(n.itertext()).split())
def save(p,v):
 if (ROOT/p).exists():raise RuntimeError("R26_IMMUTABLE_ALREADY_EXISTS")
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 assert not (ROOT/G6).exists()
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 a=j(A4);b=j(A5);pre=j(R/"A0_pre_read_contract.json")
 assert a["source_count"]==b["original_source_count"]==len(pre["selected"])==3
 d4={x["PMCID"]:x for x in a["sources"]}
 d5={x["PMCID"]:x for x in b["sources"]}
 assert set(d4)==set(d5)=={"PMC9855344","PMC12525976","PMC11577821"}
 decisions={
 "PMC9855344":dict(anchor="body/p-3",evidence_class="transcriptomic_candidate/review_of_prior_C8",
   own_study_primary_reaction="candidate expression/correlation for puerarin biosynthesis; cites C8 isoflavone routes rather than a directly demonstrated flavone C6 UDP-glucose reaction",
   scope_C6_direct_flavone=False,reason="isoflavone puerarin 8-C (and pathway ambiguity) not frozen flavone C6; no own-source complete single-step C6 reaction"),
 "PMC12525976":dict(anchor="body/p-18",evidence_class="primary_UGT84_nonC6_assays_plus_two_C6_primary_citations",
   own_study_primary_reaction="UGT84A28 and UGT84B3 assays: apigenin/naringenin O7, luteolin O3prime; explicitly NOT apigenin/naringenin C6",
   scope_C6_direct_flavone=False,reason="observed glycosylations are O, not C6; cites independent original C6 GtUF6CGT1 and UGT84A57 studies (doi 10.1016/j.febslet.2014.11.045; 10.1093/pcp/pcz164) but their reactions cannot be assigned to this study"),
 "PMC11577821":dict(anchor="body/p-33",evidence_class="primary_C_transfer_on_outside_acceptors",
   own_study_primary_reaction="UGT708S6 C-glycosylation of phloretin and 2-hydroxynaringenin; assays on luteolin/naringenin/liquiritigenin give O-glycosides rather than required direct flavone C6",
   scope_C6_direct_flavone=False,reason="C-positive acceptors are dihydrochalcone/2-hydroxyflavanone not frozen C3-H flavone C6; body/p-51 C6 refers 2-hydroxynaringenin and is not target-domain flavone"),
 }
 sources=[]
 for sid,x in decisions.items():
  u=d4[sid];v=d5[sid]
  assert u["original_SHA"]==v["source_SHA"]==sha(Path(u["original_path"]))
  a4=next(y for y in u["selected_paragraphs"] if y["location"]==x["anchor"])
  a5=next(y for y in v["potentially_relevant_evidence"] if y["anchor"]==x["anchor"])
  assert a4["paragraph_SHA256"]==a5["sha256"]
  body=ET.fromstring((ROOT/u["original_path"]).read_bytes()).find("./body")
  para=text(body.findall(".//p")[int(x["anchor"].split("-")[-1])-1])
  assert hashlib.sha256(para.encode()).hexdigest()==a4["paragraph_SHA256"]
  if sid=="PMC9855344":assert "8-C-glucosyl" in para and "isoflavanone" in para
  if sid=="PMC12525976":assert "rather than 6-C glycosylation" in para and "GtUF6CGT1" in para
  if sid=="PMC11577821":assert "phloretin" in para.lower() and "2-hydroxynaringenin" in para.lower()
  sources.append(dict(PMCID=sid,DOI=next(z["DOI"] for z in pre["selected"] if z["PMCID"]==sid),
   scientific_primary_source_disposition=x,full_article_SHA=u["original_SHA"],
   original_paragraph_anchor=x["anchor"],A4_A5_paragraph_SHA=a4["paragraph_SHA256"],
   known_prior_literature_exposure=next(z["prior_exposure_literals"] for z in pre["selected"] if z["PMCID"]==sid),
   source_scope_qualified=False,full_structural_qualification=False,fresh_admitted=False,
   independent_A4_A5_same_source_paragraph=True))
 out=dict(task=T,family="C",epoch_id="C-E02",role="A6_source_science_and_scope_reconciliation",
   at=datetime.now(timezone.utc).isoformat(),sources=sources,
   original_primary_science_reviewed=3,original_source_scope_positive_C6=0,
   scope_eligible_C6_reactions_found_in_these_three_originals=0,
   independent_direct_C6_primary_literature_leads=2,
   new_direct_C6_source_DOIs=["10.1016/j.febslet.2014.11.045","10.1093/pcp/pcz164"],
   scientific_qualifications_of_cited_DOIs="not_assessed_in_this_G6; separate official primary original required",
   new_fresh=0,new_independent_admitted_groups=0,
   no_model_MCTS=True,no_scope_redefinition=True,
   false_C6_from_protein_residue_or_C6_on_2_hydroxynaringenin_blocked=True,
   human_reviewed=False,approval_type="agent_delegated")
 dest=R/"A6/three_original_science_scope_dispositions.json"
 save(dest,out)
 paths=[A3,A4,A5,R/"A0_pre_read_contract.json",
   R/"pre_science_exposure_and_identity.json",dest,SCOPE,
   Path("scripts/task016_p7_c_r26_A0.py"),Path("scripts/task016_p7_c_r26_A4.py"),
   Path("scripts/task016_p7_c_r26_A5.py"),Path("scripts/task016_p7_c_r26_A6.py")]
 paths += [Path(x["source_path"]) for x in pre["selected"]]
 freeze_stage_manifest(ROOT/G6.parent,"G6_IDENTITY_STRUCTURE_ADMIT",paths,G5,
   expected_previous_sha=sha(G5),family="C",epoch_id="C-E02")
 assert verify_stage_chain(ROOT/G6,sha(G6))["stage"]=="G6_IDENTITY_STRUCTURE_ADMIT"
 ev=dict(task=T,epoch_id="C-E02",family="C",stage="G6_IDENTITY_STRUCTURE_ADMIT",
  event_type="R26_three_original_C_science_screen_and_C6_citation_bridge",
  status="active",stage_manifest_path=str(G6),stage_manifest_sha256=sha(G6),
  source_count=3,C6_source_scope_positive=0,independent_new_C6_reference_leads=2,
  fresh_admitted=0,human_reviewed=False,approval_type="agent_delegated")
 write(T,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(ev,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"C_E02_R26_A6_C6_bibliographic_bridge",source_originals_reviewed=3,verified_independent_C6_title_leads=2,G6_SHA=sha(G6))
 print(json.dumps(dict(R26_C3_original_science=3,in_scope_positive=0,distinct_C6_primary_leads=2,G6_SHA=sha(G6),fresh=0)))
if __name__=="__main__":main()


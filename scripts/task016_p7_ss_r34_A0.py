"""R34 A0: prospective SI science registration; no scientific PDF content read."""
import hashlib,json
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_r18_PMC_originals import now,sha,load,lines,put,gate
from scripts.task016_p7_orchestrate import freeze_stage_manifest,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R31=B/"SS/E02/fresh/SS-E02-R31-ACS-public-SI-custody-v1"
R32=B/"SS/E02/fresh/SS-E02-R32-ACS-SI-expiry-recovery-v1"
R=B/"SS/E02/fresh/SS-E02-R34-three-ACS-SI-science-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json";SCOPE=B/"SS/E02/scope_manifest.json"
G5=B/"SS/E02/stages/batches/SS-E02-R34-three-ACS-SI-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
INV=B/"governance/prior_exposure_inventory_v2"
SUP=B/"governance/R33-prior-stage-exposure-supplement-v1"
BIB=B/"SS/E02/fresh/SS-E02-R15-four-new-primary-bibliography-v1/A3_two_route_bibliographic_preflight_v2.json"
def main():
 if (ROOT/R).exists() or (ROOT/G5).exists():raise RuntimeError("IMMUTABLE")
 gate("SS")
 prior=lines(INV/"prior_exposure_rows.jsonl")+lines(SUP/"prior_stage_exposure_rows.jsonl")
 known={t for x in prior for t in x.get("closure_tokens",[])}
 records=[]
 allmeta=load(R31/"publisher_SI_metadata_projection.json")["records"]
 bibli=load(BIB)["records"]
 for ref in lines(R32/"http_ledger.jsonl"):
  if ref.get("status_code")!=200 or ref["status"]!="available":continue
  meta=next(x for x in allmeta if x["requested_doi"]==ref["doi"])
  bib=next(x for x in bibli if x["doi"]==ref["doi"])
  f=meta["metadata"]["files"][0];p=Path(ref["path"])
  data=(ROOT/p).read_bytes()
  assert data.startswith(b"%PDF-") and len(data)==f["size"] and sha(p)==ref["sha256"]
  md5=hashlib.md5(data).hexdigest()
  assert md5 in {f.get("supplied_md5"),f.get("computed_md5")}
  ids={"doi:"+ref["doi"],"pmid:"+bib["pmid"]}
  records.append(dict(source_id=ref["doi"],DOI=ref["doi"],PMID=bib["pmid"],title=bib["Crossref_title"],journal=bib["Crossref_journal"],years=bib["Crossref_years"],original_path=str(p),original_SHA=ref["sha256"],original_bytes=len(data),official_file_name=f["name"],official_file_MD5=md5,official_resource_DOI=meta["resource_doi"],Figshare_article_id=meta["metadata"]["id"],Figshare_SI_DOI=meta["metadata"]["doi"],license=meta["metadata"]["license"],publisher_link=bib["original_raw"],metadata_bibliographic_identity_verified=True,original_SI_front_identity_verified=False,prior_literal_tokens_present=sorted(ids&known),full_alias_or_graph_historical_clearance=False,full_chemical_reaction_qualified=False,source_scientific_body_read=False,fresh_eligible=None))
 assert len(records)==3
 qs=lines(R32/"query_execution.jsonl")
 assert len(qs)==6 and len({x["query_id"] for x in qs})==6
 put(R32/"raw_custody_summary.json",dict(task=T,at=now(),agent_role="A2_raw_only",approval_type="agent_delegated",planned=6,terminal=6,physical_HTTP=6,files_available=3,pdf_magic_and_official_size_MD5_SHA_verified=3,bytes=sum(x["original_bytes"] for x in records),sources=records,no_scientific_read=True,expiry_failures_preserved_in=str(R31),scientific_admitted=0,fresh_admitted=0))
 inputs=[R32/"raw_custody_summary.json",R31/"publisher_SI_metadata_projection.json",BIB,G4,SCOPE,INV/"prior_exposure_rows.jsonl",INV/"prior_exposure_snapshot_SS.json",SUP/"prior_stage_exposure_rows.jsonl",SUP/"inventory_provenance.json",Path("scripts/task016_p7_ss_r34_A0.py")]+[Path(x["original_path"]) for x in records]
 put(R/"pre_science_exposure_contract.json",dict(task=T,family="SS",epoch_id="SS-E02",at=now(),approval_type="agent_delegated",human_reviewed=False,source_universe=records,selection_reason="Three primary ACS source bibliographies discovered without source chemistry; official public SI custody completed, fixed before reading scientific content.",read_scope="Exact SHA-bound three SI PDFs; A3 first-page front, independent isolated A4 Poppler and A5 PyMuPDF extraction, then A6 reconciliation. No main-article scientific excerpt available.",scope_G4_SHA=sha(G4),scope_manifest_SHA=sha(SCOPE),no_scope_modification=True,no_model_outcome_read=True,no_MCTS=True,source_body_unread_before_G5=True,permanent_exposure_upon_first_read=True,prospective_own_post_G5_read_policy="Current epoch qualification only if prior alias/graph closure and all other gates pass; future epochs permanently exclude.",original_A3_pending=True,prior_alias_graph_and_28_names_pending=True,prior_inventory_drift_issues=load(SUP/"inventory_provenance.json")["input_drift_issues"],old_R12_mutable_input_drift_not_silently_cleared=True,actual_G7_blocked_pending_resolution=True,qualification_not_prejudged=True,counts=dict(selected=3,admitted=0,pending=3,rejected=0),input_SHA={str(p):sha(p) for p in inputs}))
 inputs.append(R/"pre_science_exposure_contract.json")
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",inputs,G4,expected_previous_sha=sha(G4),family="SS",epoch_id="SS-E02")
 verify_stage_chain(ROOT/G5,sha(G5))
 ledger=B/"epoch_ledger.jsonl"
 row=dict(task=T,epoch_id="SS-E02",family="SS",stage="G5_FRESH_HOLDOUT_ACQUIRE",status="active",at=now(),event_type="R34_three_ACS_public_SI_science_prospective_registration",stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),scope_manifest_path=str(SCOPE),scope_manifest_sha256=sha(SCOPE),source_count=3,scientific_body_read=False,prior_alias_graph_clearance=False,fresh_admitted=0,human_reviewed=False,approval_type="agent_delegated")
 write(T,str(ledger),(ROOT/ledger).read_text()+json.dumps(row,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"SS_R34_G5_before_SI_science",G5_SHA=sha(G5),selected=3)
 print(json.dumps(dict(G5=sha(G5),sources=3,official_MD5_verified=3,prior_literal_hits=sum(bool(x["prior_literal_tokens_present"]) for x in records),admitted=0)))
if __name__=="__main__":main()

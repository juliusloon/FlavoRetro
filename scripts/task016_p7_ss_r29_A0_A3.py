"""SS-E02 R29 original front A3 + G5 mandatory pre-science prereg.

Reuse previously SHA-preserved Fg3 original and newly public JATS Arabidopsis.
Historical exposure explicit; neither source can be fresh evaluation.
"""
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import verify_stage_chain,freeze_stage_manifest,sha_file
from scripts.task016_p7_c_e02_http import physical_attempts
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
G4=B/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
SCOPE=B/"SS/E02/scope_manifest.json"
EPOCH=B/"epoch_ledger.jsonl"
EXPOSE=B/"exposure_ledger.jsonl"
HIST=B/"governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl"
R28=B/"governance/R28-SS-Arabidopsis-original-access-v1/raw_custody_summary.json"
SIDS=["PMC4494776","PMC4282749"]
def sha(p):return sha_file(ROOT/p)
def j(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()] if (ROOT/p).exists() else []
def txt(el):return " ".join("".join(el.itertext()).split()) if el is not None else None
def put(p,x):
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_"+str(p))
 write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 if (ROOT/G5).exists():raise RuntimeError("IMMUTABLE_G5_EXISTS")
 assert verify_stage_chain(ROOT/G4,sha(G4))["stage"]=="G4_SCOPE_FREEZE"
 assert j(R28)["usable_original_XML"]==1
 old=physical_attempts()
 selected=[]
 for sid in SIDS:
  uri="https://www.ebi.ac.uk/europepmc/webservices/rest/"+sid+"/fullTextXML"
  possible=[r for r in old if r["url"]==uri and r.get("status_code")==200 and r.get("status")=="available" and r.get("kind")=="article_version"]
  assert len(possible)==1,(sid,len(possible))
  ref=possible[0]
  raw=Path(ref["path"])
  assert sha(raw)==ref["sha256"] and (ROOT/raw).stat().st_size==ref["bytes"]
  tree=ET.fromstring((ROOT/raw).read_bytes())
  front=tree.find("./front");assert front is not None
  meta=front.find("./article-meta")
  ids={x.get("pub-id-type"):txt(x) for x in meta.findall("./article-id") if x.get("pub-id-type")}
  assert ids.get("pmcid")==sid,ids
  title=txt(meta.find("./title-group/article-title"))
  doi=ids.get("doi")
  year=sorted({txt(x) for x in meta.findall("./pub-date/year")})
  journal=txt(front.find("./journal-meta/journal-title-group/journal-title"))
  assert doi and title and year
  selected.append(dict(PMCID=sid,DOI=doi,PMID=ids.get("pmid"),title=title,journal=journal,years=year,
    raw_source_path=str(raw),raw_source_SHA=ref["sha256"],raw_bytes=ref["bytes"],
    source_retrieval_original=ref["url"],original_front_identity_verified=True,
    prior_historical_exposure=True,scientific_body_current_R29_not_read=True,
    source_closure_group="Soybean_Fg3_2015" if sid=="PMC4494776" else "Arabidopsis_UGT79B6_2014",
    same_study_as_tomato_2025=False))
 assert len({x["source_closure_group"] for x in selected})==2
 source_text=((ROOT/EXPOSE).read_text()+(ROOT/HIST).read_text()).casefold()
 for x in selected:
  assert x["PMCID"].casefold() in source_text
 at=datetime.now(timezone.utc).isoformat()
 put(R/"A3_original_front_verified.json",dict(task=T,role="A3_front_only",at=at,
  sources=selected,front_identity_verified=2,no_abstract_or_body_read=True,
  prior_historical_PMCID_identity_both_positive=True,source_originals_currently_available=2,
  no_structure_or_fresh_promotion=True))
 paths=[R/"A3_original_front_verified.json",G4,SCOPE,EXPOSE,HIST,R28,
   Path("scripts/task016_p7_ss_r29_A0_A3.py")]+[Path(x["raw_source_path"]) for x in selected]
 put(R/"before_original_science_permanent_exposure.json",dict(task=T,epoch_id="SS-E02",
  registered_at=at,source_identifiers=[dict(PMCID=x["PMCID"],DOI=x["DOI"],
   original_SHA=x["raw_source_SHA"],group=x["source_closure_group"]) for x in selected],
  historical_exposure_sources=2,no_fresh_eligible_sources=2,
  source_original_bodies_unread_this_round=True,
  science_read_only_after_frozen_G5=True,
  no_unauthorized_human_or_formal_promotion=True))
 paths.append(R/"before_original_science_permanent_exposure.json")
 put(R/"A0_science_read_precontract.json",dict(task=T,epoch_id="SS-E02",family="SS",
  at=at,approval_type="agent_delegated",human_reviewed=False,
  original_sources=selected,original_A3_SHA=sha(R/"A3_original_front_verified.json"),
  stages=dict(A4="standalone science reader independent of A5",A5="separate original science reader independent of A4",A6="cross-check only after both"),
  allowed_science_read="exact original JATS bodies and figure/table captions in SHA-bound two sources only",
  intended_reaction="flavonol 3-O-glycoside sugar residue O2 using UDP-glucose",
  no_duplicate_study_group_claim=True,no_chemical_source_qualified_by_title=True,
  no_fresh_no_model_outcome_read=True,no_MCTS=True,
  frozen_G4_SHA=sha(G4),frozen_scope_SHA=sha(SCOPE),
  input_SHA={str(p):sha(p) for p in paths}))
 paths.append(R/"A0_science_read_precontract.json")
 freeze_stage_manifest(ROOT/G5.parent,"G5_FRESH_HOLDOUT_ACQUIRE",paths,G4,
  expected_previous_sha=sha(G4),family="SS",epoch_id="SS-E02")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 ledger_row=dict(task=T,epoch_id="SS-E02",family="SS",stage="G5_FRESH_HOLDOUT_ACQUIRE",
  event_type="R29_two_original_known_exposed_science_prereg",status="active",
  stage_manifest_path=str(G5),stage_manifest_sha256=sha(G5),
  scope_manifest_path=str(SCOPE),scope_manifest_sha256=sha(SCOPE),
  original_count=2,source_group_count=2,historical_exposure=True,fresh_admitted=0,
  human_reviewed=False,approval_type="agent_delegated")
 write(T,str(EPOCH),(ROOT/EPOCH).read_text()+json.dumps(ledger_row,ensure_ascii=False,sort_keys=True)+"\n")
 event(T,"SS_R29_G5_science_pre_exposure_frozen",G5_SHA=sha(G5),originals=2)
 print(json.dumps(dict(A3_originals=2,G5=sha(G5),prior_exposed=2,
  sources=[(x["PMCID"],x["DOI"]) for x in selected])))
if __name__=="__main__":main()


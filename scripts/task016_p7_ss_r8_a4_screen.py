"""SS-R8 A4: independent, source-pointer body-text screen, no structure inference.
No access to A5 output. Only A0-preregistered XML bodies may be inspected.
"""
import hashlib,json,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts.task016_p7_ss_sources import require_acquisition_phase
from scripts.task016_p7_orchestrate import verify_stage_chain
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R8=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
OUT=R8/"A4"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def local(t):return t.rsplit("}",1)[-1]
def txt(e):return " ".join("".join(e.itertext()).split())
def main():
 if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_A4_EXISTS")
 plan=load(R8/"A0_science_read_precontract.json")
 assert plan["count"]==2 and plan["read_permission"].startswith("only these two")
 for p,h in plan["input_SHA256"].items():
  if sha(Path(p))!=h:raise RuntimeError("INPUT_SHA_DRIFT "+p)
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 er=load(R8/"pre_read_exposure.json")
 assert len(er["source_universe"])==2 and er["chemical_read_started"] is False
 pre={"task":TASK,"role":"A4","timestamp":datetime.now(timezone.utc).isoformat(),
  "source_universe":plan["planned_sources"],"input_contract_SHA":sha(R8/"A0_science_read_precontract.json"),
  "G5_SHA":sha(G5),"exposure_prior_to_first_read_sha":sha(R8/"pre_read_exposure.json"),
  "no_access_to_other_extractor_output":True,"no_model_or_holdout_outcome_read":True}
 write(TASK,str(OUT/"pre_execution.json"),json.dumps(pre,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 science=[];terms=re.compile(r"glucosyltransferase|glycosyltransferase|glucosylat|glycosylat|flavonoid|flavonol|glucoside|glycoside|anthocyan",re.I)
 motifs={"possible_sugar_sugar":re.compile(r"(?:glycosylat|glucosylat|transfer)[^.]{0,110}(?:glucoside|glycoside)|(?:glucoside|glycoside)[^.]{0,110}(?:glycosylat|glucosylat|transfer)",re.I),
   "two_prime_or_O2":re.compile(r"(?:[23][\u2032\u2019']{1,2}|2-O-|2\u2032-O-|2\u2032\u2032-O-|sophoroside|rutinoside)",re.I),
   "aglycone_site":re.compile(r"(?:3|5|7)-?O(?:H)?(?:[- ]?glucosylat|[- ]?glycosylat|[- ]?glucoside)|7-OH",re.I)}
 for record in plan["planned_sources"]:
  raw=Path(record["raw_original"]["path"])
  if sha(raw)!=record["raw_original"]["sha256"]:raise RuntimeError("RAW_INPUT_SHA_CHANGED")
  event(TASK,"SS_R8_A4_original_science_read_start",source_id=record["source_id"],
        raw_sha256=sha(raw),G5_SHA=sha(G5),exposure_registered_prior=True)
  tree=ET.parse(ROOT/raw)
  body=next((c for c in tree.getroot().iter() if local(c.tag)=="body"),None)
  if body is None:raise RuntimeError("MISSING_ORIGINAL_SCIENTIFIC_BODY")
  para=[x for x in body.iter() if local(x.tag)=="p"]
  rows=[];matches={k:0 for k in motifs}
  for ordinal,p in enumerate(para,1):
   t=txt(p)
   flags={key:bool(pattern.search(t)) for key,pattern in motifs.items()}
   for key,v in flags.items():matches[key]+=int(v)
   if terms.search(t):
    rows.append({"xml_body_p_ordinal":ordinal,"p_sha256":hashlib.sha256(t.encode()).hexdigest(),
      "excerpt":t[:340],"matched_motifs":[k for k,v in flags.items() if v],
      "source_evidence_pointer":f"{raw}#body/p-{ordinal}"})
  science.append({"source_id":record["source_id"],"raw_original_path":str(raw),
    "raw_SHA":sha(raw),"body_paragraphs":len(para),"keyword_paragraphs":len(rows),
    "candidate_motif_paragraphs":matches,"evidence_pointers":rows[:90],
    "all_keyword_pointers_retained":len(rows)<=90,
    "complete_reaction_structure_extracted":False,
    "source_O2_reaction_qualified":False,"source_exposed":True,"fresh_eligible":False,
    "no_graph_guessed_from_paragraphs":True,
    "disposition":"pending_independent_A5_and_source_reaction_scope_review"})
 result={"task":TASK,"agent_role":"A4","timestamp":datetime.now(timezone.utc).isoformat(),
    "input_pre_execution_sha":sha(OUT/"pre_execution.json"),
    "sources":science,"counts":{"processed":2,"passed_scientific":0,"rejected":0,"pending":2},
    "human_reviewed":False,"read_chemical_original":True,"read_model_outcome":False,
    "fresh_admitted":0,"not_a_reaction_structure_extraction":True,
    "no_new_HTTP":True,"no_new_MCTS":True}
 write(TASK,str(OUT/"source_body_screen.json"),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"A4_sources":2,"paragraph_counts":[r["body_paragraphs"] for r in science],
   "possible_sugar_sugar_hits":[r["candidate_motif_paragraphs"]["possible_sugar_sugar"] for r in science],
   "fresh":0},ensure_ascii=False))
if __name__=="__main__":main()

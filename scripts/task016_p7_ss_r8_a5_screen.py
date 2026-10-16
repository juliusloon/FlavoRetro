"""SS-R8 A5: separate science-body section/caption screen from original XML.
Not A4's parser or output; no structure/SMILES inference and no fresh upgrade.
"""
from pathlib import Path
import json,hashlib,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from scripts.operate import ROOT,write,event
from scripts.task016_p7_orchestrate import verify_stage_chain
from scripts.task016_p7_ss_sources import require_acquisition_phase
TASK="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R8=B/"SS/E02/fresh/SS-E02-R8-science-screen-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R8-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
OUT=R8/"A5"
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def get(p):return json.loads((ROOT/p).read_text())
def lname(e):return e.tag.split("}")[-1]
def text(e):return re.sub(r"\s+"," ","".join(e.itertext())).strip()
def main():
 if (ROOT/OUT).exists():raise RuntimeError("A5_EXISTING_OUTPUT")
 inputs=get(R8/"A0_science_read_precontract.json")
 if len(inputs["planned_sources"])!=2:raise RuntimeError("WRONG_UNIVERSE")
 for p,h in inputs["input_SHA256"].items():
  if sha(Path(p))!=h:raise RuntimeError("PRECONTRACT_INPUT_SHA_DIFF")
 verify_stage_chain(ROOT/G5,sha(G5))
 require_acquisition_phase("fresh",epoch_id="SS-E02",scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
 preread=get(R8/"pre_read_exposure.json")
 assert len(preread["source_universe"])==2 and all(s["source_exposure"]=="permanently_science_exposed_before_first_read" for s in preread["source_universe"])
 pre={"task":TASK,"agent_role":"A5",
  "precontract_SHA":sha(R8/"A0_science_read_precontract.json"),"G5_SHA":sha(G5),
  "preregistered_exposure_sha":sha(R8/"pre_read_exposure.json"),
  "timestamp":datetime.now(timezone.utc).isoformat(),
  "other_extractor_A4_output_not_read":True,
  "no_outcome_or_scope_adjustment":True}
 write(TASK,str(OUT/"pre_execution.json"),json.dumps(pre,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
 patterns={
  "explicit_second_sugar_motif":re.compile(r"\b(?:[23][\u2032\u2019']{1,2}[-\s]?O|sophoroside|rutinoside|glucosyl[- ]glucoside|diglucoside|disaccharide)\b",re.I),
  "flavonoid_glucosyltransferase":re.compile(r"\b(?:flavonol|flavonoid|anthocyan|glycoside|glucosyltransferase|glycosyltransferase)\b",re.I),
  "specific_acceptor_glucoside":re.compile(r"(?:flavonol|flavonoid|anthocyan)[^.;:]{0,85}(?:3[- ]?O[- ]?glucoside|7[- ]?O[- ]?glucoside)|(?:3[- ]?O[- ]?glucoside|7[- ]?O[- ]?glucoside)[^.;:]{0,85}(?:flavonol|flavonoid|anthocyan)",re.I),
  "explicit_glycoside_acceptor":re.compile(r"(?:acceptor|substrate)[^.;:]{0,95}(?:flavonol|anthocyan)[^.;:]{0,45}(?:glucoside|glycoside)|(?:flavonol|anthocyan)[^.;:]{0,80}(?:glucoside|glycoside)[^.;:]{0,95}(?:acceptor|substrate)",re.I)}
 results=[]
 for source in inputs["planned_sources"]:
  original=Path(source["raw_original"]["path"])
  if sha(original)!=source["raw_original"]["sha256"]:raise RuntimeError("R8_RAW_CHANGED")
  event(TASK,"SS_R8_A5_original_science_read_start",source_id=source["source_id"],G5_SHA=sha(G5),
      original_sha256=sha(original),permanent_exposure_preregistered=True)
  tree=ET.parse(ROOT/original)
  body=next((x for x in tree.getroot() if lname(x)=="body"),None)
  if body is None:raise RuntimeError("ABSENT_XML_BODY")
  section_titles=[];caption_count=0;paragraph_count=0;hit_count={k:0 for k in patterns};hits=[]
  for e in body.iter():
   typ=lname(e)
   if typ=="title":
    section_titles.append(text(e)[:130])
   if typ in ("p","caption","table-wrap"):
    if typ=="p":paragraph_count+=1
    if typ=="caption":caption_count+=1
    chunk=text(e)
    matched=[k for k,rx in patterns.items() if rx.search(chunk)]
    for k in matched:hit_count[k]+=1
    if matched and len(hits)<115:
     hits.append({"element":typ,"paragraph_ordinal":paragraph_count,
      "record_SHA":hashlib.sha256(chunk.encode()).hexdigest(),
      "text_excerpt":chunk[:260],"motifs":matched,
      "evidence_location":f"{original}#body/{typ}-at-p{paragraph_count}"})
  results.append({"source_id":source["source_id"],"scientific_original":str(original),
    "original_sha256":sha(original),"body_paragraph_count":paragraph_count,
    "caption_elements":caption_count,"section_titles":section_titles[:60],
    "motif_counts":hit_count,"sampled_contexts":hits,
    "contexts_truncated":len(hits)>=115,
    "qualification_requires_independent_full_reaction_source_claim":True,
    "reaction_structure_qualified":False,"scope_O2_qualified":False,
    "fresh_eligible":False,"source_permanently_exposed":True,
    "disposition":"independent_bounded_screen_pending_A6_full_reaction_audit"})
 out={"task":TASK,"agent_role":"A5",
    "timestamp":datetime.now(timezone.utc).isoformat(),"pre_execution_sha":sha(OUT/"pre_execution.json"),
    "sources":results,
    "counts":{"processed":2,"passed_scientific":0,"rejected":0,"pending":2},
    "chemical_text_read":True,"read_other_extractor":False,"read_model_outcome":False,
    "human_reviewed":False,"fresh_admitted":0,"new_HTTP":0,"new_MCTS":0}
 write(TASK,str(OUT/"independent_body_scope_screen.json"),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps({"A5_sources":2,
  "O2_related_motif_counts":[s["motif_counts"]["explicit_second_sugar_motif"] for s in results],
  "glycoside_acceptor_contexts":[s["motif_counts"]["explicit_glycoside_acceptor"] for s in results],
  "fresh":0},ensure_ascii=False))
if __name__=="__main__":main()

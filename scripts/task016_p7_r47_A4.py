"""R47 A4 input-only stdlib HTML original text extractor."""
from html.parser import HTMLParser
ROLE="A4";PARSER="stdlib HTMLParser"
BLOCKS={"p","h1","h2","h3","h4","tr","td","th","figcaption"}
class Reader(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.inside=0;self.sections=[];self.active=[];self.results=[];self.sequence=0
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if tag=="article":self.inside+=1
  if not self.inside:return
  if tag=="section":self.sections.append(d.get("id"))
  if tag in BLOCKS:
   self.sequence+=1;self.active.append(dict(tag=tag,index=self.sequence,section_path=list(self.sections),element_id=d.get("id"),parts=[]))
 def handle_data(self,data):
  for cap in self.active:cap["parts"].append(data)
 def handle_endtag(self,tag):
  if tag in BLOCKS:
   for i in range(len(self.active)-1,-1,-1):
    if self.active[i]["tag"]==tag:
     cap=self.active.pop(i);cap["text"]="".join(cap.pop("parts"));self.results.append(cap);break
  if tag=="section" and self.sections:self.sections.pop()
  if tag=="article":self.inside-=1
def parse(data):
 p=Reader();p.feed(data.decode("utf-8"));p.close()
 assert not p.active and p.inside==0
 return sorted(p.results,key=lambda x:x["index"])

import json,re,hashlib,os
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import load,put,sha,now
from scripts.task016_p7_orchestrate import role_manifest
from scripts import task016_p7_full_qualification_harness_v3 as fq
T="TASK-016-P7";B=Path("outputs/task016-p7/v1");SID="PMC13422134"
SHARED=B/"governance/R47-Iris-cross-axis-source-read-binding-v1/both_G5_ready_before_first_read.json"
def main():
 binding=load(SHARED);assert binding["first_scientific_read_not_yet_started"]
 # Check both actual G5s before either source open.
 for family in ("C","SS"):
  spec=fq.validate_full_qualification_contract(binding["contracts"][family])["contract"]
  fq._g5(binding["contracts"][family],spec,binding["G5"][family],ROOT)
 rid="R47-"+ROLE+"-isolated-"+str(os.getpid())
 for family in ("C","SS"):
  cp=binding["contracts"][family];spec=load(Path(cp["path"]));r=Path(cp["path"]).parent
  opened=fq.open_for_first_scientific_read(cp,binding["G5"][family],SID,ROLE,rid)
  blocks=[];opaque=[]
  for path,data in opened["payloads"].items():
   if data.startswith(b"\xff\xd8"):
    opaque.append(dict(path=path,sha256=sha(path),bytes=len(data),content="JPEG",decoded_for_chemical_graphs=False))
   else:
    assert b"<html" in data[:3000].lower() or b"<!doctype html" in data[:3000].lower()
    for block in parse(data):
     text=" ".join(block["text"].split())
     blocks.append(dict(block,text=text,text_SHA=hashlib.sha256(text.encode()).hexdigest(),source_file=path,source_SHA=sha(path)))
  contexts=[x for x in blocks if re.search(r"glycosyl|glucosyl|substrat|cataly|compound|product|sugar|UDP|luteolin|quercetin|kaempferol|naringenin",x["text"],re.I)]
  out=r/ROLE/"available_original_scientific_text.json"
  put(out,dict(task=T,agent_role=ROLE,source_id=SID,contract_sha256=cp["sha256"],timestamp=now(),parser=PARSER,blocks=blocks,literal_scientific_contexts=contexts,actual_reader_receipt=opened["receipt"],source_figures_opened_as_opaque_bytes=opaque,SI_original_access_pending=True,peer_final_read=False,independent_graph_transcription=False,unprocessed_chemical_reaction_enumeration=True))
  evidence=[fq.pointer(out),opened["receipt"],fq.pointer(SHARED)]
  result=r/ROLE/"round_result.json"
  put(result,dict(task=T,agent_role=ROLE,epoch_id=family+"-E02",contract_sha256=cp["sha256"],timestamp=now(),reader_id=rid,source_dispositions=[dict(source_id=SID,execution_state="completed",terminal_for_this_round=True,disposition="deferred",reason="Available main-original text scientifically processed; all advertised routes attempted. SI is a retained CAPTCHA HTML response, not a PDF. Complete chemical reaction/graph/site/stereo/precursor inventory and historical closure remain untranscribed; source images opened only as opaque bytes by this text extractor.",evidence=evidence,original_routes_executed=["EPMC_XML_attempt","PMC_public_open_data_index_attempt","PMC_public_HTML","Crossref_declared_publisher_HTML_attempt","PMC_advertised_SI_and_images_attempt"],scientific_body_read=True)],reaction_records=[],zero_reaction_records_means="No complete reaction records transcribed; does NOT mean no reactions in the paper.",chemical_reaction_enumeration_complete=False))
  inputs=[Path(cp["path"]),Path(binding["G5"][family]["path"]),r/"raw_source_universe.json",SHARED,Path(__file__).resolve().relative_to(ROOT)]
  role=role_manifest(ROLE,family+"-E02",inputs,[out,result],dict(processed=1,passed=0,rejected=0,pending=1),pointers=evidence,read_holdout=True,read_model_outcome=False)
  role.update(reader_id=rid,read_other_extractor_output=False,independent_graph_transcription=False,count_unit="one available original source text processed, chemistry qualification deferred",SI_original_access_pending=True)
  put(r/ROLE/"role_manifest.json",role)
  print(json.dumps(dict(role=ROLE,family=family,text_blocks=len(blocks),literal_contexts=len(contexts),opaque_images=len(opaque),qualified_graphs=0,SI_access_pending=True)),flush=True)
if __name__=="__main__":main()

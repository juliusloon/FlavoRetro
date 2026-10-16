"""R39 A5: isolated lxml decoding and independent token-context observations."""
from lxml import etree
ROLE="A5";PARSER="lxml original JATS and DOCX"
def parse(data,group):
 root=etree.fromstring(data)
 if group=="main":elements=root.xpath("./body//p");return [" ".join(" ".join(p.itertext()).split()) for p in elements]
 ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
 return [" ".join("".join(p.xpath(".//w:t/text()",namespaces=ns)).split()) for p in root.xpath("//w:p",namespaces=ns)]
def observe(rows):
 out={key:[] for key in ["acceptor","product","donor","site","anomer","enzyme","reference"]}
 for row in rows:
  text=row["text"];flat=text.casefold().replace("–","-").replace("‐","-").replace("‑","-")
  tokens=set(re.findall(r"[a-z0-9]+",flat))
  keys=[]
  if "luteolin" in tokens:keys.append("acceptor")
  if "isoorientin" in tokens:keys.append("product")
  if "udp" in tokens and ("glucose" in tokens or "glc" in tokens):keys.append("donor")
  if any(s in flat for s in ["6-c-glucos","6-c-glycos","c6-glucos","c-6-glucos","6 c glucos"]):keys.append("site")
  if "β" in text or "beta" in tokens:keys.append("anomer")
  if re.search(r"(?:ugt|cgt|gtuf6)",flat):keys.append("enzyme")
  if tokens.intersection({"standard","substrate","purified","purification","assay","supplementary"}):keys.append("reference")
  for key in keys:out[key].append(dict(group=row["group"],paragraph=row["index"],text_SHA=row["text_SHA"],text=text))
 return out

import json,re,hashlib,zipfile,io,os
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_r18_PMC_originals import sha,load,put,now
from scripts import task016_p7_full_qualification_harness_v3 as fq
from scripts.task016_p7_orchestrate import role_manifest
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
SID="PMC13564134"
def main():
 contract=fq.pointer(R/"full_qualification_contract.json")
 rid=ROLE+"-isolated-"+str(os.getpid())
 opened=fq.open_for_first_scientific_read(contract,fq.pointer(G5),SID,ROLE,rid)
 paragraphs=[]
 for path,data in opened["payloads"].items():
  group="SI" if data.startswith(b"PK") else "main"
  if group=="SI":
   with zipfile.ZipFile(io.BytesIO(data)) as z:xml=z.read("word/document.xml")
  else:xml=data
  for index,text in enumerate(parse(xml,group),1):
   paragraphs.append(dict(group=group,index=index,source_file=path,source_SHA=sha(Path(path)),text=text,text_SHA=hashlib.sha256(text.encode()).hexdigest()))
 out=R/ROLE/"original_scientific_paragraphs.json"
 put(out,dict(task=T,agent_role=ROLE,source_id=SID,contract_sha256=contract["sha256"],parser=PARSER,paragraphs=paragraphs,actual_reader_receipt=opened["receipt"],peer_final_read=False))
 findings=observe(paragraphs)
 results=R/ROLE/"round_result.json"
 evidence=[fq.pointer(out),opened["receipt"],fq.pointer(B/"C/E02/fresh/C-E02-R38-isoorientin-original-custody-v1/A3_original_front_identity.json"),fq.pointer(B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1/execution.jsonl")]
 put(results,dict(task=T,agent_role=ROLE,epoch_id="C-E02",contract_sha256=contract["sha256"],timestamp=now(),reader_id=rid,source_dispositions=[dict(source_id=SID,execution_state="completed",terminal_for_this_round=True,disposition="deferred",reason="Original main and SI scientifically read; named-context observations extracted independently. Full graph, donor/stereo/precursor and prior closure are not established by text alone.",evidence=evidence,original_routes_executed=["EuropePMC_fullTextXML","PMC_exact_index_advertised_SI"],scientific_body_read=True)],reaction_records=[dict(source_id=SID,reaction_id="R39:PMC13564134:isoorientin-endpoint",observed_evidence=findings,structure_record=None,complex_graphs_invented=False,full_reaction_qualified=False)],scientific_field_observations=findings))
 inputs=[R/"raw_source_universe.json",R/"full_qualification_contract.json",G5,B/"C/E02/fresh/C-E02-R38-isoorientin-original-custody-v1/A3_original_front_identity.json",B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1/execution.jsonl",Path(__file__).resolve().relative_to(ROOT)]
 role=role_manifest(ROLE,"C-E02",inputs,[out,results],dict(processed=1,passed=0,rejected=0,pending=1),pointers=evidence,read_holdout=True,read_model_outcome=False)
 role.update(reader_id=rid,read_other_extractor_output=False,independent_graph_transcription=False,qualification_pending_fields=["full_graphs","stereo","reference_precursors","historical_alias_graph_closure"],count_unit="one source scientifically processed with chemistry qualification pending")
 put(R/ROLE/"role_manifest.json",role)
 print(json.dumps(dict(role=ROLE,source=SID,main_paragraphs=sum(x["group"]=="main" for x in paragraphs),SI_paragraphs=sum(x["group"]=="SI" for x in paragraphs),observation_contexts=sum(len(v) for v in findings.values()),scientific_qualified=0)))
if __name__=="__main__":main()

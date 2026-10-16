"""R39 A4: isolated ElementTree source text and literal field observations."""
import xml.etree.ElementTree as ET
ROLE="A4";PARSER="stdlib ElementTree original JATS and DOCX"
def parse(data,group):
 root=ET.fromstring(data)
 if group=="main":
  body=root.find("./body")
  return [" ".join("".join(p.itertext()).split()) for p in body.iter("p")]
 ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
 return [" ".join("".join(x.text or "" for x in p.findall(".//w:t",ns)).split()) for p in root.findall(".//w:p",ns)]
def observe(rows):
 patterns=dict(acceptor=r"\bluteolin\b",product=r"\bisoorientin\b",donor=r"UDP[\s‐‑–-]*(?:glucose|Glc)\b",site=r"(?:6[\s‐‑–-]*C|C[\s‐‑–-]*6)[\s‐‑–-]*(?:glucos|glycos)|luteolin.{0,45}6[\s‐‑–-]*C",anomer=r"\bβ\b|\bbeta\b",enzyme=r"GtUF6CGT1|UGT84A57|[A-Za-z]+CGT\d*",reference=r"standard|purif|enzyme assay|substrate|supplement")
 return {key:[dict(group=x["group"],paragraph=x["index"],text_SHA=x["text_SHA"],text=x["text"]) for x in rows if re.search(pat,x["text"],re.I)] for key,pat in patterns.items()}

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

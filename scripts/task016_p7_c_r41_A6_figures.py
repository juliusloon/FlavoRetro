"""R41 A6 original figures supplement; exact advertised public PMC original PDF."""
import json,urllib.parse,io,zipfile,hashlib
from pathlib import Path
from scripts.operate import ROOT,write,event
from scripts import task016_p7_c_e02_http as transport
from scripts.task016_p7_r18_PMC_originals import gate,put,sha,load,lines,now
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
O=B/"C/E02/fresh/C-E02-R41-A6-original-figure-supplement-v1"
R=B/"C/E02/fresh/C-E02-R39-prospective-full-qualification-v1"
INDEX=B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1/object_index_projection.json"
G5=B/"C/E02/stages/batches/C-E02-R39-prospective-full-qualification/G5_FRESH_HOLDOUT_ACQUIRE.json"
transport.C=ROOT/O;transport.RAW=ROOT/"data/raw/task016-p7/C/E02/C-E02-R41-A6-original-figure-supplement-v1"
def pre():
 if (ROOT/O).exists():raise RuntimeError("IMMUTABLE")
 ga=gate("C");index=load(INDEX)
 matches=[x for x in index["objects"] if x["key"]=="PMC13564134.1/PMC13564134.1.pdf"]
 assert len(matches)==1
 obj=matches[0]
 put(O/"precontract.json",dict(task=T,family="C",epoch_id="C-E02",batch_id=O.name,at=now(),approval_type="agent_delegated",human_reviewed=False,G4_pointer=dict(path=ga["G4_path"],sha256=ga["G4_SHA"]),files_sha256={str(p):sha(p) for p in [INDEX,G5,R/"full_qualification_contract.json",R/"A4/round_result.json",R/"A5/round_result.json",Path(__file__).resolve().relative_to(ROOT)]},max_HTTP=1,max_article_bytes=8*1024**2,role="A6",reason="Supplemental same-source original figures after both independent text readers; no change to their frozen two-file source universe or G5. A6 only; not an independent second graph extraction.",scientific_read_permitted_role="A6",model_outcome_read=False,prior_read_receipts_preserved=True,source_id="PMC13564134",current_epoch_eligibility="conditional_only",future_fresh_eligible=False,development_exposed=True,exposure_type="current_epoch_evaluation",queries=[dict(query_id="R41-original-PDF",url="https://pmc-oa-opendata.s3.amazonaws.com/"+urllib.parse.quote(obj["key"],safe="/"),kind="original_pdf",limit=8*1024**2,advertised_size=obj["size"])]))
 print("A6 same-original figure supplement preregistered")
def run():
 c=load(O/"precontract.json")
 assert not (ROOT/O/"execution.jsonl").exists()
 for x in c["queries"]:
  r=transport.acquire(ROOT/O/"precontract.json",x["url"],x["kind"],"A6 exact official index-advertised same-source original PDF supplement; no new selected source.",object_limit=x["limit"])
  row=dict(query_id=x["query_id"],raw_pointer={k:r[k] for k in ["path","sha256","bytes"]},status=r["status"],HTTP_status=r["status_code"],advertised_size=x["advertised_size"],actual_size_match=r["bytes"]==x["advertised_size"])
  write(T,str(O/"execution.jsonl"),json.dumps(row,sort_keys=True)+"\n")
  print(json.dumps({k:row[k] for k in ["HTTP_status","status","actual_size_match"]}))
def render():
 import fitz
 from PIL import Image
 row=lines(O/"execution.jsonl")[0]
 assert row["status"]=="available" and row["actual_size_match"]
 raw=Path(row["raw_pointer"]["path"]);assert sha(raw)==row["raw_pointer"]["sha256"]
 data=(ROOT/raw).read_bytes();assert data.startswith(b"%PDF")
 exposure=dict(task=T,source_id="PMC13564134",timestamp=now(),reader_role="A6",G5=dict(path=str(G5),sha256=sha(G5)),raw_pointer=row["raw_pointer"],contract_sha256=sha(R/"full_qualification_contract.json"),closure_tokens=["article:PMC13564134","doi:10.1016/j.abiote.2026.100085","pmid:42730264"],development_exposed=True,scientific_content_read=True,exposure_type="current_epoch_evaluation",future_fresh_eligible=False,current_epoch_eligibility="conditional_only",read_model_outcome=False)
 put(O/"A6_scientific_read_receipt.json",exposure)
 doc=fitz.open(stream=data,filetype="pdf");pages=[]
 for i,page in enumerate(doc):
  txt=page.get_text()
  pages.append(dict(page=i+1,text=txt,text_SHA=hashlib.sha256(txt.encode()).hexdigest()))
 put(O/"original_pdf_text.json",dict(task=T,pages=pages,raw_pointer=row["raw_pointer"],page_count=len(doc),parser="PyMuPDF",not_dual_graph_transcription=True))
 # Render all pages for the A6 reviewer, raw figures stay outside Git.
 paths=[]
 for i,page in enumerate(doc):
  out=ROOT/"data/raw/task016-p7/C/E02/C-E02-R41-A6-original-figure-supplement-v1"/("A6-original-page-%02d.png"%(i+1))
  out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists():raise RuntimeError("IMMUTABLE")
  b=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).tobytes("png");out.write_bytes(b)
  event(T,"write_binary",path=str(out.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),reason="A6 source figure review render from acquired original")
  paths.append(dict(path=str(out.relative_to(ROOT)),sha256=sha(out),page=i+1))
 # Preserve SI images and their unchanged decoded pixels for visual review.
 si=next(x for x in lines(B/"C/E02/fresh/C-E02-R40-advertised-SI-custody-v1/execution.jsonl") if x["query_id"]=="R40-SI")
 images=[]
 with zipfile.ZipFile(ROOT/si["raw_pointer"]["path"]) as z:
  for n in z.namelist():
   if n.startswith("word/media/"):
    im=Image.open(io.BytesIO(z.read(n)));out=ROOT/transport.RAW/("SI-"+Path(n).stem+".png")
    if out.exists():raise RuntimeError("IMMUTABLE")
    buf=io.BytesIO();im.save(buf,format="PNG");b=buf.getvalue();out.write_bytes(b)
    event(T,"write_binary",path=str(out.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),reason="Decoded unchanged SI embedded image for A6 visual inspection")
    images.append(dict(path=str(out.relative_to(ROOT)),sha256=sha(out),member=n,member_sha256=hashlib.sha256(z.read(n)).hexdigest(),dimensions=list(im.size)))
 put(O/"A6_render_manifest.json",dict(task=T,pages=paths,SI_images=images,raw_pointer=row["raw_pointer"],SI_raw_pointer=si["raw_pointer"],render_only=True,scientific_graphs_approved=False))
 print(json.dumps(dict(original_pages=len(doc),SI_embedded_images=len(images),render_manifest=str(O/"A6_render_manifest.json"))))
if __name__=="__main__":
 import sys
 {"pre":pre,"run":run,"render":render}[sys.argv[1]]()

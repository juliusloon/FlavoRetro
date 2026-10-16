"""R21 A4 independent first body reader, source-focused evidence extraction."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,hashlib,re
from datetime import datetime,timezone
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
def sha(p):return sha_file(ROOT/p)
def txt(el):return " ".join("".join(el.itertext()).split())
def save(p,x):write(T,str(p),json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
 p=R/"A4/source_original_reaction_claims.json"
 if (ROOT/p).exists():raise RuntimeError("IMMUTABLE_A4")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 a=json.loads((ROOT/A3).read_text())
 out=[]
 for x in a["sources"]:
  if x["PMCID"] not in ("PMC12611259","PMC11974848"):continue
  src=Path(x["original_source_path"])
  if sha(src)!=x["original_SHA"]:raise RuntimeError("ORIGINAL_DRIFT")
  tree=ET.fromstring((ROOT/src).read_bytes());body=tree.find("./body")
  if body is None:raise RuntimeError("NO_JATS_BODY")
  paragraphs=body.findall(".//p")
  sel=[]
  for index,node in enumerate(paragraphs,1):
   t=txt(node);l=t.casefold()
   if ("slugt79b-b" in l or "f3ggt" in l or "2″-o-glucosyltransferase" in l or "k-gal-glu" in l) and any(y in l for y in ("kaempferol","udp-","k-gal","2″","glucosyltransferase","enzyme","glycoside")):
    sel.append(dict(anchor="body/p-"+str(index),literal_sha256=hashlib.sha256(t.encode()).hexdigest(),
      source_text=t[:9000],paragraph_length=len(t)))
  figures=[dict(figure_id=f.get("id"),caption=txt(f.find("./caption"))[:7000]) for f in body.findall(".//fig") if f.find("./caption") is not None and any(t in txt(f.find("./caption")).lower() for t in ("glycosyltransferase","glycoside","enzyme","slugt79"))]
  out.append(dict(PMCID=x["PMCID"],DOI=x["DOI"],raw_path=str(src),
    raw_SHA=x["original_SHA"],original_source_claims=sel,figure_captions=figures,
    candidate_site="parent galactoside 2-double-prime O" if x["PMCID"]=="PMC12611259" else "pending independent evidence review",
    independent_of_A5=True,read_only_after_G5=True,
    full_graph_derived=False,formal_chemical_validation=False))
 save(p,dict(task=T,role="A4",at=datetime.now(timezone.utc).isoformat(),
   source_count=len(out),sources=out,A5_file_read=False,source_originals_SHA_bound=True,
   no_build_or_holdout_change=True,not_fresh=True,not_full_structure_complete=True))
 print(json.dumps(dict(A4=2,source_paragraphs=[len(z["original_source_claims"]) for z in out],figure_captions=[len(z["figure_captions"]) for z in out])))
if __name__=="__main__":main()


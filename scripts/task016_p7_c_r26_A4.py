"""C-E02 R26 A4 first independent original-JATS source chemistry reader.
Frozen scope only; evidence locations not full stereo-graph assertion.
"""
import json,hashlib,re,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
G5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
def sha(p):return sha_file(ROOT/p)
def txt(n):return " ".join("".join(n.itertext()).split())
def main():
 dest=R/"A4/first_original_C_reaction_screen.json"
 if (ROOT/dest).exists():raise RuntimeError("OUTPUT_EXISTS")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 a=json.loads((ROOT/R/"A0_pre_read_contract.json").read_text());results=[]
 keys=["c-glycosyl","c-glucosyl","c6","6-c-","6-c glyco","8-c-","isoflavone","puerarin","dendrobium","ugt708s6","udp-glucose","6-position","8-position","chrysin","flavone","in vitro","glucosyltransferase"]
 for x in a["selected"]:
  p=Path(x["source_path"]);assert sha(p)==x["raw_SHA"]
  tree=ET.fromstring((ROOT/p).read_bytes());body=tree.find("./body")
  if body is None:raise RuntimeError("NO_BODY")
  paragraphs=[]
  for i,el in enumerate(body.findall(".//p"),1):
   s=txt(el);low=s.lower()
   present=[t for t in keys if t in low]
   if present and (any(w in low for w in ("enzyme","glycosyl","flavon","ugt","c-glycos","puerarin","in vitro","chrysin","c6","8-c-"))):
    paragraphs.append(dict(location=f"body/p-{i}",paragraph_SHA256=hashlib.sha256(s.encode()).hexdigest(),
     observed_terms=present,source_text=s[:6000],source_length=len(s)))
  figures=[]
  for el in body.findall(".//fig"):
   cp=el.find("./caption")
   if cp is not None:
    s=txt(cp)
    if any(k in s.casefold() for k in ("c-glycos","flavon","ugt","glycosyltransfer","puerarin","safflower")):
     figures.append(dict(id=el.get("id"),caption_SHA256=hashlib.sha256(s.encode()).hexdigest(),caption=s[:3400]))
  results.append(dict(PMCID=x["PMCID"],DOI=x["DOI"],original_path=str(p),original_SHA=x["raw_SHA"],
    total_body_paragraphs=len(body.findall(".//p")),selected_paragraphs=paragraphs,
    selected_figure_captions=figures,independent_A4_first_reader=True,
    source_catalysis_site_not_prejudged=True,full_product_graph_not_from_name=True))
 out=dict(task=T,family="C",epoch_id="C-E02",role="A4_independent_first_source_screener",
   at=datetime.now(timezone.utc).isoformat(),sources=results,source_count=3,
   A5_read=False,source_science_only_after_G5=True,
   candidate_structures_not_guessed=True,zero_auto_fresh=True)
 write(T,str(dest),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(A4_sources=3,hit_paragraphs=[(x["PMCID"],len(x["selected_paragraphs"])) for x in results])))
if __name__=="__main__":main()


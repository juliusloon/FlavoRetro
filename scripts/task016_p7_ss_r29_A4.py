"""SS R29 A4 independent original primary science read for two distinct O2 studies."""
import json,hashlib,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
def sha(p):return sha_file(ROOT/p)
def txt(el):return " ".join("".join(el.itertext()).split())
def main():
 dest=R/"A4/first_independent_original_O2_evidence.json"
 if (ROOT/dest).exists():raise RuntimeError("A4_EXISTS")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 originals=json.loads((ROOT/R/"A3_original_front_verified.json").read_text())["sources"]
 results=[]
 keys=("2″","2''","2′′","2-o","1→2","1 → 2","1->2","glucosyltransferase","fg3","ugt79b","galactoside","udp-glucose","sophoroside","kaempferol")
 for x in originals:
  path=Path(x["raw_source_path"]);assert sha(path)==x["raw_source_SHA"]
  root=ET.fromstring((ROOT/path).read_bytes());body=root.find("./body");assert body is not None
  selection=[]
  for n,el in enumerate(body.findall(".//p"),1):
   s=txt(el);l=s.casefold()
   hits=[t for t in keys if t in l]
   if len(hits)>=2 and any(y in l for y in ("glucosyl", "glycoside", "2″", "1 → 2", "1->2", "transferase")):
    selection.append(dict(anchor=f"body/p-{n}",sha256=hashlib.sha256(s.encode()).hexdigest(),
      terms=hits,text=s[:8000],text_len=len(s)))
  figures=[]
  for fig in body.findall(".//fig"):
   cap=fig.find("./caption")
   if cap is not None:
    s=txt(cap)
    if any(v in s.casefold() for v in ("glucosyltransferase","2″","sophoroside","3-o-glycoside","fg3")):
     figures.append(dict(figure_id=fig.get("id"),caption_SHA=hashlib.sha256(s.encode()).hexdigest(),
      caption=s[:5500]))
  results.append(dict(PMCID=x["PMCID"],source_DOI=x["DOI"],original_SHA=x["raw_source_SHA"],
   source_path=str(path),A4_independent=True,body_paragraphs=len(body.findall(".//p")),
   selected_original_paragraphs=selection,selected_figures=figures,
   explicit_structure_graph_not_yet_verified=True,not_fresh=True))
 out=dict(task=T,role="A4_standalone_primary_source_science",at=datetime.now(timezone.utc).isoformat(),
   independent_of_A5=True,sources=results,source_count=2,no_model_output_read=True)
 write(T,str(dest),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(A4_originals=2,paragraphs=[(x["PMCID"],len(x["selected_original_paragraphs"])) for x in results])))
if __name__=="__main__":main()


"""R21 A5 second independent original study screener; no A4 imports or reads."""
import hashlib,xml.etree.ElementTree as ET,json,re
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R21-tomato-O2-original-science-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R21-tomato-O2-original-science/G5_FRESH_HOLDOUT_ACQUIRE.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
def digest(p):return sha_file(ROOT/p)
def normalize(node):return " ".join("".join(node.itertext()).split())
def main():
 p=R/"A5/independent_original_O2_screen.json"
 if (ROOT/p).exists():raise RuntimeError("A5_ALREADY_WRITTEN")
 assert verify_stage_chain(ROOT/G5,digest(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 refs=json.loads((ROOT/A3).read_text())["sources"];results=[]
 for x in refs:
  if x["PMCID"] not in ("PMC12611259","PMC11974848"):continue
  path=Path(x["original_source_path"]);assert digest(path)==x["original_SHA"]
  r=ET.fromstring((ROOT/path).read_bytes());body=r.find("./body")
  if body is None:raise RuntimeError("NO_ORIGINAL_BODY")
  anchors=[];context=[]
  for i,node in enumerate(body.iter("p"),1):
   literal=normalize(node)
   lower=literal.lower()
   # Independent A5 requiring textual catalytic action and sugar-residue acceptor,
   # not just the name "diglycoside".
   sl="slugt79b-b" in lower or "solyc10g008860" in lower
   donor=("udp-glucose" in lower or "udp-glc" in lower or "udp-glucose" in lower.replace("–","-"))
   site=("2″" in lower or "2''" in lower or "2′′" in lower or "2\\u2033" in lower)
   acceptor=("k-gal" in lower or "kaempferol 3-o-galactoside" in lower)
   catalytic=any(s in lower for s in ("produced","catalyz","glucosyltransferase activity","converts","in vitro","assay"))
   if sl or (site and acceptor):
    anchors.append(dict(anchor=f"body/p-{i}",SHA256=hashlib.sha256(literal.encode()).hexdigest(),
      has_enzyme=sl,has_udp_glc=donor,has_site_2doubleprime=site,
      has_preglycosylated_acceptor=acceptor,has_catalytic_statement=catalytic,
      original_text=literal[:9000]))
   if donor and acceptor and (site or sl) and catalytic:context.append(f"body/p-{i}")
  results.append(dict(PMCID=x["PMCID"],DOI=x["DOI"],raw_path=str(path),
     raw_SHA=x["original_SHA"],screened_body_paragraphs=len(list(body.iter("p"))),
     evidence_anchors=anchors,direct_evidence_paragraphs=context,
     full_stereo_graph_not_encoded=True,
     preprint_cannot_be_independent_closure=True,
     read_A4=False,read_model=False,scope_not_changed=True))
 output=dict(task=T,role="A5_independent",timestamp=datetime.now(timezone.utc).isoformat(),
   results=results,source_count=2,no_A4_input=True,original_SHA_bound=True,
   no_automatic_fresh_or_structure_admission=True)
 write(T,str(p),json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(dict(A5=2,anchors=[len(z["evidence_anchors"]) for z in results],
   direct_text_paragraphs=[len(z["direct_evidence_paragraphs"]) for z in results])))
if __name__=="__main__":main()


"""C-E02 R26 A5 independently read official primary body with site and step flags.

Does not read A4 or source-dispositions. No positive admission from abstract,
name, enzyme family, metabolite association, or C-glycoside occurrence alone.
"""
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import verify_stage_chain,sha_file
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"C/E02/fresh/C-E02-R26-original-science-screen-v1"
G5=B/"C/E02/stages/batches/C-E02-R26-original-science-screen/G5_FRESH_HOLDOUT_ACQUIRE.json"
A3=B/"governance/R20-six-original-front-identity-v1/A3_six_original_front_identity_v1.json"
def sha(p):return sha_file(ROOT/p)
def text(n):return " ".join("".join(n.itertext()).split())
def main():
 dest=R/"A5/second_independent_canonical_site_screen.json"
 if (ROOT/dest).exists():raise RuntimeError("IMMUTABLE")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 selected=[r for r in json.loads((ROOT/A3).read_text())["sources"] if r["family"]=="C"]
 out=[]
 for src in selected:
  path=Path(src["original_source_path"]);assert sha(path)==src["original_SHA"]
  root=ET.fromstring((ROOT/path).read_bytes())
  body=root.find("./body");assert body is not None
  hits=[]
  for pos,p in enumerate(body.iter("p"),1):
   s=text(p);l=s.casefold()
   signals={
    "direct_transfer_assay":any(k in l for k in ("in vitro","enzyme assay","in vitro assays","recombinant","enzymatic reaction","catalytic activity")),
    "literal_C6":any(k in l for k in ("6-c-","6-c glucos","6-c-glycos","c-6","c6","6-position","position 6","6-cglycos")),
    "literal_C8":any(k in l for k in ("8-c-","8-c glycos","8-c-glucos","c-8","c8","8-position","position 8")),
    "C_glycosyl":any(k in l for k in ("c-glycos","c-glucos","c-glycosyl","c-glucosyl")),
    "UDP_donor":any(k in l for k in ("udp-glucose","udp-glc","udp glucose")),
    "flavone":("flavone" in l or "chrysin" in l or "apigenin" in l or "luteolin" in l or "flavones" in l),
    "isoflavone":("isoflavone" in l or "puerarin" in l or "daidzein" in l),
    "aglycone_monomer":("aglycone" in l or "acceptor" in l or "substrate" in l),
    "alternative_C_transformation":any(k in l for k in ("o-to-c","o–c","o- to c-","rearrangement","c-glycosyl flavonoids")),
    "structural_figure":any(k in l for k in ("fig.","figure","scheme","supplementary")),
   }
   if ((signals["C_glycosyl"] or signals["literal_C6"] or signals["literal_C8"]) and
       (signals["direct_transfer_assay"] or signals["UDP_donor"] or signals["flavone"] or signals["isoflavone"] or signals["aglycone_monomer"])):
    hits.append(dict(anchor=f"body/p-{pos}",sha256=hashlib.sha256(s.encode()).hexdigest(),
       flags=signals,original_text=s[:8000],complete_char_count=len(s)))
  out.append(dict(PMCID=src["PMCID"],DOI=src["DOI"],source_SHA=src["original_SHA"],
   source_path=str(path),read_body_only_after_G5=True,body_paragraphs=len(list(body.iter("p"))),
   potentially_relevant_evidence=hits,source_cannot_be_accepted_without_full_reaction_site_structure=True,
   no_A4_input=True,no_model_output_read=True))
 result=dict(task=T,epoch_id="C-E02",family="C",
   role="A5_independent_second_source_reader",
   at=datetime.now(timezone.utc).isoformat(),sources=out,
   original_source_count=3,A4_not_read=True,
   full_product_and_acceptor_graphs_not_guessed=True,
   site_ambiguity_fail_closed=True,scientific_fresh_admitted=0)
 write(T,str(dest),json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(A5_originals=len(out),evidence_anchors=[(x["PMCID"],len(x["potentially_relevant_evidence"])) for x in out])))
if __name__=="__main__":main()


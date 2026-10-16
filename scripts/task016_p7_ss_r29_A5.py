"""SS R29 A5 second independent original science read without A4 input."""
import hashlib,json,xml.etree.ElementTree as ET
from datetime import datetime,timezone
from pathlib import Path
from scripts.operate import ROOT,write
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T="TASK-016-P7";B=Path("outputs/task016-p7/v1")
R=B/"SS/E02/fresh/SS-E02-R29-two-independent-O2-original-studies-v1"
G5=B/"SS/E02/stages/batches/SS-E02-R29-two-independent-O2-original-studies/G5_FRESH_HOLDOUT_ACQUIRE.json"
def sha(p):return sha_file(ROOT/p)
def text(n):return " ".join("".join(n.itertext()).split())
def main():
 dest=R/"A5/second_independent_catalytic_site_screen.json"
 if (ROOT/dest).exists():raise RuntimeError("A5_EXISTS")
 assert verify_stage_chain(ROOT/G5,sha(G5))["stage"]=="G5_FRESH_HOLDOUT_ACQUIRE"
 refs=json.loads((ROOT/R/"A3_original_front_verified.json").read_text())["sources"]
 results=[]
 for ref in refs:
  path=Path(ref["raw_source_path"]);assert sha(path)==ref["raw_source_SHA"]
  tree=ET.fromstring((ROOT/path).read_bytes());body=tree.find("./body");assert body is not None
  evidence=[]
  for i,p in enumerate(body.iter("p"),1):
   text_value=text(p);v=text_value.casefold()
   flags=dict(
    donor_UDPglc=any(w in v for w in ("udp-glucose","udp–glucose","udp-glc","udp‐glucose")),
    pre_glycosylated_flavonol=any(w in v for w in ("3-o-glucoside","3‐o‐glucoside","3-o-galactoside","3-o-glycoside","3-o-glycosyl")),
    interglycosidic_2prime=any(w in v for w in ("2″","2′′","2''","1 → 2","1→2","1->2","1 → 2")),
    original_enzymatic_assay=any(w in v for w in ("recombinant","enzyme activity","enzyme assay","incubated","in vitro","in-vitro","enzyme assays","transferase activity")),
    gene_enzyme_explicit=any(w in v for w in ("fg3","ugt79b","ugt79b6","glucosyltransferase","glycosyltransferase")),
    flavonol_explicit=any(w in v for w in ("flavonol","quercetin","kaempferol","sophoroside")),
   )
   if (flags["gene_enzyme_explicit"] and (flags["interglycosidic_2prime"] or flags["pre_glycosylated_flavonol"]) and flags["flavonol_explicit"]) or all((flags["donor_UDPglc"],flags["interglycosidic_2prime"],flags["pre_glycosylated_flavonol"])):
    evidence.append(dict(anchor=f"body/p-{i}",literal_sha256=hashlib.sha256(text_value.encode()).hexdigest(),
      flags=flags,source_text=text_value[:9000],paragraph_length=len(text_value)))
  results.append(dict(PMCID=ref["PMCID"],DOI=ref["DOI"],raw_SHA=ref["raw_source_SHA"],
    raw_path=str(path),body_paragraph_count=len(list(body.iter("p"))),
    original_candidate_reaction_evidence=evidence,no_A4_read=True,
    full_graph_structure_not_auto_generated=True))
 out=dict(task=T,role="A5_independent_second_source_reader",
  at=datetime.now(timezone.utc).isoformat(),results=results,original_count=2,
  not_enough_by_title_or_abstract=True,source_science_only_after_frozen_G5=True,
  no_fresh_admission=True,A4_source_output_not_read=True)
 write(T,str(dest),json.dumps(out,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
 print(json.dumps(dict(A5_originals=2,evidence_paragraphs=[(r["PMCID"],len(r["original_candidate_reaction_evidence"])) for r in results])))
if __name__=="__main__":main()


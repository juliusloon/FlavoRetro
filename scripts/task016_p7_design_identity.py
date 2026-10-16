"""Independent identity verification of original JATS and archived official metadata."""
import json,sys
from pathlib import Path
from scripts.task016_p7_identity_harness import parse_jats,verify_identity
from scripts.task016_p7_orchestrate import sha_file,role_manifest,save_json
from scripts.operate import write
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"outputs/task016-p7/v1"
def european(path):
    x=json.loads(path.read_text())
    rs=x["resultList"]["result"]
    if len(rs)!=1: raise RuntimeError("ambiguous identity result")
    v=rs[0];j=v.get("journalInfo") or {}; journal=j.get("journal") or {}
    # Europe PMC pageInfo holds an e-location for these sources, preserve its axis.
    return dict(provider="Europe PMC",authoritative=True,metadata=dict(pmcid=v.get("pmcid"),pmid=v.get("id") if v.get("source")=="MED" else None,doi=v.get("doi"),title=v.get("title"),journal=journal.get("title"),year=j.get("yearOfPublication") or v.get("pubYear"),volume=j.get("volume"),article_number=v.get("pageInfo"),publisher=None,pages=None),evidence_pointer=dict(path=str(path.relative_to(ROOT)),sha256=sha_file(path)))
def main():
    inputs=[json.loads(s) for s in (OUT/"C/E01/design_source_identity_inputs.jsonl").read_text().splitlines()]
    results=[]
    for r in inputs:
        x=ROOT/r["xml"]["path"]; xm=parse_jats(x,dict(path=str(x.relative_to(ROOT)),sha256=sha_file(x)))
        em=european(ROOT/r["europepmc"]["path"])
        # pageInfo can be a conventional page range; route it by the JATS field.
        if xm["metadata"].get("pages") and not xm["metadata"].get("article_number"):
            em["metadata"]["pages"]=em["metadata"].pop("article_number")
        claim={k:r.get(k) for k in ["pmcid","doi","title","journal"]}
        q=verify_identity(claim,[xm,em]);q["pmcid"]=r["pmcid"];q["scope_role"]="design_build_only"
        results.append(q)
    write("TASK-016-P7","outputs/task016-p7/v1/C/E01/source_identity_verification.jsonl","".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in results))
    save_json(OUT/"C/E01/role_A3_identity_manifest.json",role_manifest("A3 Source Identity Verifier",inputs=[OUT/"C/E01/design_source_identity_inputs.jsonl"],outputs=[OUT/"C/E01/source_identity_verification.jsonl"],epoch_id="C-E01",counts=dict(processed=len(results),passed=sum(r["source_identity_verified"] for r in results),pending=sum(not r["source_identity_verified"] for r in results),rejected=0),pointers=[p for r in results for p in r["authoritative_evidence_pointers"]],errors=[]))
    print([dict(pmcid=r["pmcid"],verified=r["source_identity_verified"],conflicts=r["conflict_fields"],missing=r["missing_fields"]) for r in results])
if __name__=="__main__":main()

"""Independent source identity of frozen fresh original-source intake; no chemistry."""
import argparse,json
from pathlib import Path
from scripts.operate import write
from scripts.task016_p7_identity_harness import parse_jats,verify_identity
from scripts.task016_p7_orchestrate import sha_file,save_json,role_manifest
R=Path(__file__).resolve().parents[1]
def main(intake,output,family="C"):
    intake=R/intake;output=R/output
    if output.exists():raise RuntimeError("preserve original identity verification; use new version")
    source=json.loads(intake.read_text());result=[];raw_inputs=[intake]
    for r in source:
        if not r.get("xml") or r["xml"].get("status")!="available":continue
        pointer={k:r["xml"][k] for k in ["path","sha256"]};path=R/pointer["path"]
        if sha_file(path)!=pointer["sha256"]:raise RuntimeError("fresh original XML SHA drift")
        jats=parse_jats(path,pointer);authorities=[jats];raw_inputs.append(path)
        if r.get("metadata") and r["metadata"].get("status")=="available":
            p={k:r["metadata"][k] for k in ["path","sha256"]};raw=R/p["path"]
            if sha_file(raw)!=p["sha256"]:raise RuntimeError("official metadata SHA drift")
            m=json.loads(raw.read_text());authorities.append(dict(provider="PMC authoritative metadata",authoritative=True,metadata={k:m.get(k) for k in ["pmcid","pmid","doi","title"]},evidence_pointer=p));raw_inputs.append(raw)
        hint=r.get("source_hint",{})
        claim={k:hint.get(k) or r.get(k) for k in ["pmcid","pmid","doi","title"]}
        v=verify_identity(claim,authorities)
        result.append(dict(v,pmcid=r["pmcid"],family=family,epoch_id=family+"-E01",source_role="fresh_original_pending_chemical_admission",intake_sha256=sha_file(intake),source_article_metadata=jats["metadata"]))
    output.parent.mkdir(parents=True,exist_ok=True)
    write("TASK-016-P7",str(output.relative_to(R)),"".join(json.dumps(x,ensure_ascii=False,sort_keys=True)+"\n" for x in result))
    save_json(output.with_name("role_A3_fresh_identity_manifest.json"),role_manifest("A3 Source Identity Verifier",family+"-E01",raw_inputs,[output],dict(processed=len(result),passed=sum(x["source_identity_verified"] for x in result),pending=sum(not x["source_identity_verified"] for x in result),rejected=0),pointers=[p for x in result for p in x["authoritative_evidence_pointers"]],errors=[dict(pmcid=x["pmcid"],conflict_fields=x["conflict_fields"]) for x in result if not x["source_identity_verified"]]),immutable=True)
    print([dict(pmcid=x["pmcid"],verified=x["source_identity_verified"],conflicts=x["conflict_fields"],missing=x["missing_fields"]) for x in result])
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("intake");p.add_argument("output");p.add_argument("--family",choices=["C","SS"],default="C");a=p.parse_args();main(a.intake,a.output,a.family)

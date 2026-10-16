"""TASK-016-P7 SS-E02 R5 A3 original-front bibliographic identity, zero chemistry read."""
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET
import hashlib, json, re, sys
from scripts.operate import ROOT, write
from scripts.task016_p7_ss_sources import require_acquisition_phase

TASK="TASK-016-P7"; BASE=Path("outputs/task016-p7/v1")
R5=BASE/"SS/E02/fresh/SS-E02-R5-original-acquisition-v1"
R4=BASE/"SS/E02/fresh/SS-E02-R4-bibliographic-resolution-v1"
OUT=BASE/"SS/E02/fresh/SS-E02-R6-A3-original-identity-v1"
FIX=BASE/"governance/SS_E02_R5_G5_binding_repair_v1/validation.json"
V17=BASE/"report_snapshots/progress-v17.json"
G4=BASE/"SS/E02/stages/G4_SCOPE_FREEZE.json"
G5=BASE/"SS/E02/stages/batches/SS-E02-R4-metadata/G5_FRESH_HOLDOUT_ACQUIRE.json"

def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(x) for x in (ROOT/p).read_text().splitlines() if x.strip()]
def save(name,obj):write(TASK,str(OUT/name),json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
def canon(s):return re.sub(r"[\W_]+","",str(s or "").casefold(),flags=re.UNICODE)
def txt(e):return " ".join("".join(e.itertext()).split()) if e is not None else ""
def local(tag):return tag.rsplit("}",1)[-1]
def front_only(path):
    """Read XML only through end of journal front; do not visit body/figures."""
    front=None
    with (ROOT/path).open("rb") as stream:
        for _,element in ET.iterparse(stream,events=("end",)):
            if local(element.tag)=="front":
                front=element;break
    if front is None:raise ValueError("MISSING_ORIGINAL_FRONT")
    ids={}
    journal={}
    titles=[]
    dates=[]
    for e in front.iter():
        tag=local(e.tag)
        if tag=="article-id":ids.setdefault(e.get("pub-id-type","unknown"),[]).append(txt(e))
        elif tag=="article-title":titles.append(txt(e))
        elif tag in {"journal-title","publisher-name","volume","issue","fpage","lpage","elocation-id"}:
            journal.setdefault(tag,[]).append(txt(e))
        elif tag=="pub-date":
            dates.append({"pub_type":e.get("pub-type"),
                          "year":[txt(x) for x in e if local(x.tag)=="year"],
                          "month":[txt(x) for x in e if local(x.tag)=="month"],
                          "day":[txt(x) for x in e if local(x.tag)=="day"]})
    return {"ids":ids,"titles":titles,"journal":journal,"publication_dates":dates,
            "stopped_at_end_of_front":True,"chemical_body_or_figures_read":False}

def main():
    if (ROOT/OUT).exists():raise RuntimeError("IMMUTABLE_OUTPUT_EXISTS")
    sel=load(R5/"selection_dispositions.json")["selected_sources"]
    execution=rows(R5/"original_query_execution.jsonl")
    official=rows(R4/"authoritative_bibliographic_records.jsonl")
    inp=[R5/"role_A2_raw_only_manifest.json",R5/"raw_only_intake_manifest.json",
      R5/"original_query_execution.jsonl",R5/"selection_dispositions.json",
      R4/"authoritative_bibliographic_records.jsonl",V17,FIX,G4,G5]
    fixed_inputs={str(p):sha(p) for p in inp}
    fixed_raw={}
    for r in execution:
        if r["front_projection"] is not None:
            path=Path(r["raw_pointer"]["path"])
            if sha(path)!=r["raw_pointer"]["sha256"]:
                raise RuntimeError("ORIGINAL_SHA_DRIFT")
            fixed_raw[str(path)]=sha(path)
    gate=require_acquisition_phase("fresh",epoch_id="SS-E02",
        scope_id="p7-SS-Petunia-GlcGal-O2-betaGlc-proposal-v1")
    save("preflight.json",{"task":TASK,"role":"A3","timestamp":now(),
       "input_SHA256":fixed_inputs,"original_XML_SHA256":fixed_raw,
       "registered_before_new_front_read":True,
       "G4_stage_sha":gate["G4_manifest_sha256"],"G5_stage_sha":gate["G5_manifest_sha256"],
       "allowed_read":"bibliography front only; zero abstract/body/figure/SI chemistry",
       "selected_sources":len(sel),"fresh_admitted":0})
    results=[];passn=0
    for s in sel:
        sid=s["source_id"];doi=s["DOI"].lower()
        rs=[r for r in official if "doi:"+doi in r["normalized_identifier_tokens"]]
        routes={r["route"] for r in rs}
        originals=[r for r in execution if r["source_id"]==sid and r["front_projection"] is not None and
                   r["container_validity"]=="XML_front_projected_only"]
        out={"source_id":sid,"DOI":doi,"source_titles":s["titles"],
             "R4_records":[{"record_id":r["record_id"],"route":r["route"],"raw_pointer":r["raw_pointer"]} for r in rs],
             "publication_identity_verified":False,"full_scientific_source_eligible":False,
             "reaction_eligible":False,"scope_applicable":None,"fresh_eligible":False,
             "human_reviewed":False,"abstract_or_chemical_body_read":False}
        if len(originals)!=1 or len(routes)<2:
            out.update(status="pending_independent_original_or_two_authoritative_routes",
                original_objects_with_front=len(originals),independent_official_routes=len(routes))
            results.append(out);continue
        r=originals[0];p=Path(r["raw_pointer"]["path"])
        if sha(p)!=r["raw_pointer"]["sha256"]:raise RuntimeError("ORIGINAL_CHANGED_AFTER_FREEZE")
        f=front_only(p)
        med=next((x["bibliographic_metadata"] for x in rs if x["route"].startswith("EuropePMC")),None)
        pm=next((x["bibliographic_metadata"] for x in rs if x["route"].startswith("PubMed_ESummary")),None)
        if not med or not pm:
            out.update(status="pending_missing_EuropePMC_or_PubMed",front=f);results.append(out);continue
        expected=s["identifier_tokens"];r4ids=set(rs[0]["normalized_identifier_tokens"])
        doi_ok=(doi in [x.lower() for x in f["ids"].get("doi",[])])
        pmcid_ok=(sid in f["ids"].get("pmcid",[])) and "article:"+sid in r4ids
        pmid=next((t[5:] for t in expected if t.startswith("pmid:")),None)
        pmid_ok=bool(pmid) and pmid in f["ids"].get("pmid",[]) and "pmid:"+pmid in r4ids and str(pm.get("uid"))==pmid
        titles_equal=len(f["titles"])==1 and canon(f["titles"][0])==canon(med.get("title"))==canon(pm.get("title"))
        journals_equal=any(canon(j)==canon(pm.get("fulljournalname")) for j in f["journal"].get("journal-title",[]))
        years={y for x in f["publication_dates"] for y in x["year"]}
        years_equal=bool(years) and all(y==str(med.get("pubYear")) for y in years)
        vol_equal=str(pm.get("volume")) in f["journal"].get("volume",[]) and str(med.get("journalVolume")) in f["journal"].get("volume",[])
        issue=f["journal"].get("issue",[])
        issue_equal=not issue or (str(pm.get("issue")) in issue and str(med.get("issue")) in issue)
        page=f["journal"].get("elocation-id",[None])[0]
        if f["journal"].get("fpage") and f["journal"].get("lpage"):
            page=f["journal"]["fpage"][0]+"-"+f["journal"]["lpage"][0]
        pages_equal=bool(page) and page==str(pm.get("pages"))==str(med.get("pageInfo"))
        checks={"DOI":doi_ok,"PMCID":pmcid_ok,"PMID":pmid_ok,
                "title_EuropePMC_PubMed_original":titles_equal,
                "journal_full_title_original_PubMed":journals_equal,
                "year_original_EuropePMC":years_equal,
                "volume_3way":vol_equal,"issue_when_original_present":issue_equal,
                "pages_or_article_number_3way":pages_equal,
                "R4_bibliographic_original_records_distinct_routes":len(routes)>=2}
        passed=all(checks.values())
        out.update(status="verified_original_front_vs_two_official_routes" if passed else "unresolved_bibliographic_conflict",
                   publication_identity_verified=passed,checks=checks,front=f,
                   source_raw_path=str(p),source_raw_sha=sha(p),
                   raw_figure_and_body_unread=True,
                   metadata_publication_year_variants_pending=s["publication_year_variants_pending"],
                   original_pdf_not_independently_reparsed=True)
        if passed:passn+=1
        results.append(out)
    assert len(results)==len(sel)==6
    manifest={"task":TASK,"epoch_id":"SS-E02","role":"A3","approval":"agent_delegated",
      "timestamp":now(),"input_preflight_sha":sha(OUT/"preflight.json"),
      "original_independent_front_verified":passn,"pending":len(results)-passn,
      "counts":{"processed":6,"passed":passn,"rejected":0,"pending":6-passn},
      "results":results,"new_HTTP":0,"new_MCTS":0,"human_reviewed":False,
      "fresh_admitted":0,"scientific_body_figures_read":False,
      "no_new_G6_stage":True,"no_chemical_source_eligibility_claim":True}
    save("A3_original_identity_results.json",manifest)
    save("role_A3_manifest.json",{"task":TASK,"role":"A3",
      "input_SHA256":sha(OUT/"preflight.json"),"outputs_SHA256":{"A3_original_identity_results.json":sha(OUT/"A3_original_identity_results.json")},
      "counts":manifest["counts"],"source_evidence_pointers":list(fixed_raw),
      "read_holdout_chemical_content":False,"read_model_outcome":False,
      "unprocessed":[s["source_id"] for s in results if not s["publication_identity_verified"]],
      "no_G6_or_fresh_scientific_promotion":True})
    print(json.dumps({"A3_original_front_verified":passn,"pending":6-passn,
          "new_HTTP":0,"fresh":0},ensure_ascii=False))
if __name__=="__main__":main()

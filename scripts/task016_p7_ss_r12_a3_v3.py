"""SS-E02 R12: A3 front-only identity for two R11 newly acquired original XMLs.
No body, abstract, figure, SI or reaction content is inspected here.
"""
import json, hashlib, re
from pathlib import Path
from xml.etree import ElementTree as ET
from datetime import datetime, timezone
from scripts.operate import ROOT, write
TASK="TASK-016-P7"
BASE=Path("outputs/task016-p7/v1")
R11=BASE/"SS/E02/fresh/SS-E02-R11-original-acquisition-v1"
R12=BASE/"SS/E02/fresh/SS-E02-R12-original-science-review-v3"
R10=BASE/"SS/E02/fresh/SS-E02-R10-new-source-discovery-v1"
SOURCES={"PMC5444469":("10.1093/jxb/erw420","28204516","2017"),"PMC6813240":("10.3389/fpls.2019.01330","31681396","2019")}
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
def rows(p):return [json.loads(l) for l in (ROOT/p).read_text().splitlines() if l.strip()]
def save(path,obj):write(TASK,str(path),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def text(el):return " ".join("".join(el.itertext()).split())
def local(el):return el.tag.rsplit("}",1)[-1]
def canon(s):return re.sub(r"[^a-z0-9]+","",re.sub(r"<[^>]*>","",str(s).casefold()))
def front_only(p):
    f=None
    with (ROOT/p).open("rb") as stream:
        for _,el in ET.iterparse(stream,events=("end",)):
            if local(el)=="front":f=el;break
    if f is None:raise RuntimeError("FRONT_NOT_FOUND")
    ids={}
    for el in f.iter():
        if local(el)=="article-id":ids.setdefault(el.get("pub-id-type",""),[]).append(text(el))
    val=lambda tag:[text(el) for el in f.iter() if local(el)==tag]
    return dict(ids=ids,titles=val("article-title"),journals=val("journal-title"),
      publishers=val("publisher-name"),years=val("year"),volume=val("volume"),issue=val("issue"),
      fpage=val("fpage"),lpage=val("lpage"),no_body_or_figures_read=True)
def main():
    if (ROOT/R12).exists():raise RuntimeError("IMMUTABLE_R12_EXISTS")
    original=[r for r in rows(R11/"http_ledger.jsonl") if r.get("kind")=="article_version" and r.get("source_id") in SOURCES]
    discovery=[r for r in rows(R10/"discovery_metadata_records.jsonl") if r.get("discovery_class")=="identifier_resolution"]
    input_paths=[R11/"http_ledger.jsonl",R11/"original_API_query_plan.json",R11/"precontract.json",
       R10/"discovery_metadata_records.jsonl",BASE/"SS/E02/scope_manifest.json",
       BASE/"SS/E02/stages/G4_SCOPE_FREEZE.json"]
    pre=dict(task=TASK,role="A3",time=datetime.now(timezone.utc).isoformat(),input_SHA={str(p):sha(p) for p in input_paths},
      source_ids=list(SOURCES),originals={r["source_id"]:dict(path=r["path"],SHA=r["sha256"],bytes=r["bytes"]) for r in original if r.get("status_code")==200},
      allowed_read="only XML front/end; no scientific body, abstracts, captions or SI",scope_changed=False,
      human_reviewed=False,fresh_admitted=0)
    save(R12/"A3_pre_execution.json",pre)
    results=[]
    for sid,(doi,pmid,year) in SOURCES.items():
        candidates=[r for r in original if r.get("source_id")==sid and r.get("status_code")==200 and r.get("status")=="available"]
        refs=[r for r in discovery if {"article:"+sid,"doi:"+doi,"pmid:"+pmid}.issubset(set(r.get("identifier_tokens",[])))]
        if len(candidates)!=1 or len(refs)<1:raise RuntimeError("IDENTIFIER_ROUTE_NOT_VERIFIED_"+sid)
        r=candidates[0];p=Path(r["path"])
        if sha(p)!=r["sha256"] or (ROOT/p).stat().st_size!=r["bytes"]:raise RuntimeError("RAW_SHA_CHANGED_"+sid)
        f=front_only(p)
        checks={
          "PMCID": sid in f["ids"].get("pmcid",[]),
          "PMID":pmid in f["ids"].get("pmid",[]),
          "DOI":doi in f["ids"].get("doi",[]),
          "year":year in f["years"],
          "title_matches_existing_official_metadata":any(canon(a) and canon(a)==canon(b) for a in f["titles"] for x in refs for b in ([x.get("bibliographic_metadata",{}).get("title","")] if isinstance(x.get("bibliographic_metadata",{}).get("title",""),str) else x.get("bibliographic_metadata",{}).get("title",[]))),
          "journal_exists":bool(f["journals"]), "pages_or_article_number":bool(f["fpage"] or f["lpage"]),
          "original_raw_SHA":sha(p)==r["sha256"],"no_scientific_read":f["no_body_or_figures_read"]}
        if not all(checks.values()):raise RuntimeError("IDENTITY_CONFLICT_"+sid+json.dumps(checks))
        results.append(dict(source_id=sid,doi=doi,pmid=pmid,year=year,status="original_publication_identity_verified_front_only",
          checks=checks,front=f,original=dict(path=str(p),sha256=r["sha256"],bytes=r["bytes"]),
          authoritative_metadata_pointers=[dict(record_id=x["record_id"],raw=x["source_pointer"].get("raw_pointer", x["source_pointer"])) for x in refs],
          source_reaction_qualified=False,source_historical_exposure_status="unresolved_requires_full_alias_graph_closure",
          source_science_read=False,fresh_admitted=0))
    save(R12/"A3_front_identity.json",dict(task=TASK,role="A3",time=datetime.now(timezone.utc).isoformat(),
       inputs_SHA={str(p):sha(p) for p in input_paths},results=results,
       counts=dict(processed=2,publication_identity_passed=2,scientific_source_qualified=0,fresh=0),
       human_reviewed=False))
    print(json.dumps(dict(original_A3_pass=2,raw_paths=[x["original"]["path"] for x in results],fresh=0)))
if __name__=="__main__":main()


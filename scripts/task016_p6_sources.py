"""Bounded P6 T1 source discovery and metadata verification before content use.

Europe PMC and Crossref are queried directly because the academic-search MCP is
not mounted. All successful, failed and reused HTTP objects retain their costs.
"""
import json
import html
import re
import sys
import threading
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.task016_p6_common import *
LOCK=threading.Lock()
RAW=ROOT/"data/raw/task016-p6/2026-10-07"
B="https://pmc-oa-opendata.s3.amazonaws.com/"
QUERIES=[
  '("rhamnosyltransferase" OR "rhamnosylation") AND (neohesperidin OR naringin OR "flavonoid glucoside") AND OPEN_ACCESS:Y',
  '("2-O-rhamnosyltransferase" OR "1,2RhaT" OR "2′′-O-rhamnosyl") AND OPEN_ACCESS:Y',
  '("glycoside-specific" OR "glycosyl-glycosyltransferase") AND (flavonoid OR rhamnose) AND OPEN_ACCESS:Y',
  '("apiosyltransferase" OR "apiose") AND (flavonoid OR glycoside) AND OPEN_ACCESS:Y',
  '("glycosyltransferase") AND ("astragalin" OR "polyphyllin") AND OPEN_ACCESS:Y',
  '("rhamnosyltransferase") AND ("substrate specificity" OR "substrate scope" OR "characterization") AND OPEN_ACCESS:Y',
  '("TcCGT" OR "C-glycosylflavonols") AND OPEN_ACCESS:Y',
  '("C-glycosylation") AND (isorhamnetin OR tamarixetin OR myricetin) AND OPEN_ACCESS:Y',
]

def history():
    return rows(OUT/"acquisition_attempts.jsonl") if (OUT/"acquisition_attempts.jsonl").exists() else []

def append(name,record):
    p=OUT/name; old=p.read_text() if p.exists() else ""
    write(TASK,str(p.relative_to(ROOT)),old+json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n")

def get(url,role="metadata",limit=16*1024**2):
    with LOCK:
        old=[r for r in history() if r["url"]==url]
        if old:
            return old[-1]
        n=len(history()); cap=load("approval.json")["budgets"]
        if n>=cap["source_HTTP_attempts"]: raise RuntimeError("HTTP ceiling")
        entry=dict(url=url,role=role,status="reserved",bytes=0,index=n+1)
        append("acquisition_attempts.jsonl",entry)
    data=b""; status=None; error=None
    try:
        with urlopen(Request(url,headers={"User-Agent":"FlavoRetro-P6/0.1"}),timeout=20) as response:
            status=response.status; data=response.read(limit+1)
            if len(data)>limit:raise ValueError("per-file ceiling")
    except HTTPError as exc:
        status=exc.code; error=str(exc); data=exc.read(min(limit,1024**2))
    except Exception as exc:
        error=type(exc).__name__+": "+str(exc)
    path=RAW/(content_sha(url)+"."+role)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise RuntimeError("immutable raw snapshot already exists")
    path.write_bytes(data); path.chmod(0o444)
    result=dict(entry,status="available" if status==200 and error is None else "unavailable",status_code=status,error=error,
                bytes=len(data),path=str(path.relative_to(ROOT)),sha256=sha(path))
    with LOCK:
        values=history(); values[n]=result
        save_rows("acquisition_attempts.jsonl",values)
        event(TASK,"source_http",**result)
        if sum(r["bytes"] for r in values)>cap["source_bytes"]:raise RuntimeError("byte ceiling")
    return result

def read_json(result):
    if result["status"]!="available":return None
    try:return json.loads((ROOT/result["path"]).read_text())
    except ValueError:return None

def discovery():
    save("query_plan.json",dict(queries=QUERIES,sources=["EuropePMC","Crossref"],purpose="independent O2 build closure or complete SS holdout; C evidence completion",human_reviewed=False))
    urls=[("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urlencode(dict(query=q,format="json",resultType="core",pageSize=100)),"discovery") for q in QUERIES]
    urls.append(("https://api.crossref.org/works?"+urlencode({"query.bibliographic":"flavonoid glucoside 2 O rhamnosyltransferase substrate scope", "rows":30}),"crossref"))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda t:get(*t),urls))
    records={}; ledger=[]
    for q,r in zip(QUERIES+["Crossref: flavonoid glucoside 2 O rhamnosyltransferase"],results):
        d=read_json(r)
        ledger.append(dict(query=q,result=r,hit_count=d.get("hitCount") if d and "hitCount" in d else None))
        if not d:continue
        for rec in d.get("resultList",{}).get("result",[]):
            if rec.get("pmcid"):
                records[rec["pmcid"]]=rec
    save("query_ledger.json",ledger);save("discovery_records.json",records)
    print(json.dumps(dict(queries=len(results),successful=sum(r["status"]=="available" for r in results),pmcid_records=len(records)),ensure_ascii=False))

def metadata_and_article(pid,known=None):
    # Official article metadata is compared with Europe PMC before full-text use.
    meta_result=get(B+pid+".1/"+pid+".1.json")
    meta=read_json(meta_result)
    ep_result=get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urlencode(dict(query="EXT_ID:"+pid+" AND SRC:PMC",format="json",resultType="core",pageSize=2)))
    ep=read_json(ep_result); matches=ep.get("resultList",{}).get("result",[]) if ep else []
    if not matches:
        ep_result=get("https://www.ebi.ac.uk/europepmc/webservices/rest/search?"+urlencode(dict(query="PMCID:"+pid,format="json",resultType="core",pageSize=2)))
        ep=read_json(ep_result);matches=ep.get("resultList",{}).get("result",[]) if ep else []
    result=dict(pmcid=pid,meta=meta_result,europepmc=ep_result,evidence_eligible=False,status="identity_unverified")
    if meta is None or not matches:
        return result
    identity=matches[0]
    if identity.get("pmcid")!=pid:
        return result
    # Title and DOI are checked on the XML front matter, retrieved from the official metadata URL.
    if str(meta.get("license_code","")).startswith("CC") and not meta.get("is_retracted"):
        result["license"]=meta.get("license_code")
    else:
        result["status"]="license_or_retraction_pending";return result
    if known and known.get("xml") and sha(ROOT/known["xml"]["path"])==known["xml"]["sha256"]:
        xml=known["xml"];xml=dict(xml,status="available",role="fullTextXML",reused=True)
        append("reused_files.jsonl",xml)
    else:
        url=meta.get("xml_url","").replace("s3://pmc-oa-opendata/",B)
        xml=get(url,"fullTextXML",64*1024**2) if url else dict(status="unavailable")
    result["xml"]=xml
    if xml["status"]!="available":return result
    try:
        root=ET.parse(ROOT/xml["path"]).getroot()
    except ET.ParseError:return result
    info=root.find(".//article-meta")
    title=" ".join("".join(info.find(".//article-title").itertext()).split())
    ids={e.get("pub-id-type"):e.text for e in info.findall("article-id")}
    journal=root.findtext(".//journal-title")
    normalize=lambda s:re.sub(r"[^a-z0-9]","",s.lower())
    ep_title=re.sub(r"<[^>]+>","",html.unescape(identity.get("title", "")))
    ep_doi=identity.get("doi","").lower()
    xml_issns={z.text.replace("-", "") for z in root.findall(".//journal-meta/issn") if z.text}
    ep_journal=identity.get("journalInfo",{}).get("journal",{})
    ep_issns={str(ep_journal.get(k, "")).replace("-", "") for k in ("issn", "essn") if ep_journal.get(k)}
    journal_match=normalize(journal)==normalize(ep_journal.get("title", "")) or bool(xml_issns & ep_issns)
    result["journal_identity_check"] = dict(xml_issns=sorted(xml_issns),europepmc_issns=sorted(ep_issns),matched=journal_match)
    ok=ids.get("pmc",ids.get("pmcid","")).removeprefix("PMC")==pid.removeprefix("PMC") and normalize(title)==normalize(ep_title) and ids.get("doi","").lower()==ep_doi and bool(journal) and journal_match
    result.update(title=title,doi=ids.get("doi"),journal=journal,publication_metadata=identity.get("journalInfo"),evidence_eligible=ok,status="verified" if ok else "identity_mismatch")
    result["media_urls"]=meta.get("media_urls",[]) if ok else []
    return result

def verify_selected():
    inherited=load("inherited_source_bindings.json")
    discovery_records=load("discovery_records.json") if (OUT/"discovery_records.json").exists() else {}
    chosen=list(inherited)
    if "PMC11053098" not in chosen:chosen.append("PMC11053098")
    # Only targeted enzymatic-primary-study titles; all remaining hints are retained.
    for pid,r in discovery_records.items():
        title=re.sub(r"<[^>]+>","",r.get("title","")).lower()
        if ("rhamnosyltransferase" in title or "apiosyltransferase" in title or "glycoside-specific" in title or "apiin" in title or "triglycosides" in title) and pid not in chosen:
            chosen.append(pid)
    chosen=chosen[:30]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda pid:metadata_and_article(pid,inherited.get(pid)),chosen))
    save("source_identity_checks.json",results)
    save("article_acquisition_manifest.json",dict(articles=results,selection_rule="frozen inherited panel originals plus targeted primary enzymatic study titles",not_source_exhaustion=True))
    print(json.dumps([dict(pmcid=r["pmcid"],status=r["status"],title=r.get("title")) for r in results],ensure_ascii=False,indent=2))
if __name__=="__main__":
    if sys.argv[1]=="discover":discovery()
    elif sys.argv[1]=="verify":verify_selected()

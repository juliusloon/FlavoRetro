"""Documented public file endpoint; do not automatically repeat exhausted redirects."""
import json, urllib.request, urllib.error, hashlib
from scripts.task016_p7_c_sources import ROOT,OUT,RAW,rows,save,append,now,sha,raw_manifest,require_fresh_scope,get
from scripts.operate import event
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
u="https://api.figshare.com/v2/file/download/43957078";require_fresh_scope();rr=rows(OUT/"http_ledger.jsonl")
if any(x["url"]==u for x in rr):raise RuntimeError("public endpoint already attempted")
if len(rr)>=2500 or sum(x["bytes"] for x in rr)>=2*1024**3 or sum(x["kind"]=="attachment" for x in rr)>=200:raise RuntimeError("C budget")
aid=f"C-HTTP-{len(rr)+1:05d}";started=now();append("acquisition_plan.jsonl",dict(attempt_id=aid,url=u,kind="attachment",reason="official documented unauthenticated Public File Download; no automatic redirect into exhausted ndownloader",phase="fresh",registered_at=started,limit_bytes=80*1024**2,follow_redirects=False))
data=b"";code=None;error=None;headers={}
try:
 with urllib.request.build_opener(NoRedirect()).open(urllib.request.Request(u,headers={"User-Agent":"FlavoRetro-TASK016P7/1.0 public research"}),timeout=30) as r:
  code=r.status;headers=dict(r.headers);data=r.read(80*1024**2+1)
 if len(data)>80*1024**2:raise RuntimeError("OBJECT_LIMIT")
except urllib.error.HTTPError as e:code=e.code;headers=dict(e.headers);data=e.read(1024**2);error=str(e)
except Exception as e:error=type(e).__name__+": "+str(e)
p=RAW/(hashlib.sha256(u.encode()).hexdigest()+".attempt-1.attachment")
if p.exists():raise RuntimeError("immutable path exists")
p.write_bytes(data);p.chmod(0o444)
r=dict(attempt_id=aid,url=u,kind="attachment",phase="fresh",reason="official documented public download; no automatic redirect",status="available" if code==200 and error is None else "redirect_not_followed" if code in (301,302,303,307,308) else "failed",status_code=code,error=error,bytes=len(data),path=str(p.relative_to(ROOT)),sha256=sha(p),license="CC BY-NC 4.0",redistribution="local_only_pending_or_source_license",started_at=started,finished_at=now(),recovery_chain=False,headers=headers,follow_redirects=False)
append("http_ledger.jsonl",r);event("TASK-016-P7","source_http",**r);raw_manifest();save("E01/fresh/alternate/acs_figshare_public_download_result.json",r)
print(json.dumps(dict(status=r["status"],status_code=code,path=r["path"],sha256=r["sha256"],bytes=r["bytes"],location_present=bool(headers.get("Location")))))

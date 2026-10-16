"""Supplemental A3 correction: PNAS PDF filename is not DOI. Preserve v1 HTTP404."""
from pathlib import Path
import json,hashlib,sys,urllib.request,urllib.error,datetime
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1/manual_grabbed_A3_R2_20261011')
DOI='10.1073/pnas.2012745117'
V1=ROOT/'outputs/task016-p7/v1/manual_grabbed_A3_20261011/A3_raw_authoritative_metadata.json'
SRC=ROOT/'data/raw/task016-p7/manual_grabbed_20261011/11-pnas.202012745.pdf'
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def put(rel,o):
 p=ROOT/rel
 if p.exists():raise RuntimeError('immutable existing')
 write(T,str(rel),json.dumps(o,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
 return {'path':str(rel),'sha256':sha(p.read_bytes())}
def main():
 a=json.loads(V1.read_text())
 s=next(x for x in a['sources'] if x['source_no']=='11')
 assert s['metadata'] is None and s['expected_DOI']=='10.1073/pnas.202012745'
 assert s['manual_original_sha256']==sha(SRC.read_bytes())
 plan={'task':T,'at':now(),'scope':'A3_publication_identity_only',
 'reason':'Initial unqualified filename-derived 11 DOI was false; original PDF imprimatur explicitly prints DOI 10.1073/pnas.2012745117',
 'incorrect_identifier_retained':s['expected_DOI'],'original_pub_printed_identifier':DOI,
 'original_sha':sha(SRC.read_bytes()),'v1_file_sha':sha(V1.read_bytes()),
 'pdf_text_anchor_literal':'doi:10.1073/pnas.2012745117/-/DCSupplemental.',
 'query':'https://api.crossref.org/works/'+urllib.parse.quote(DOI,safe='') if False else 'https://api.crossref.org/works/10.1073%2Fpnas.2012745117',
 'requests_max':1,'source_fresh':False}
 pp=put(B/'precontract.json',plan)
 req=urllib.request.Request(plan['query'],headers={'User-Agent':'FlavoRetro-A3-P7-academic-provenance-check/0.1','Accept':'application/json'})
 status=None;err=None;raw=b''
 try:
  with urllib.request.urlopen(req,timeout=16) as f:
   status=f.status;raw=f.read(2500000)
 except urllib.error.HTTPError as e:
  status=e.code;raw=e.read(2500000);err='HTTP_'+str(e.code)
 except Exception as e:err=str(e)
 rawref=None
 if raw:
  f=ROOT/'data/raw/task016-p7/manual_grabbed_20261011/crossref_a3_R2/11.crossref.corrected.raw.json'
  if f.exists():raise RuntimeError('original exists')
  f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(raw)
  rawref={'path':str(f.relative_to(ROOT)),'sha256':sha(raw)}
  event(T,'write_binary',path=rawref['path'],before=None,after=rawref['sha256'],bytes=len(raw),source='Crossref corrected DOI')
 data=json.loads(raw)['message'] if status==200 else {}
 out={'task':T,'at':now(),'input_precontract':pp,'v1_incorrect_DOI_HTTP404_kept':True,'source_no':'11',
  'official_DOI':data.get('DOI'),'title':(data.get('title') or [None])[0],
  'journal':(data.get('container-title') or [None])[0],
  'published':data.get('published'),'volume':data.get('volume'),'page':data.get('page'),
  'publisher':data.get('publisher'),'status':status,'HTTP':1,'bytes':len(raw),'error':err,'raw_pointer':rawref,
  'chemical_reaction_status':'not_assessed','fresh_admitted':False}
 put(B/'A3_corrected_11.json',out)
 event(T,'A3_corrected_DOI_physical_HTTP',url=plan['query'],status=status,bytes=len(raw),raw_sha=sha(raw) if raw else None)
 print(json.dumps({'status':status,'DOI':data.get('DOI'),'title':out['title'],'corrected_from':s['expected_DOI'],'bytes':len(raw)}))
if __name__=='__main__':main()

"""SS-E02 historical/exposed source-only acquisition; no fresh discovery or admission."""
import json,sys,urllib.parse
from pathlib import Path
import scripts.task016_p7_ss_sources as io
ROOT=io.ROOT; BASE=ROOT/'outputs/task016-p7/v1/SS'; io.OUT=BASE/'E02_design';io.OUT.mkdir(exist_ok=True)
EPOCH='SS-E02'
def old_records():
 return [r for p in BASE.rglob('http_ledger.jsonl') if 'superseded' not in p.parts for r in io.rows(p)]
def acquire(url,role,reason):
 prior=next((r for r in reversed(old_records()) if r['url']==url and r['status_code']==200 and not r.get('error') and (ROOT/r['path']).is_file()),None)
 if prior:
  assert io.sha(ROOT/prior['path'])==prior['sha256'];io.append('reused_raw_records.jsonl',dict(url=url,path=prior['path'],sha256=prior['sha256'],role=role,actual_reuse_at=io.now(),previous_ledger_namespace=prior.get('ledger_namespace'),phase='design',epoch_id=EPOCH,development_exposed=True));return prior
 return io.request(url,role,reason,phase='design',route='E02_historical_source_identity_or_original',epoch_id=EPOCH)
def metadata():
 source=json.loads((io.OUT/'common_source_raw_only_input_v1.json').read_text())['sources'];out=[]
 plan=[dict(source_id=s['source_id'],phase='design',epoch_id=EPOCH,source_is_previously_exposed=True,official_metadata_requests=['https://pmc-oa-opendata.s3.amazonaws.com/'+s['source_id']+'.1/'+s['source_id']+'.1.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query='PMCID:'+s['source_id'],format='json',resultType='core',pageSize=2))],registered_at=io.now()) for s in source]
 if not (io.OUT/'source_metadata_plan.json').exists():io.save('source_metadata_plan.json',plan)
 previous_identity=json.loads((ROOT/'outputs/task016-p6/v1/source_identity_checks.json').read_text())
 for s,p in zip(source,plan):
  prior=next((r for r in previous_identity if r['pmcid']==s['source_id']),None)
  if prior:
   rec=dict(source_id=s['source_id'],s3=prior['meta'],europepmc=prior['europepmc'],exposed_raw_original=s['full_original_xml'],phase='design',metadata_reused_at=io.now())
   for r in [prior['meta'],prior['europepmc']]:assert io.sha(ROOT/r['path'])==r['sha256']
  else:rec=dict(source_id=s['source_id'],s3=acquire(p['official_metadata_requests'][0],'metadata','Official identity and original-media routes for already-exposed original'),europepmc=acquire(p['official_metadata_requests'][1],'metadata','Second official metadata identity for already-exposed source'),exposed_raw_original=s['full_original_xml'],phase='design')
  out.append(rec);io.save('source_metadata_intake.json',out);print(s['source_id'],'metadata raw bound',flush=True)
def media(sid):
 rec=next(r for r in json.loads((io.OUT/'source_metadata_intake.json').read_text()) if r['source_id']==sid)
 if rec['s3'].get('status_code')!=200 or rec['s3'].get('error'):raise RuntimeError('metadata unavailable')
 m=json.loads((ROOT/rec['s3']['path']).read_text());urls=m.get('media_urls',[])
 if not isinstance(urls,list):raise RuntimeError('unexpected official media URL schema')
 # Retain all actual original main figures plus every native SI; full assay universe is determined later.
 plan=[dict(url='https://pmc-oa-opendata.s3.amazonaws.com/'+u.split('s3://pmc-oa-opendata/',1)[1],source_id=sid,phase='design',epoch_id=EPOCH,registered_at=io.now(),reason='Original main figures and complete SI for independent source-backed graph/assay review') for u in urls if not u.split('?')[0].endswith(('.xml','.json'))]
 path=sid+'_media_plan.json';
 if not (io.OUT/path).exists():io.save(path,plan)
 out=io.rows(io.OUT/(sid+'_media_intake.jsonl'));done={r['url'] for r in out}
 for p in plan:
  if p['url'] in done:continue
  r=acquire(p['url'],'attachment',p['reason']);out.append(dict(source_id=sid,**r));io.save_rows(sid+'_media_intake.jsonl',out);print(sid,p['url'].split('/')[-1],r['status_code'],r['bytes'],r.get('error'),flush=True)
def database():
 # Literal source-standard names: properties are raw identity candidates, never structure/source admission.
 names=['quercetin 3-O-sophoroside','kaempferol 3-O-sophoroside','quercetin 3-O-neohesperidoside','kaempferol 3-O-neohesperidoside','UDP-glucose','apiin','UDP-apiose','kaempferol 3-O-[beta-D-apiofuranosyl-(1->2)-beta-D-glucopyranoside]']
 plan=[dict(name=name,source_id='PMC13140228' if name in ['apiin','UDP-apiose',names[-1]] else 'PMC13084081',source_name_anchor='body//p[83] chemical standards' if name not in ['apiin','UDP-apiose',names[-1]] else 'body//p[13,14,19]',phase='design',epoch_id=EPOCH,registered_at=io.now(),property_url='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+urllib.parse.quote(name,safe='')+'/property/Title,IUPACName,MolecularFormula,InChI,InChIKey,IsomericSMILES/JSON',synonym_url='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+urllib.parse.quote(name,safe='')+'/synonyms/JSON') for name in names]
 if not (io.OUT/'source_named_database_identity_plan.json').exists():io.save('source_named_database_identity_plan.json',plan)
 out=io.rows(io.OUT/'source_named_database_identity_intake.jsonl');done={r['source_name'] for r in out}
 for p in plan:
  if p['name'] in done:continue
  prop=acquire(p['property_url'],'structure_database','Official raw source-named database graph identity; CID hints are not authoritative')
  syn=acquire(p['synonym_url'],'metadata','Official raw synonyms to resolve source standard identity; no admission inferred')
  out.append(dict(source_name=p['name'],source_id=p['source_id'],source_name_anchor=p['source_name_anchor'],properties=prop,synonyms=syn,evidence_eligible=False,contains_A4_final_structures=False));io.save_rows('source_named_database_identity_intake.jsonl',out)
  print(p['name'],prop['status_code'],syn['status_code'],flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='metadata':metadata()
 elif mode=='media':media(sys.argv[2])
 elif mode=='database':database()

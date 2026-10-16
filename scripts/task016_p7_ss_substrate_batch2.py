"""Preregister additional E01 substrate-focused discovery; no E02 fresh collection."""
import sys,json,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scripts.task016_p7_ss_sources as s
from scripts.task016_p7_ss_fresh import historical
BASE=s.OUT;s.OUT=BASE/'fresh_substrate_source_batch2';s.OUT.mkdir(exist_ok=True)
queries=[
 '(rhamnosyltransferase OR UGT79D OR UGT79A OR UGT91) AND (myricetin OR isorhamnetin OR scutellarein OR pinocembrin) AND (flavonoid OR flavonol OR flavone OR flavanone)',
 '(("1,6" AND rhamnosyltransferase) OR rutinoside OR rutinosylation) AND (isorhamnetin OR myricetin OR luteolin OR diosmetin OR hesperetin) AND (enzyme OR enzymatic OR glycosyltransferase)'
]
plan=[dict(query_id='SS-E01-SUBSTRATE-BATCH2:'+str(i+1),query=q,url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(dict(query=q,format='json',pageSize=100,resultType='core')),registered_at=s.now(),route='EuropePMC_additional_E01_substrates',scope_freeze_sha256=s.sha(BASE/'scope_freeze.json'),max_pages=1,maximum_results=100,epoch_id='SS-E01',not_E02_fresh=True) for i,q in enumerate(queries)]
if (s.OUT/'registered_plan.jsonl').exists():raise RuntimeError('IMMUTABLE_BATCH_EXISTS')
s.save_rows('registered_plan.jsonl',plan)
seen=historical();executions=[];hits=[]
for q in plan:
 r=s.request(q['url'],'metadata','Find additional E01 Rha(1→6) substrates after actual original review; not model-outcome dependent',phase='fresh',route=q['route'])
 result=json.loads((ROOT/r['path']).read_text()).get('resultList',{}).get('result',[]) if r['status_code']==200 and not r['error'] else []
 executions.append(dict(query_id=q['query_id'],http=r,returned_objects=len(result),executed_at=s.now(),admitted=0,metadata_only=True))
 for h in result:hits.append(dict(query_id=q['query_id'],pmcid=h.get('pmcid'),pmid=h.get('pmid'),doi=h.get('doi'),title=h.get('title'),is_open_access=h.get('isOpenAccess'),journal_info=h.get('journalInfo'),historical_source=h.get('pmcid') in seen,metadata_only=True,evidence_eligible=False,raw_response=r['path']))
 s.save_rows('executions.jsonl',executions);s.save_rows('hits.jsonl',hits)
print(json.dumps(dict(queries=len(executions),hits=len(hits),historical=sum(r['historical_source'] for r in hits)),ensure_ascii=False))

"""Bounded official alternate metadata routes after Europe PMC core requests fail."""
import sys,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save
queries=[]
terms=['UGT79B1','UGT79B6','UGT79B30 OR GmF3G2','CaUGT3','F3GGT1','EsGT1','GtUF6CGT OR TcCGT OR PlUGT43 OR WjGT1']
for i,term in enumerate(terms):
    params=dict(query=term,format='json',pageSize=50,resultType='lite')
    queries.append(dict(provider='europepmc-lite',term=term,url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(params),role='discovery-json'))
    params=dict(db='pmc',term=term,retmode='json',retmax=30)
    queries.append(dict(provider='ncbi',term=term,url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?'+urlencode(params),role='discovery-json'))
save('alternate_query_contract.json',dict(approval_type='agent_delegated',reason='EuropePMC core route returned 503 twice for every query; retain failures, use lightweight official metadata and NCBI PMC search',queries=queries,limits_unchanged=True))
def fetch(q):return dict(**q,raw=get(q['url'],q['provider'],q['role'],q['term']))
with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(fetch,queries))
save('alternate_discovery_manifest.json',records)
by={}
for r in records:
    if r['raw']['status']!='raw_available':print(r['provider'],r['term'],r['raw']['status'],flush=True);continue
    d=json.loads((ROOT/r['raw']['path']).read_text())
    if r['provider']=='ncbi':
        entries=[dict(pmcid='PMC'+i,title='NCBI gene-directed PMC match: '+r['term']) for i in d.get('esearchresult',{}).get('idlist',[])]
    else:entries=[i for i in d.get('resultList',{}).get('result',[]) if i.get('pmcid')]
    for e in entries:
        if e['pmcid'] not in by:by[e['pmcid']]={**e,'discoveries':[]}
        by[e['pmcid']]['discoveries'].append(dict(query=r['term'],raw_path=r['raw']['path'],raw_sha256=r['raw']['sha256']))
    print(r['provider'],r['term'],len(entries),flush=True)
by['PMC4494776']=dict(pmcid='PMC4494776',title='GmF3G2″Gt/UGT79B30 primary study from approved G1 candidate',discoveries=[dict(query='approved G1 source candidate',prior_audit='outputs/planning/task016-p2-transfer-gap-audit.json')])
for r in sorted(by.values(),key=lambda x:x['pmcid']):print('CANDIDATE',r['pmcid'],r['title'],flush=True)
save('article_intake_addendum.json',dict(selection='complete official gene-directed hits, no model outputs; extra article count still bounded by120',records=sorted(by.values(),key=lambda x:x['pmcid'])))

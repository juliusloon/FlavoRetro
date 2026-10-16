"""Retry semantic discovery through the working lightweight official interface."""
import sys,json,re,html
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save
queries=json.loads((OUT/'query_contract.json').read_text())['queries']
queries=[q for q in queries if q['provider']=='europepmc']
plan=[]
for q in queries:
    params={'query':q['params']['query'],'format':'json','pageSize':100,'resultType':'lite'}
    plan.append(dict(label=q['label'],url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(params)))
save('lightweight_query_contract.json',dict(approval_type='agent_delegated',reason='retain failed core route; same semantic source queries through known working lite interface',queries=plan,bounds_unchanged=True))
def fetch(q):return dict(**q,raw=get(q['url'],'europepmc-lite','discovery-json',q['label']))
with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(fetch,plan))
save('lightweight_discovery_manifest.json',result)
records=[]
for q in result:
    if q['raw']['status']!='raw_available':continue
    d=json.loads((ROOT/q['raw']['path']).read_text())
    for r in d.get('resultList',{}).get('result',[]):
        if r.get('pmcid'):records.append(dict(**r,P2_discovery=dict(query=q['label'],raw_path=q['raw']['path'],raw_sha256=q['raw']['sha256'])))
    print(q['label'],d.get('hitCount'),len(d.get('resultList',{}).get('result',[])),flush=True)
save('lightweight_metadata.jsonl',records,True)
selected={}
for r in records:
    title=html.unescape(r['title']);title=re.sub('<[^>]+>',' ',title).lower()
    primary=bool(re.search('glycosyltransferase|glucosyltransferase|rhamnosyltransferase|xylosyltransferase|glycosylflav|c-glycos|c-glucos|sophoros|sambubios|triglycos',title))
    unrelated=bool(re.search('review|overview|human|dermal|panax|ginsenoside|trillin|steroidal|glycosamin|protein|exopolysacch|glycoprotein|n-glycos|lancefield|notch|rmlt',title))
    if primary and not unrelated:
        if r['pmcid'] not in selected:selected[r['pmcid']]={**r,'discoveries':[]}
        selected[r['pmcid']]['discoveries'].append(r['P2_discovery'])
save('lightweight_article_plan.json',dict(selection='same source-title primary/domain rules before assay/model outputs',records=sorted(selected.values(),key=lambda r:r['pmcid'])))
print('selected',len(selected),flush=True)
for r in sorted(selected.values(),key=lambda r:r['pmcid']):print(r['pmcid'],r['title'][:180],flush=True)

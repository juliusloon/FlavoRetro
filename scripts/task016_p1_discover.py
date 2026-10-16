"""Freeze source/query universe independently of model outcomes."""
import json,sys
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p1_sources import get,save,ROOT,OUT
from scripts.operate import event
queries=[]
terms='flavonoid OR flavonol OR flavone OR isoflavone OR anthocyanin OR quercetin OR kaempferol OR luteolin OR apigenin OR naringenin OR hesperetin OR myricetin OR genistein OR daidzein OR baicalein OR scutellarein OR vitexin OR orientin'
for label,q in [('broad',f'({terms}) AND (UDP OR glycosyl OR glucosyl OR rhamnosyl OR galactosyl OR arabinosyl)'),('sugar-sugar','(flavonoid OR flavonol OR rutin OR montbretin OR quercetin OR kaempferol) AND (rhamnosyl OR xylosyl OR arabinosyl OR galactosyl)'),('c-formation','(vitexin OR orientin OR C-glycosyl OR C-glucosyl) AND (UDP OR glycosyltransferase)'),('donors','(flavonoid OR quercetin OR kaempferol OR anthocyanidin) AND (UDP-rhamnose OR UDP-arabinose OR UDP-galactose OR UDP-glucuronate)')]:
    params={'query':q,'columns':'rhea-id,equation,chebi-id,ec,pubmed','format':'tsv','limit':1000};queries.append(dict(provider='rhea',label=label,url='https://www.rhea-db.org/rhea/?'+urlencode(params),params=params,role='query-tsv'))
for label,q in [('enzymatic','(flavonoid OR flavonol OR flavone OR isoflavone) AND (glycosyltransferase OR glucosyltransferase OR rhamnosyltransferase)'),('C','(flavonoid OR flavone) AND (C-glycosyltransferase OR C-glucosyltransferase)'),('sugar-sugar','(flavonoid OR montbretin OR flavonol) AND (glycoside glycosyltransferase OR rhamnosyltransferase OR UGT79 OR UGT94)'),('chemical','(flavonoid OR flavonol OR flavone) AND (glycosylation synthesis glycosyl donor)')]:
    params={'query':'('+q+') AND OPEN_ACCESS:Y','format':'json','pageSize':100,'resultType':'core','sort':'RELEVANCE','cursorMark':'*'};queries.append(dict(provider='europepmc',label=label,url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(params),params=params,role='discovery-json'))
queries+=[dict(provider='enzymemap',label='zenodo-metadata',url='https://zenodo.org/api/records/8254726',params={},role='metadata-json'),dict(provider='enzymemap',label='github-metadata',url='https://api.github.com/repos/hesther/enzymemap/contents/data',params={},role='metadata-json'),dict(provider='sabiork',label='flavonoid',url='https://sabiork.h-its.org/sabioRestWebServices/searchKineticLaws/sbml?'+urlencode({'q':'EnzymeType:"glycosyltransferase" AND (Substrate:"quercetin" OR Substrate:"kaempferol" OR Substrate:"luteolin")'}),params={},role='query-sbml')]
if not (OUT/'query_contract.json').exists():save('query_contract.json',dict(approval_type='agent_delegated',selection='source fields and stable identifiers; no model outcomes',queries=queries,include_si=True,max_records=10000,max_articles=200,max_attachments=400,max_requests=4000,max_bytes=5*1024**3))
def fetch(q):
    r=get(q['url'],q['provider'],q['role'],q['label']);return {**q,**r}
with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(fetch,queries))
save('discovery_manifest.json',result)
for r in result:
    count=None
    if r['status']=='raw_available':
        data=(ROOT/r['path']).read_text()
        if r['role']=='query-tsv':count=max(0,len(data.splitlines())-1)
        elif r['provider']=='europepmc':count=json.loads(data).get('hitCount')
    print(r['provider'],r['label'],r['status'],r['bytes'],count,flush=True)
event('TASK-016-P1','source_intake',approval_type='agent_delegated',workflow='multi-source-search, lawful OA + explicit SI in approved contract',academic_mcp_available=False)

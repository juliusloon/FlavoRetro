"""Public publisher fulltext/SI for primary direct-C and sugar-transfer citations."""
import sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save
records=[]
for doi,role in [('10.1002/anie.201905505','C-direct'),('10.1111/tpj.13510','C-isoflavone'),('10.1016/j.febslet.2014.11.045','C-direct6'),('10.1111/j.1365-313X.2010.04409.x','SS-xylose'),('10.1111/j.1365-313X.2005.02383.x','SS-glucose')]:
    records.append(dict(doi=doi,role=role,url='https://onlinelibrary.wiley.com/doi/full/'+doi if not doi.startswith('10.1016') else 'https://doi.org/'+doi,content_role='publisher_fulltext'))
records.append(dict(doi='10.1002/anie.201905505',role='C-direct',url='https://onlinelibrary.wiley.com/doi/suppl/10.1002/anie.201905505/supinfo/anie201905505-sup-0001.pdf',content_role='supplement'))
save('publisher_intake_contract.json',dict(selection='primary articles cited by already acquired studies; direct-C and SS follow-up, no model selection',public_anonymous_only=True,records=records,unknown_license_local_only=True))
def fetch(r):return dict(**r,raw=get(r['url'],'publisher',r['content_role'],r['doi']),admission='pending complete source identity and license; metadata never substitutes for assay')
with ThreadPoolExecutor(max_workers=2) as pool:result=list(pool.map(fetch,records))
save('publisher_acquisition_manifest.json',result)
for r in result:print(r['doi'],r['content_role'],r['raw']['status'],r['raw'].get('status_code'),flush=True)

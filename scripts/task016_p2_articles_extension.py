"""Source-only completion of promising pending primary candidates; no success-based selection."""
import sys,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save,rows
import scripts.task016_p1_articles as adapter
adapter.get=get
WANTED=['PMC10706860','PMC10856022','PMC11273223','PMC11502824','PMC12246196','PMC12494026','PMC12658608','PMC12790375','PMC12844164','PMC12984077','PMC13421352','PMC12993211']
plan=json.loads((OUT/'lightweight_article_plan.json').read_text())['records']
previous={r['pmcid']:r for n in ['article_acquisition_manifest.json','article_acquisition_addendum.json'] for r in json.loads((OUT/n).read_text())}
records=[r for r in plan if r['pmcid'] in WANTED]
assert len(records)==len(WANTED)
save('primary_extension_contract.json',dict(approval_type='agent_delegated',reason='finish source-only pending direct C formation, broad UGT, and flavonoid sugar-chain candidates; no A/B/D results used for selection; scientific thresholds unchanged',records=records,limits_unchanged=True))
def fetch(r):
 if r['pmcid'] in previous:return {**previous[r['pmcid']],'P2_extension_reused':True}
 return {**adapter.available_article(r),'P2_role':'new_article','selection_stage':'G1_primary_extension'}
result=[]
with ThreadPoolExecutor(max_workers=4) as pool:
 for r in pool.map(fetch,records):
  result.append(r);save('article_acquisition_extension.json',result);print(r['pmcid'],r['status'],flush=True)
segments=[]
for item in result:
 if item['status']!='fulltext_available':continue
 root=ET.parse(ROOT/item['xml']['path']).getroot();doi=root.find(".//article-id[@pub-id-type='doi']")
 for tag in ['p','table-wrap','fig']:
  for i,el in enumerate(root.findall('.//body//'+tag)):
   text=' '.join(''.join(el.itertext()).split())
   segments.append(dict(pmcid=item['pmcid'],doi=doi.text if doi is not None else None,locator=f'body//{tag}[{i+1}]',xml_id=el.get('id'),text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),raw_path=item['xml']['path'],raw_sha256=item['xml']['sha256'],license=item.get('license'),article_version=item.get('article_version')))
save('article_evidence_extension.jsonl',segments,True)
print('extension segments',len(segments),flush=True)

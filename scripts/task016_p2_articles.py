"""Reuse immutable P1 articles and the existing official PMC acquisition adapter."""
import sys,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save,rows
import scripts.task016_p1_articles as adapter
adapter.get=get  # Reuse parsing logic, bind all downloads to P2 budget and immutable namespace.
def collect():
    plan=json.loads((OUT/'article_intake_plan.json').read_text())
    old=[r for name in ['article_acquisition_manifest.json','article_acquisition_addendum.json'] for r in json.loads((ROOT/'outputs/task016-p1/v1'/name).read_text())]
    available={r['pmcid']:r for r in old if r['status']=='fulltext_available'}
    def fetch(r):
        if r['pmcid'] in available:
            item=available[r['pmcid']]
            for f in item['files']:
                assert hashlib.sha256((ROOT/f['path']).read_bytes()).hexdigest()==f['sha256']
            return dict(**item,P2_role='reused_immutable_article',P2_discovery=r.get('P2_discoveries',[]))
        return dict(**adapter.available_article({**r,'discoveries':r.get('P2_discoveries',[])}),P2_role='new_article')
    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for item in pool.map(fetch,plan['records']):
            results.append(item);save('article_acquisition_manifest.json',results)
            print(len(results),item['pmcid'],item['status'],item['P2_role'],flush=True)
    segments=[]
    for item in results:
        if item['status']!='fulltext_available':continue
        root=ET.parse(ROOT/item['xml']['path']).getroot()
        doi=root.find(".//article-id[@pub-id-type='doi']")
        for tag in ['p','table-wrap','fig']:
            for i,el in enumerate(root.findall('.//body//'+tag)):
                text=' '.join(''.join(el.itertext()).split())
                segments.append(dict(pmcid=item['pmcid'],doi=doi.text if doi is not None else None,locator=f'body//{tag}[{i+1}]',xml_id=el.get('id'),text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),raw_path=item['xml']['path'],raw_sha256=item['xml']['sha256'],license=item.get('license'),article_version=item.get('article_version')))
    save('article_evidence_segments.jsonl',segments,True)
    save('source_registry.json',dict(articles=results,all_new_attempts=len(rows(OUT/'acquisition_attempts.jsonl')),reused_files=rows(OUT/'reused_files.jsonl'),unacquired_pages=json.loads((OUT/'discovery_manifest.json').read_text()),scope='source-only discovery; exact reaction admission not established'))
    print('available',sum(r['status']=='fulltext_available' for r in results),'segments',len(segments),flush=True)
if __name__=='__main__':collect()

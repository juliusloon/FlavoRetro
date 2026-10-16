"""Acquire the source-only alternate-route article addendum."""
import sys,json,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save,rows
import scripts.task016_p1_articles as adapter
adapter.get=get
previous=json.loads((OUT/'article_acquisition_manifest.json').read_text())
old={r['pmcid']:r for r in previous if r['status']=='fulltext_available'}
result=[]
for rec in json.loads((OUT/'article_intake_addendum.selected.json').read_text())['records']:
    item=dict(**old[rec['pmcid']],P2_addendum_reuse=True) if rec['pmcid'] in old else dict(**adapter.available_article(rec),P2_role='new_article')
    result.append(item);save('article_acquisition_addendum.json',result)
    print(rec['pmcid'],item['status'],flush=True)
segments=rows(OUT/'article_evidence_segments.jsonl');known={r['pmcid'] for r in segments}
for item in result:
    if item['status']!='fulltext_available' or item['pmcid'] in known:continue
    root=ET.parse(ROOT/item['xml']['path']).getroot();doi=root.find(".//article-id[@pub-id-type='doi']")
    for tag in ['p','table-wrap','fig']:
        for i,el in enumerate(root.findall('.//body//'+tag)):
            text=' '.join(''.join(el.itertext()).split())
            segments.append(dict(pmcid=item['pmcid'],doi=doi.text if doi is not None else None,locator=f'body//{tag}[{i+1}]',xml_id=el.get('id'),text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),raw_path=item['xml']['path'],raw_sha256=item['xml']['sha256'],license=item.get('license'),article_version=item.get('article_version')))
save('article_evidence_segments.jsonl',segments,True)

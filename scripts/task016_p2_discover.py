"""Source-only query and article discovery, no model or template access."""
import sys,json,re,html
from pathlib import Path
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p2_sources import ROOT,OUT,get,save,rows
queries=[]
for label,q in [
('C-general','(flavonoid OR flavone OR flavanone OR dihydrochalcone) AND (C-glycosyltransferase OR C-glucosyltransferase OR C-rhamnosyltransferase OR C-xylosyltransferase)'),
('C-acceptors','(C-glycosyl OR C-glucosyl OR C-rhamnosyl) AND (substrate promiscuity OR acceptor OR NMR)'),
('C-novel','(dihydrochalcone OR phloretin OR davidigenin OR aspalathin) AND (glycosyltransferase OR glycosylation)'),
('C-rhamnose','(VtCGTc OR violanthin OR C-rhamnosyltransferase)'),
('SS-glucose','(flavonoid OR flavonol OR anthocyanin) AND (sophoroside OR sophorosyl OR glucosyltransferase) AND (glycoside OR UGT79 OR UGT94 OR UGT91)'),
('SS-xylose','(flavonoid OR flavonol OR anthocyanin OR cyanidin) AND (xylosyltransferase OR sambubioside OR sambubiosyl)'),
('SS-genes','(UGT79B1 OR UGT79B6 OR UGT79B30 OR UGT79B31 OR UGT94 OR GmF3G2 OR F3GGT1 OR EsGT1 OR CaUGT3)'),
('SS-16','(flavonoid OR flavonol OR glycoside) AND (oligoglucoside OR gentiobioside OR diglucoside OR triglycoside) AND (biosynthesis OR glycosyltransferase)'),
('SS-rhamnose','(flavonoid OR rutin OR naringin OR hesperidin) AND (rhamnosyltransferase OR UGT79 OR UGT91)'),
('SS-montbretin','(montbretin OR mini-MbA) AND (glucosylation OR xylosyltransferase OR glycosyltransferase)'),
('SS-chemical','(flavonoid OR flavonol) AND (sophoroside OR sambubioside OR gentiobioside) AND synthesis'),
('C-chemical','(flavonoid OR flavone OR chalcone) AND (C-glycoside OR C-glycosylation) AND (synthesis OR glycosyl donor)'),
('SS-UGT79B1','UGT79B1'),('SS-UGT79B6','UGT79B6'),('SS-Gm','UGT79B30 OR GmF3G2'),('SS-CaUGT3','CaUGT3'),('SS-F3GGT1','F3GGT1'),('SS-EsGT1','EsGT1'),('C-direct','GtUF6CGT OR TcCGT1 OR PlUGT43 OR WjGT1 OR direct C-glycosyltransferase')]:
    params=dict(query='('+q+') AND OPEN_ACCESS:Y',format='json',pageSize=100,resultType='core',sort='RELEVANCE',cursorMark='*')
    queries.append(dict(provider='europepmc',label=label,url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urlencode(params),params=params,role='discovery-json'))
for label,q in [('crossref-C','flavonoid C glycosyltransferase substrate NMR'),('crossref-SS','flavonoid glycoside glucosyltransferase xylosyltransferase sophoroside')]:
    params={'query':q,'rows':50}
    queries.append(dict(provider='crossref',label=label,url='https://api.crossref.org/works?'+urlencode(params),params=params,role='discovery-json'))
if not (OUT/'query_contract.json').exists():
    save('query_contract.json',dict(task='TASK-016-P2',selection='source-only title/abstract/fulltext identity quality; stable PMCID, no model outcomes',queries=queries,budgets=dict(max_metadata=5000,max_articles=120,max_attachments=240,max_HTTP_attempts=2500,max_bytes=2*1024**3),include_si=True,title_HTML_stripped=True,query_keywords_version='C-and-sugar-transfer-synonyms-v1',existing_sources_reused=True))
def fetch(q):return dict(**q,raw=get(q['url'],q['provider'],q['role'],q['label']))
with ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(fetch,queries))
save('discovery_manifest.json',results)
by={}
for name in ['outputs/task016-p1/v1/article_discovery_records.jsonl']:
    for r in rows(ROOT/name):
        if r.get('pmcid'):by[r['pmcid']]={**r,'P2_discoveries':[],'inherited_metadata':True}
for result in results:
    raw=result['raw']
    if raw['status']!='raw_available':continue
    doc=json.loads((ROOT/raw['path']).read_text())
    recs=doc.get('resultList',{}).get('result',[]) if result['provider']=='europepmc' else []
    result['hit_count']=doc.get('hitCount',doc.get('message',{}).get('total-results'))
    result['records_returned']=len(recs) if result['provider']=='europepmc' else len(doc.get('message',{}).get('items',[]))
    result['unacquired_pages']='hit_count beyond returned page retained as unacquired; no exhaustive coverage claim'
    for rec in recs:
        pmc=rec.get('pmcid')
        if not pmc:continue
        if pmc not in by:by[pmc]={**rec,'P2_discoveries':[],'inherited_metadata':False}
        by[pmc]['P2_discoveries'].append(dict(query=result['label'],raw_path=raw['path'],raw_sha256=raw['sha256']))
records=[]
for r in by.values():
    title=html.unescape(re.sub('<[^>]+>',' ',r['title'])).lower()
    r['stripped_title']=title
    c=bool(re.search(r'c[- ‐–]*(?:glycos|glucos|rhamnos|xylos)|di[- ‐–]*c[- ‐–]*glycos|violanthin',title))
    ss=bool(re.search(r'sophoros|sambubios|montbret|oligogluc|triglycos|diglycos|diglucos|sugar.*sugar|glycoside glycos|rhamnosyltransferase|xylosyltransferase|ugt79|ugt91|ugt94',title))
    review=bool(re.search(r'review|perspective|advances|overview|glycosyltransferases:|glycosyltransferases for|progress',title))
    targeted=any(d['query'] in ['SS-UGT79B1','SS-UGT79B6','SS-Gm','SS-CaUGT3','SS-F3GGT1','SS-EsGT1','C-direct'] for d in r['P2_discoveries'])
    unrelated=bool(re.search(r'human|dermal|fibroblast|proteoglycan|collagen|arthro|streptococcus|spondylo|gastric|macrophage|senescence|chondrocyte|osteopor|exopolysaccharide|xyloglucan|rhamnogalacturonan|glycosaminoglycan|rmlt|n-glycan|n-glycosylation|nosiheptide|notch|trillin|polyphyllin|paris polyphylla|ginsenoside|mogroside|asiaticoside|crocin|saponin|phenylethanoid',title))
    r['intake_selected']=((c or ss) and not unrelated or targeted) and not review
    r['candidate_family']='C' if c or any(d['query']=='C-direct' for d in r['P2_discoveries']) else 'SS' if ss or targeted else 'other'
    r['selection_reason']='targeted C or sugar-chain transfer title; chemical admission pending' if r['intake_selected'] else 'metadata retained; broad/review/unrelated title'
    records.append(r)
assert len(records)<=5000
records.sort(key=lambda r:r['pmcid'])
save('article_discovery_records.jsonl',records,True);save('discovery_manifest.json',results)
chosen=[r for r in records if r['intake_selected']]
chosen.sort(key=lambda r:(r['candidate_family'],r['pmcid']))
# Existing available fulltexts do not consume newly acquired article slots.
old=[r for name in ['article_acquisition_manifest.json','article_acquisition_addendum.json'] for r in json.loads((ROOT/'outputs/task016-p1/v1'/name).read_text())]
old_ids={r['pmcid'] for r in old if r['status']=='fulltext_available'}
new=[r for r in chosen if r['pmcid'] not in old_ids][:120]
selected=[r for r in chosen if r['pmcid'] in old_ids]+new
save('article_intake_plan.json',dict(selection='fixed title synonyms and stable PMCID before assays/templates/model',new_article_cap=120,records=selected,unselected_new=[r['pmcid'] for r in chosen if r not in selected],reused_article_ids=sorted({r['pmcid'] for r in selected}&old_ids)))
print('metadata',len(records),'selected',len(selected),'new',len(new),'reused',len(selected)-len(new),flush=True)
for r in selected:print(r['candidate_family'],r['pmcid'],r['stripped_title'][:150],flush=True)

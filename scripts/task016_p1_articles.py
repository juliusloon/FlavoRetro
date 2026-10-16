"""Source-only selection and bounded anonymous PMC XML/SI acquisition."""
import hashlib,json,re,sys,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode,unquote,urlparse,parse_qs
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.task016_p1_sources import get,save,ROOT,OUT,rows
from scripts.operate import event
B='https://pmc-oa-opendata.s3.amazonaws.com/'
def metadata_records():
    by={}
    for name in ['secondary_discovery_manifest.json','focused_discovery_manifest.json']:
        for raw in json.loads((OUT/name).read_text()):
            if raw['status']!='raw_available':continue
            for rec in json.loads((ROOT/raw['path']).read_text())['resultList']['result']:
                if not rec.get('pmcid'):continue
                pmc=rec['pmcid']
                if pmc not in by:by[pmc]={**rec,'discoveries':[]}
                by[pmc]['discoveries'].append(dict(query=raw.get('name'),path=raw['path'],sha256=raw['sha256']))
    return sorted(by.values(),key=lambda r:r['pmcid'])
def select(records):
    kept=[]
    for r in records:
        title=re.sub('<[^>]+>',' ',r['title']).lower()
        glyco=bool(re.search('glycos|glucos|rhamnos|xylos|apios|ugt',title))
        review=bool(re.search('review|perspective|progress|advances|overview',title))
        primary=bool(re.search('characteri|functional|identification|biosynth|substrate|regioselec|enzyme|cataly|glycosylation|structure|engineering|specificity',title))
        r['intake_selected']=glyco and primary and not review
        r['selection_reason']='primary glycosylation-focused title; source eligibility still pending' if r['intake_selected'] else 'metadata-only: title not a targeted primary glycosylation study'
        if r['intake_selected']:kept.append(r)
    # Stable priority, independent of template/model outcomes; reserve multi-version slots.
    kept.sort(key=lambda r:(0 if any(x['query']=='rhea-citations' for x in r['discoveries']) else 1,0 if re.search('c-glycos|c-glucos|montbret|apios|rhamnos|xylos',r['title'],re.I) else 1,r['pmcid']))
    return kept[:180]
def available_article(rec):
    pmc=rec['pmcid'];result=dict(pmcid=pmc,title=rec['title'],discovery=rec['discoveries'],files=[],status='unavailable',review_type='agent_delegated',independent_chemical_validation=False)
    raw=get(B+'?'+urlencode({'list-type':2,'prefix':pmc+'.','max-keys':100}),'pmc','listing',pmc)
    result['files'].append(raw)
    if raw['status']!='raw_available':return result
    try:keys=[el.text for el in ET.parse(ROOT/raw['path']).findall('.//{*}Key')]
    except ET.ParseError:result['status']='invalid_listing';return result
    metas=[]
    for key in sorted(k for k in keys if k.endswith('.json'))[:2]:
        m=get(B+key,'pmc','metadata',pmc+'-'+hashlib.sha256(key.encode()).hexdigest()[:8]);result['files'].append(m)
        if m['status']=='raw_available':
            try:metas.append((json.loads((ROOT/m['path']).read_text()),m))
            except ValueError:pass
    # Prefer final published version based on metadata, not largest version number.
    metas.sort(key=lambda t:(t[0].get('is_manuscript') in [True,'yes'],str(t[0].get('version'))))
    if not metas:
        x=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+pmc+'/fullTextXML','europepmc','fullTextXML',pmc);result['files'].append(x)
        if x['status']=='raw_available':
            try:
                root=ET.parse(ROOT/x['path']).getroot();lic=root.find('.//license')
                license_text=''.join(lic.itertext()) if lic is not None else ''
                if 'creativecommons.org' not in ET.tostring(lic,encoding='unicode') if lic is not None else True:
                    result['status']='license_pending';return result
                result.update(status='fulltext_available',xml=x,license=license_text,article_version='EuropePMC-deposit',supplement_status='cloud_listing_empty; not acquired')
            except ET.ParseError:result['status']='format_error'
        return result
    meta,m=metas[0];license=meta.get('license_code');result.update(license=license,article_version=meta.get('version'),article_metadata=m)
    if meta.get('is_retracted') in [True,'yes'] or not str(license).startswith('CC'):
        result['status']='retracted_or_license_pending';return result
    urls=[meta.get('xml_url')]+[u for u in meta.get('media_urls',[]) if unquote(urlparse(u).path).lower().endswith(('.pdf','.docx','.xlsx','.csv','.zip','.doc','.xls'))][:4]
    for index,u in enumerate(urls):
        if not u:continue
        u=u.replace('s3://pmc-oa-opendata/',B)
        x=get(u,'pmc','fullTextXML' if index==0 else 'supplement',pmc+'-v'+str(meta.get('version'))+'-'+str(index));result['files'].append(x)
        if x['status']=='raw_available':
            expected=parse_qs(urlparse(u).query).get('md5',[None])[0]
            x['official_md5_verified']=expected is not None and hashlib.md5((ROOT/x['path']).read_bytes()).hexdigest()==expected
            if not x['official_md5_verified']:x['semantic_status']='hash_failed';continue
            if index==0:
                try:ET.parse(ROOT/x['path'])
                except ET.ParseError:x['semantic_status']='format_error';continue
                result.update(status='fulltext_available',xml=x)
    return result
if __name__=='__main__':
    records=metadata_records();chosen=select(records)
    if not (OUT/'article_intake_plan.json').exists():
        save('article_discovery_records.jsonl',records,True)
        save('article_intake_plan.json',dict(version=1,selection='frozen source/title rule before extraction/templates/model results',max_versions=200,max_attachments=400,pmcids=[r['pmcid'] for r in chosen],records=chosen))
    else:chosen=json.loads((OUT/'article_intake_plan.json').read_text())['records']
    print('article_plan',len(chosen),'discovered',len(records),flush=True)
    results=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,r in enumerate(pool.map(available_article,chosen)):
            results.append(r);save('article_acquisition_manifest.json',results)
            print(i+1,r['pmcid'],r['status'],flush=True)
    para=[]
    for r in results:
        if r['status']!='fulltext_available':continue
        root=ET.parse(ROOT/r['xml']['path']).getroot()
        doi=root.find(".//article-id[@pub-id-type='doi']")
        for tag in ['p','table-wrap','fig']:
            for n,el in enumerate(root.findall('.//body//'+tag)):
                text=' '.join(''.join(el.itertext()).split())
                para.append(dict(pmcid=r['pmcid'],doi=doi.text if doi is not None else None,locator=f'body//{tag}[{n+1}]',xml_id=el.get('id'),text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),raw_path=r['xml']['path'],raw_sha256=r['xml']['sha256'],license=r.get('license')))
    save('article_evidence_segments.jsonl',para,True)
    actual=rows(OUT/'acquisition_attempts.jsonl');articles=[r for r in actual if r['content_role']=='fullTextXML'];attachments=[r for r in actual if r['content_role']=='supplement']
    # HTTP retries are not distinct article/attachment versions.
    assert len({r['url'] for r in articles})<=200
    assert len({r['url'] for r in attachments})<=400
    print('available',sum(r['status']=='fulltext_available' for r in results),'segments',len(para),'requests',len(actual),'bytes',sum(r['bytes'] for r in actual))

"""Bounded PMC cloud fallback using official per-article metadata, not HTML scraping."""
import hashlib,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from flavoretro.open_reactions import freeze_download
from scripts.operate import event,write
root=Path(__file__).resolve().parents[1];base=root/'data/raw/task016/pmc-s3/2026-10-06';download_base=base/'https'
manifest=[]
for pmcid in ['PMC6036675','PMC5897352']:
    listing=ET.parse(base/(pmcid+'-listing.xml')).getroot()
    keys=[el.text for el in listing.findall('.//{*}Key')]
    meta_keys=sorted(k for k in keys if k.endswith('.json'))
    for key in meta_keys:
        rows=freeze_download('https://pmc-oa-opendata.s3.amazonaws.com/'+key,download_base/pmcid,'metadata')
        for row in rows: row.update(provider='PMC-cloud',record_id=pmcid,content_role='metadata');manifest.append(row);event('TASK-016','open_download',**row)
        if rows[-1]['status']!='raw_available':continue
        meta=json.loads(Path(rows[-1]['path']).read_text());print('META',meta)
        if meta.get('is_retracted') in (True,'yes') or meta.get('license_code') not in ['CC BY','CC-BY','CC BY 4.0','CC-BY-4.0']:raise ValueError('unapproved article licence or retracted article')
        urls=[meta['xml_url']]+[u for u in meta.get('media_urls',[]) if unquote(urlparse(u).path).lower().endswith(('.pdf','.docx','.xlsx','.csv','.zip'))]
        for index,url in enumerate(urls):
            url=url.replace('s3://pmc-oa-opendata/','https://pmc-oa-opendata.s3.amazonaws.com/')
            rows=freeze_download(url,download_base/pmcid,'xml' if index==0 else 'si-'+str(index))
            for row in rows:
                row.update(provider='PMC-cloud',record_id=pmcid,license=meta['license_code'],content_role='fullTextXML' if index==0 else 'supplement',article_version=meta.get('version'))
                if row['status']=='raw_available':
                    md5=parse_qs(urlparse(url).query).get('md5',[None])[0]
                    row['official_md5_verified']=md5 is not None and hashlib.md5(Path(row['path']).read_bytes()).hexdigest()==md5
                    if not row['official_md5_verified']:raise ValueError('official object hash mismatch')
                manifest.append(row);event('TASK-016','open_download',**row)
write('TASK-016','outputs/task016/v1/pmc_cloud_https_manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:r.get(k) for k in ['record_id','content_role','status','bytes','official_md5_verified']} for r in manifest],indent=2))

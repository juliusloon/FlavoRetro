"""Read-only source attachment extraction; preserve unavailable, scanned and unparsed cases."""
import sys,json,zipfile,subprocess,xml.etree.ElementTree as ET,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.resources import sha
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'outputs/task016-p2/v1';Q=ROOT/'outputs/task016-p2/v2'
articles={r['pmcid']:r for n in ['article_acquisition_manifest.json','article_acquisition_addendum.json','article_acquisition_extension.json'] for r in json.loads((R/n).read_text())}
chosen=set(r['pmcid'] for r in json.loads((R/'article_acquisition_extension.json').read_text()))|{'PMC9700910','PMC6255700','PMC3507004','PMC12313340','PMC4282749'}
records=[]
def extract(pmc,f,label,data):
 h=hashlib.sha256(data).hexdigest();dest=Q/'attachment-text'/pmc/(h[:24]+'.txt');text=None;status='unparsed_format';error=None
 if data.startswith(b'%PDF'):
  av=['pdftotext','-layout','-','-'];event('TASK-016-P2','attachment_pdf_text_command',argv=av,raw_path=f['path'],member=label)
  r=subprocess.run(av,input=data,capture_output=True);text=r.stdout.decode('utf8','replace');error=r.stderr.decode('utf8','replace')[-1500:] or None;status='parsed_text' if r.returncode==0 and text.strip() else 'empty_scanned_or_parse_failure'
 elif label.endswith('.xml'):
  try:text='\n'.join(''.join(p.itertext()) for p in ET.fromstring(data).findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'));status='parsed_text'
  except Exception as ex:error=str(ex);status='parse_failure'
 if text is not None:write('TASK-016-P2',str(dest.relative_to(ROOT)),text)
 records.append(dict(pmcid=pmc,raw_path=f['path'],raw_sha256=f['sha256'],member=label,member_sha256=h,status=status,error=error,characters=len(text) if text else 0,derived_text_path=str(dest.relative_to(ROOT)) if text is not None else None,identity_admission=False))
for pmc in sorted(chosen):
 a=articles[pmc]
 if a['status']!='fulltext_available':continue
 for f in a['files']:
  if f['content_role']!='supplement':continue
  if f['status']!='raw_available':records.append(dict(pmcid=pmc,raw_path=f['path'],raw_sha256=f['sha256'],status='retained_unavailable',error=f.get('error')));continue
  path=ROOT/f['path'];assert sha(path)==f['sha256'];data=path.read_bytes()
  if data.startswith(b'%PDF'):extract(pmc,f,'attachment.pdf',data)
  elif zipfile.is_zipfile(path):
   with zipfile.ZipFile(path) as z:
    for item in z.infolist():
     if item.file_size>64*1024**2 or item.is_dir():continue
     if item.filename=='word/document.xml' or item.filename.lower().endswith('.pdf'):extract(pmc,f,item.filename,z.read(item))
     elif item.filename.startswith('word/media/'):records.append(dict(pmcid=pmc,raw_path=f['path'],raw_sha256=f['sha256'],member=item.filename,status='embedded_image_not_structurally_encoded',member_sha256=hashlib.sha256(z.read(item)).hexdigest()))
  else:records.append(dict(pmcid=pmc,raw_path=f['path'],raw_sha256=f['sha256'],status='retained_unparsed_format',identity_admission=False))
write('TASK-016-P2',str((Q/'attachment_parse_manifest.jsonl').relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in records))
from collections import Counter
print('parse',dict(Counter(r['status'] for r in records)))

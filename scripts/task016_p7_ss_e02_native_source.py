"""A4 native source preprocessing of all complete frozen E02 historical originals/SI.
No other extractor output is read; no graph is inferred from a name.
"""
import json,sys,zipfile,subprocess,hashlib,xml.etree.ElementTree as ET,urllib.parse
from pathlib import Path
from scripts.operate import write,event
from scripts.task016_p7_ss_sources import ROOT,sha,now
BASE=ROOT/'outputs/task016-p7/v1/SS/E02_design';OUT=BASE/'A4_native_source';TASK='TASK-016-P7'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
manifest=json.loads((BASE/'common_source_raw_only_input_v2.json').read_text());records=[]
def save(name,obj,jsonl=False):
 p=OUT/name
 if p.exists():return dict(path=str(p.relative_to(ROOT)),sha256=sha(p),existing_immutable_preprocessing_reused=True)
 txt=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in obj) if jsonl else json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 write(TASK,str(p.relative_to(ROOT)),txt);return dict(path=str(p.relative_to(ROOT)),sha256=sha(p))
for source in manifest['sources']:
 sid=source['source_id']
 for item in source['official_all_main_figures_and_complete_SI_raw']:
  name=urllib.parse.urlsplit(item['url']).path.rsplit('/',1)[-1];suffix=Path(name).suffix.lower();p=ROOT/item['path']
  assert sha(p)==item['sha256'];r=dict(source_id=sid,raw_path=item['path'],raw_sha256=item['sha256'],original_name=name,processed_at=now(),no_final_graphs=True)
  if suffix=='.pdf':
   argv=['pdftotext','-layout',str(p),'-'];event(TASK,'native_source_subcommand_start',argv=argv,source_sha256=item['sha256'])
   done=subprocess.run(argv,capture_output=True);event(TASK,'native_source_subcommand_end',argv=argv,returncode=done.returncode,stdout_sha256=hashlib.sha256(done.stdout).hexdigest(),stderr_sha256=hashlib.sha256(done.stderr).hexdigest())
   text=done.stdout.decode('utf-8',errors='replace');pages=text.split('\f');
   if pages and not pages[-1].strip():pages=pages[:-1]
   r.update(native_parser='pdftotext -layout whole original',returncode=done.returncode,stderr_literal=done.stderr.decode('utf-8',errors='replace'),physical_pages=len(pages),outputs=[save(sid+'/'+name+'.pages.jsonl',[dict(source_id=sid,raw_path=item['path'],raw_sha256=item['sha256'],physical_page=i,literal_text=t,no_final_graphs=True) for i,t in enumerate(pages,1)],True)])
  elif suffix=='.docx':
   with zipfile.ZipFile(p) as z:
    native=z.read('word/document.xml');doc=ET.fromstring(native);rel=ET.fromstring(z.read('word/_rels/document.xml.rels'));relationships={n.get('Id'):n.get('Target') for n in rel}
    paragraphs=[dict(paragraph_index=i,literal_text=''.join(n.text or '' for n in q.findall('.//w:t',NS)),image_refs=[n.get('{'+NS['r']+'}embed') for n in q.findall('.//a:blip',NS)]) for i,q in enumerate(doc.findall('.//w:p',NS),1)]
    tables=[dict(table_index=i,literal_rows=[[ ''.join(n.text or '' for n in cell.findall('.//w:t',NS)) for cell in row.findall('./w:tc',NS)] for row in table.findall('./w:tr',NS)]) for i,table in enumerate(doc.findall('.//w:tbl',NS),1)]
    media=[dict(zip_member=n,bytes=len(z.read(n)),sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in z.namelist() if n.startswith('word/media/')]
    r.update(native_parser='complete ZIP document.xml paragraphs/cells, original media identifiers',paragraphs=len(paragraphs),tables=len(tables),media=len(media),outputs=[save(sid+'/'+name+'.native.json',dict(source_id=sid,raw_path=item['path'],raw_sha256=item['sha256'],paragraphs=paragraphs,tables=tables,relationships=relationships,source_media_manifest=media,no_final_graphs=True))])
  elif suffix=='.xlsx':
   with zipfile.ZipFile(p) as z:
    strings=[]
    if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
    decoded=[]
    for name2 in z.namelist():
     if not name2.startswith('xl/worksheets/sheet') or not name2.endswith('.xml'):continue
     for row in ET.fromstring(z.read(name2)).findall('.//s:row',NS):
      cells=[]
      for c in row.findall('s:c',NS):
       v=c.find('s:v',NS);txt=v.text if v is not None else None;typ=c.get('t')
       if typ=='s' and txt is not None:txt=strings[int(txt)]
       elif typ=='inlineStr':txt=''.join(c.find('s:is',NS).itertext())
       cells.append(dict(cell=c.get('r'),type=typ,value_literal=txt,formula_literal=c.find('s:f',NS).text if c.find('s:f',NS) is not None else None))
      decoded.append(dict(source_id=sid,source_zip_member=name2,source_row=row.get('r'),cells=cells,no_final_graphs=True))
    r.update(native_parser='all worksheet native XML rows including styled-empty cells',rows=len(decoded),outputs=[save(sid+'/'+name+'.rows.jsonl',decoded,True)])
  elif suffix=='.xls':r.update(native_parser=None,disposition='opaque_legacy_binary_native_workbook_retained_complete; data kind/assay relevance pending independent review',rows=None)
  else:continue
  records.append(r)
output=save('source_preprocessing_manifest.json',dict(task_id=TASK,epoch_id='SS-E02',agent_role='A4 native source preprocessing',input_manifest_path=str((BASE/'common_source_raw_only_input_v2.json').relative_to(ROOT)),input_manifest_sha=sha(BASE/'common_source_raw_only_input_v2.json'),created_at=now(),records=records,read_other_extractor_output=False,read_model_outcomes=False,read_future_fresh=False,contains_final_graphs=False,all_actual_original_files_retained=True))
print(json.dumps({'manifest':output,'native_records':len(records),'PDF_pages':sum(r.get('physical_pages',0) for r in records),'DOCX_tables':sum(r.get('tables',0) for r in records)},ensure_ascii=False,indent=2))

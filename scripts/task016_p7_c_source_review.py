"""A4 source text inventory from immutable per-round G5 raw inputs only."""
import json,sys,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain,save_json
base=ROOT/"outputs/task016-p7/v1/C/E01"
def review(roundno):
 folder=base/f"stages/batches/R{roundno}";stage=folder/"G5_FRESH_HOLDOUT_ACQUIRE.json";verify_stage_chain(stage,sha_file(stage));inputp=folder/"fresh_source_input_manifest.json";m=json.loads(inputp.read_text());text=lambda x:' '.join(''.join(x.itertext()).split()) if x is not None else ''
 for s in m['sources']:
  pointer=s['xml_pointer'];p=ROOT/pointer['path']
  if sha_file(p)!=pointer['sha256']:raise RuntimeError('raw drift')
  tree=E.fromstring(p.read_bytes());paragraphs=[dict(location=f'abstract//p[{i+1}]',text=text(x)) for i,x in enumerate(tree.findall('.//abstract//p'))]+[dict(location=f'body//p[{i+1}]',text=text(x)) for i,x in enumerate(tree.findall('.//body//p'))]
  figures=[dict(id=x.get('id'),caption=text(x),links=[dict(href=z.get('{http://www.w3.org/1999/xlink}href'),kind=z.tag) for z in x.iter() if z.tag in ('graphic','media','ext-link')]) for x in tree.findall('.//fig')]
  tables=[dict(id=x.get('id'),text=text(x)) for x in tree.findall('.//table-wrap')]
  attachments=[dict(kind=x.tag,text=text(x),href=x.get('{http://www.w3.org/1999/xlink}href')) for x in tree.iter() if x.tag in ('supplementary-material','media','ext-link')]
  result=dict(task='TASK-016-P7',agent_role='A4',pmcid=s['pmcid'],input_manifest_sha256=sha_file(inputp),source_pointer=pointer,title=text(tree.find('.//article-title')),paragraphs=paragraphs,figures=figures,tables=tables,attachments=attachments,read_other_extractor_output=False,read_model_outcome=False,evidence_eligible=False)
  save_json(base/f'fresh/R{roundno}/A4_source_review/{s["pmcid"]}.source_text.json',result,immutable=True)
  print(json.dumps(dict(pmcid=s['pmcid'],title=result['title'],paragraph_count=len(paragraphs),figures=[{'id':x['id'],'caption':x['caption'][:1800]} for x in figures],abstract=[x['text'] for x in paragraphs if 'abstract' in x['location']]),ensure_ascii=False))
if __name__=='__main__':review(int(sys.argv[1]))

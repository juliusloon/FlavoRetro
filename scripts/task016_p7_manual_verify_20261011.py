"""Independent byte/anchor and scope-boundary audit for manual P7 documentary batch."""
from __future__ import annotations
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write
TASK='TASK-016-P7';DIR=ROOT/'outputs/task016-p7/v1/manual_grabbed_intake_20261011'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check(test,msg,details=None):
 if not test:raise RuntimeError(msg)
 results.append({'check':msg,'passed':True,'details':details})
def output(name,obj):
 rel='outputs/task016-p7/v1/manual_grabbed_intake_20261011/'+name
 p=ROOT/rel
 if p.exists():raise RuntimeError('immutable file exists '+rel)
 write(TASK,rel,json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 return {'path':rel,'sha256':sha(p)}
def main():
 global results
 results=[]
 inv=json.loads((DIR/'custody_manifest.json').read_text())
 sc=json.loads((DIR/'source_scope_screen.json').read_text())
 pre=json.loads((DIR/'documentary_review_precontract.json').read_text())
 check(len(inv['source_files'])==23,'all 23 custody entries present')
 check(len(sc['reviews'])==12,'12 numbered documentary screens')
 check(sha(DIR/'custody_manifest.json')==pre['input_manifest']['sha256'],'review input bound to exact custody manifest')
 check(sha(DIR/'documentary_review_precontract.json')==sc['review_precontract']['sha256'],'precontract hash bound to review')
 for fam in ('C','SS'):
  g4=inv['G4_current_sha'][fam]
  check(sha(ROOT/g4['path'])==g4['sha256'],fam+' G4 frozen stage SHA unchanged')
 source_map={}
 for row in inv['source_files']:
  p=ROOT/row['local_custody'];orig=ROOT/row['source_original']
  check(p.is_file() and sha(p)==row['sha256'],row['number']+' raw SHA matches '+p.name[:30])
  check(orig.is_file() and sha(orig)==row['sha256'],row['number']+' user original remains unchanged '+p.name[:30])
  check(p.stat().st_mode & 0o222 ==0,row['number']+' archive read-only '+p.name[:30])
  source_map.setdefault(row['number'],[]).append(row)
 for rv in sc['reviews']:
  matches=[r for r in source_map[rv['number']] if r['sha256']==rv['sha256'] and r['local_custody']==rv['raw_pointer']]
  check(len(matches)==1,'source and reported screen SHA unique for '+rv['number'])
  p=ROOT/matches[0]['local_custody']
  proc=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True)
  check(proc.returncode==0 and len(proc.stdout)>0,'PDF extractor returns readable text '+rv['number'])
  pages=[x for x in proc.stdout.decode('utf-8',errors='replace').split('\f') if x.strip()]
  for a in rv['cited_observation']:
   pg=pages[a['pdf_page']-1]
   check(sha_text(pg)==a['original_page_extracted_text_sha256'],'page text SHA '+rv['number']+' p'+str(a['pdf_page']))
   check(re.search(re.escape(a['anchor_literal']),pg,re.I) is not None,'anchor occurs on cited PDF page '+rv['number'])
  check(rv['fresh_target_admitted'] is False and not rv['full_product_acceptor_donor_site_stereo_reference_graphs_verified'],'no false fresh/graph claim '+rv['number'])
 check(all(inv['slot_summary'][str(n).zfill(2)]['manual_access']=='unavailable_owner_reported_no_access' for n in range(13,17)),'13-16 explicitly access unavailable')
 check(sc['qualified_fresh_C']==0 and sc['qualified_fresh_SS']==0 and sc['scientific_ABE_cells']==0,'scientific status not upgraded')
 # Additional more discriminative Figure 5 original-data anchor for source 03.
 pdf=next(ROOT/r['local_custody'] for r in inv['source_files'] if r['number']=='03' and r['role']=='main_article_pdf')
 text=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
 pages=[x for x in text.split('\f') if x.strip()]
 fig=None
 for n,page in enumerate(pages,1):
  pp=' '.join(page.split())
  if 'P10, quercetin 3-O-rutinoside 7-O-glucoside' in pp and 'P13, kaempferol 3-O-rutinoside 7-O-glucoside' in pp:
   fig={'pdf_page':n,'page_text_sha256':sha_text(page),
        'figure_labels':['P10 quercetin 3-O-rutinoside 7-O-glucoside',
                         "P11 quercetin 3-O-rutinoside 4'-O-glucoside",
                         "P12 quercetin 3-O-rutinoside 3'-O-glucoside",
                         'P13 kaempferol 3-O-rutinoside 7-O-glucoside']}
   break
 check(fig is not None,'03 Figure 5 P10-P13 products localized to original text')
 add={'task':TASK,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source_number':'03','doi':'10.1021/acs.jafc.4c03824',
      'source_sha256':sha(pdf),'source_pointer':str(pdf.relative_to(ROOT)),
      'figure5_source_evidence':fig,
      'disposition':'reported_Figure5_rutinoside_substrate_products_are_aglycone_O7_O4prime_O3prime_not_inner_sugar_O2',
      'interpretation':'The directly labelled P10-P13 products add glucose to flavonol aglycone positions; this evidence does not establish frozen inner sugar O2 glycosylation. Do not generalize to every unreviewed assay/figure.',
      'G6_qualified_reaction':False,'fresh_holdout_admitted':False,
      'full_A4_A5_structural_extraction':False,'follow_up':'If desired, dual-independent figure-based full graph check before any reaction qualification.'}
 addref=output('source03_figure5_scope_addendum.json',add)
 aud={'task':TASK,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'agent_role':'A11_byte_and_documentary_anchor_recomputer',
      'scope':'independent raw SHA, first-stage bind, text anchor and 03 specific Figure 5 only; NOT chemical A4/A5 or formal evaluation',
      'checks':results,'passed':len(results),'failed':0,
      'source03_addendum':addref,'fresh_C':0,'fresh_SS':0,'G7':False,'scientific_ABE_cells':0}
 r=output('independent_A11_bounded_verification.json',aud)
 print(json.dumps({'checks_passed':len(results),'failed':0,'source03_addendum':addref['path'],'audit':r['path'],'fresh':{'C':0,'SS':0}},ensure_ascii=False))
def sha_text(s):return hashlib.sha256(s.encode('utf-8')).hexdigest()
if __name__=='__main__':main()

"""A3 reconciliation and bounded documentary G6 question-set for owner R3 13–16.
No atomgraphs or prospective holdout claims; original and v1 are immutable.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,html,json,re,subprocess,sys,unicodedata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';BASE=Path('outputs/task016-p7/v1')
IN=BASE/'manual_grabbed_R3_20261011/R3_custody_receipt.json'
HTTP=BASE/'manual_grabbed_R3_A3_20261011/A3_http_identity_ledger.json'
OLD=BASE/'verification-v32-pending-original-source-inventory/named_pending_original_inventory.json'
OUTPUT=BASE/'manual_grabbed_R3_A3_reconciled_20261011'
ANNOT={
'13':('Free Reversibility','reversib','flavonol_3O_UDPGlc_transfer_and_reverse',
  'Sutter/Grisebach flavonol 3-O glucose transfer reversible with UDP; does not establish frozen SS inner sugar O2 glucosylation.'),
'14':('Biosynthesis of Flavonol Triglucosides','3-diglucoside','sequential_flavonol_3O_mono_di_tri_glucosides',
  'Pea enzyme extract converts flavonol aglycone through 3-O-mono/di to triglucosides; bond atom O2, sugar branching, stereochemistry and exact graph not determined by this text-level read.'),
'15':('Flowers of Petunia hybrida','glucosylation','flavonol_and_anthocyanidin_aglycone_3O',
  'Petunia 3-O glycosyltransferase activity on flavonols/anthocyanidins; aglycone 3-O does not establish sugar residue O2.'),
'16':('Chrysanthemum segetum','7-hydroxyl','flavonol_aglycone_7O',
  'Chrysanthemum 7-O glycosyltransferase adds glucose at flavonol 7-OH; not sugar-residue O2.')
}
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def norm(s):
 s=unicodedata.normalize('NFKD',html.unescape(re.sub(r'<[^>]*>',' ',str(s or '')))).casefold()
 s=''.join(t for t in s if not unicodedata.combining(t))
 return re.sub(r'[^a-z0-9]+',' ',s).strip()
def dump(path,val):
 rel=OUTPUT/path
 if (ROOT/rel).exists():raise RuntimeError('immutable output')
 write(T,str(rel),json.dumps(val,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return {'path':str(rel),'sha256':sha(rel)}
def main():
 if (ROOT/OUTPUT).exists():raise RuntimeError('batch already exists')
 inv=json.loads((ROOT/IN).read_text())
 payload=json.loads((ROOT/HTTP).read_text())
 legacy=json.loads((ROOT/OLD).read_text())
 assert len(inv['rows'])==4 and len(payload['results'])==4
 out=[]
 for s in inv['rows']:
  no=s['no']
  x=next(x for x in payload['results'] if x['source_no']==no)
  m=x['metadata']
  assert x['status_code']==200 and m and m['DOI'].casefold()==s['requested_DOI'].casefold()
  assert next(z for z in legacy['items'] if z['source_identifier']==s['requested_DOI'])['family']=='SS'
  p=ROOT/s['preserved_raw'];assert sha(s['preserved_raw'])==s['sha256']
  # Use original first-page layout, retain 13 year-197% OCR damage explicitly.
  first=subprocess.run(['pdftotext','-f','1','-l','1','-layout',str(p),'-'],check=True,capture_output=True,text=True).stdout
  full=subprocess.run(['pdftotext','-layout',str(p),'-'],check=True,capture_output=True,text=True).stdout
  pages=[pg for pg in full.split('\f') if pg.strip()]
  tokens={t for t in norm(m['title']).split() if len(t)>2 and t not in {'the','and','from','for','into','involved'}}
  all_first=set(norm(first).split())
  matches=sorted(tokens & all_first)
  coverage=len(matches)/max(1,len(tokens))
  article_ref=f"{m['volume']}" in first and bool(re.search(re.escape(str(m['page']).split('-')[0]),re.sub(r'\s+','',first)))
  if coverage<0.72 or not article_ref:raise RuntimeError(f'A3_imprint_conflict_{no}:title={coverage:.2f},article={article_ref}')
  if str(m['year'])!=s['publication_year_expected']:raise RuntimeError('official year conflict '+no)
  title,needle,label,summary=ANNOT[no]
  matches=[]
  for i,page in enumerate(pages,1):
   mo=re.search(re.escape(needle),page,re.I)
   if mo:
    excerpts=' '.join(page[max(0,mo.start()-120):mo.end()+230].split())[:390]
    matches.append({'page':i,'anchor':needle,'excerpt':excerpts,
      'page_text_sha256':hashlib.sha256(page.encode()).hexdigest()})
  if not matches:raise RuntimeError('missing chemistry text anchor '+no)
  out.append({'number':no,'inventory_family':'SS','requested_DOI':s['requested_DOI'],
   'file':s['preserved_raw'],'file_sha256':s['sha256'],'bytes':s['bytes'],
   'original_pdf_pages':s['pdf_pages'],'metadata_DOI':m['DOI'],
   'metadata_title':m['title'],'metadata_journal':m['journal'],'metadata_year':m['year'],
   'metadata_volume':m['volume'],'metadata_pages':m['page'],
   'PDF_title_token_coverage':round(coverage,4),'PDF_volume_first_page_found':True,
   'PDF_first_page_start_page_found':True,
   'PDF_original_year_ocr_partial':'197%' if no=='13' else None,
   'publisher_pdf_source_identity':'passed_title_volume_start_page_vs_official_metadata',
   'PDF_DOI_literal_not_required_for_1975_1997_articles':True,
   'chemical_screen_category':label,'chemical_text_anchor':matches[:2],
   'chemical_interpretation_provisional':summary,
   'historical_design_exposed':True,'prospective_fresh_eligible':False,
   'full_original_structure_figure_transcribed_twice':False,
   'reaction_atom_site_stereo_origin_complete':False,'G6_reaction_admitted':False,
   'do_not_conflate_3O_aglycone_with_inner_sugar_O2':True})
 old16=json.loads((ROOT/(BASE/'manual_grabbed_A3_reconciled_20261011/A3_owner_intake_inventory_reconciliation.json')).read_text())
 assert len(old16['owner_16_items'])==16 and sum(x['owner_provided_original'] for x in old16['owner_16_items'])==12
 res={'task':T,'at':now(),'phase':'R3_A3_historical_original_identity_13_16',
 'input_sha':{str(q):sha(q) for q in [IN,HTTP,OLD]},
 'publication_identity_pass':4,'historical_access_recovered':4,
 'historical_16_document_requests_fulfilled':16,'historical_16_document_requests_unavailable_remaining':0,
 'historical_source_not_assumed_scientifically_eligible':True,
 'full_P7_G5_fresh_discovery_completed':False,'full_P7_G6_reaction_qualification_completed':False,
 'R3_13_16':out,'source14_glycosyl_position_O2_not_verified':True,
 'source_chemistry_reaction_admitted':0,'fresh_SS':0,'fresh_C':0,
 'new_G7':False,'new_scientific_MCTS':0,'metrics':None,'G4_unchanged':True}
 rec=dump('R3_A3_4original_crosscheck_and_G6_documentary_questions.json',res)
 exposure=[{'task':T,'at':now(),'source_no':x['number'],'identifier':x['requested_DOI'],
   'original_path':x['file'],'original_sha256':x['file_sha256'],
   'exposure_class':'historical_previously_known_and_current_turn_scientific_summary_read',
   'first_page_read_before_local_R3_precontract':True,'fresh_candidate_eligible':False,
   'future_G7_must_be_consumed_as_anti_leakage_supplement':True,
   'chemical_graph_complete':False,'G7':False} for x in out]
 epath=OUTPUT/'R3_4original_permanent_exposure.jsonl'
 write(T,str(epath),'\n'.join(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in exposure)+'\n')
 erec=dump('R3_4original_exposure_receipt.json',{'task':T,'source_count':4,'source_sha':sha(epath),
     'original_development_exposure_12_preserved':True,'new_historical_exposure':4,'fresh':0,
     'G7_writer_manual_exposure_integration_required':True})
 event(T,'P7_R3_4historical_originals_A3_screen_verified',A3_sha256=rec['sha256'],exposure_sha256=sha(epath))
 print(json.dumps({'identity_pass':4,'documentary_access_closed_16_of_16':True,
   'scope14_O2_site_verified':False,'fresh':0,'receipt':rec['path'],'exposure_receipt':erec['path']},ensure_ascii=False))
if __name__=='__main__':main()

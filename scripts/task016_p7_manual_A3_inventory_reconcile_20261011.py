"""Independent A3 metadata-PDF identity and 16-slot original access reconciliation.
Uses frozen owner bytes and Crossref raw bytes. Does NOT read chemistry, infer structural graphs or mark fresh.
"""
import hashlib,html,json,re,subprocess,sys,unicodedata,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write
T='TASK-016-P7';D=Path('outputs/task016-p7/v1')
P=D/'manual_grabbed_intake_20261011/custody_manifest.json'
A=D/'manual_grabbed_A3_20261011/A3_raw_authoritative_metadata.json'
R=D/'manual_grabbed_A3_R2_20261011/A3_corrected_11.json'
I=D/'verification-v32-pending-original-source-inventory/named_pending_original_inventory.json'
OUT=D/'manual_grabbed_A3_reconciled_20261011'
MAN={'01':'10.1111/tpj.70932','02':'10.1021/acs.jafc.5c06227','03':'10.1021/acs.jafc.4c03824','04':'10.1021/acs.jafc.4c00488',
     '05':'10.1111/tpj.16898','06':'10.1039/c5ob01926e','07':'10.1039/c0ob00011f','08':'10.1039/c4cc00536h','09':'10.1002/bit.26491',
     '10':'10.1002/cbic.70486','11':'PMC7720146','12':'PMC2709393','13':'10.1016/0003-9861(75)90485-3',
     '14':'10.1515/znc-1979-9-1014','15':'10.1515/znc-1984-0609','16':'10.1515/znc-1997-3-403'}
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clean(s):
 s=html.unescape(re.sub(r'<[^>]*>',' ',str(s or '')))
 s=unicodedata.normalize('NFKD',s).casefold()
 s=''.join(x for x in s if not unicodedata.combining(x))
 return re.sub(r'[^a-z0-9]+',' ',s).strip()
def jread(p):return json.loads((ROOT/p).read_text())
def put(name,o):
 rel=OUT/name
 if (ROOT/rel).exists():raise RuntimeError('immutable output already exists')
 write(T,str(rel),json.dumps(o,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return str(rel)
def pdftext(p):
 v=subprocess.run(['pdftotext','-f','1','-l','2','-layout',str(p),'-'],capture_output=True)
 if v.returncode:raise RuntimeError('PDF extract failed')
 return v.stdout.decode('utf-8',errors='replace')
def main():
 if (ROOT/OUT).exists():raise RuntimeError('immutable output directory exists')
 manual=jread(P); a=jread(A); corr=jread(R); vint=jread(I)
 assert len(vint['items'])==16
 assert corr['official_DOI']=='10.1073/pnas.2012745117' and corr['status']==200
 refsrc={x['source_no']:x for x in a['sources']}
 out=[];count=0;unresolved=[];crossref_invalid=[]
 for no in [str(i).zfill(2) for i in range(1,17)]:
  original=MAN[no]
  mapping=[x for x in vint['items'] if x['source_identifier'].lower()==original.lower()]
  if len(mapping)!=1:raise RuntimeError('not unique original 16-slot identifier '+no)
  record=mapping[0]
  avail=manual['slot_summary'][no]
  if int(no)>=13:
   assert not any(x['number']==no for x in manual['source_files'])
   out.append({'owner_number':no,'inventory_identifier':original,'inventory_family':record['family'],
    'owner_provided_original':False,'owner_access_state':'permission_unavailable_not_a_chemical_rejection',
    'legacy_original_source_not_qualified':True,'G6_chemistry_status':'not_started','fresh':False})
   continue
  # Correct owner-number 10 family to actual v32 C. The old summary is preserved as historical error.
  stored_family=avail['family_hint']
  if stored_family!=record['family']:unresolved.append({'number':no,'prior_family_hint':stored_family,'v32_inventory_family':record['family'],'action':'effective family set to frozen inventory family'})
  role='supporting_pdf' if no=='10' else 'main_article_pdf'
  file=next(x for x in manual['source_files'] if x['number']==no and x['role']==role)
  text=pdftext(ROOT/file['local_custody'])
  info=refsrc[no]
  m=corr if no=='11' else info['metadata']
  if not m:raise RuntimeError('authoritative metadata missing for '+no)
  doi=m['official_DOI'] if no=='11' else m['DOI']
  target_doi= '10.1073/pnas.2012745117' if no=='11' else info['expected_DOI']
  if doi.lower()!=target_doi.lower():crossref_invalid.append(no)
  title=m['title']
  nt=set(clean(title).split()); nft=set(clean(text).split())
  stop={'a','an','of','the','and','in','to','for','on','from','by','with','or','at','as','using'}
  nts={t for t in nt if t not in stop and len(t)>1}
  overlap=sorted(nts & nft)
  ratio=len(overlap)/len(nts) if nts else 0
  # The long first pages sometimes hyphenate flavonol names; hard minimum, no backfilling.
  literal_doi_in_pdf=target_doi.lower() in text.lower()
  positive=(no!='10' and literal_doi_in_pdf and ratio>=0.72 and doi.lower()==target_doi.lower())
  special=(no=='10' and ('UGT707B2' in text) and ('Iris tectorum' in text))
  if positive:count+=1
  if no!='10' and not positive:unresolved.append({'number':no,'doi_literal':literal_doi_in_pdf,'title_token_coverage':ratio})
  out.append({'owner_number':no,'inventory_identifier':original,'inventory_family':record['family'],
   'prior_manual_family_hint':stored_family,'owner_provided_original':True,
   'main_or_support':role,'file':file['local_custody'],'file_sha':file['sha256'],
   'metadata_DOI':doi,'metadata_title':title,'metadata_journal':m['journal'],
   'metadata_publisher':m.get('publisher'),'title_normalized_token_overlap':round(ratio,5),
   'title_overlap_tokens':overlap,'publisher_pdf_DOI_literal':literal_doi_in_pdf,
   'authoritative_metadata_DOI_match':doi.lower()==target_doi.lower(),
   'bibliographic_publisher_pdf_DOI_title_crosscheck':'pass' if positive else ('SI_related_title_only_pending_DOI_attachment_link' if special else 'pending'),
   'owner_access_status':'local_original_available','source_qualification':'not_chemical_reaction_qualified',
   'structure_and_assay_qualification':'not_completed','fresh':False,
   'full_A3_journal_year_volume_page':'present_in_raw_metadata_not_independently_all_reconciled'})
 assert not crossref_invalid
 assert len(out)==16 and count>=9
 physical={'v1_Crossref_HTTP':12,'v2_corrected_DOI_HTTP':1,'HTTP_total':13,
 'bytes_v1':sum(x['bytes'] for x in jread(D/'manual_grabbed_A3_20261011/physical_HTTP_ledger.json')['records']),
 'bytes_v2':corr['bytes'],'not_a_corpus_exhaustion_round':True}
 summary={'task':T,'at':now(),'status':'A3_original_publication_identity_crosscheck_completed_for_main_PDFs',
 'source_input_SHA':{str(p):sha((ROOT/p).read_bytes()) for p in (P,A,R,I)},
 'A3_crossref_HTTP':physical,'owner_16_items':out,
 'main_article_PDF_identifiers_checked':11,'main_article_publisher_PDF_DOI_title_pass':count,
 'SI_only_doctype_related_but_publisher_DOI_attachment_unverified':1,
 'only_access_unavailable_numbers':['13','14','15','16'],'prior_11_incorrect_DOI': '10.1073/pnas.202012745',
 'correct_11_DOI':'10.1073/pnas.2012745117','v1_HTTP404_not_erased':True,
 'prior_10_family_misclassified':'SS','correct_10_v32_inventory_family':'C',
 'corrections_or_pending':unresolved,'source_records_added_to_fresh':0,
 'formal_G6_full_graph_reaction_admission':0,'scientific_ABE_cells':0,'metrics':None,
 'remaining_documentary_non_access_items':4,
 'source_level_only_not_human_or_independent_chemistry':True}
 dest=put('A3_owner_intake_inventory_reconciliation.json',summary)
 print(json.dumps({'main_pass':count,'main_total':11,'SI_only_pending':1,'manual_access_available':12,'manual_unavailable':4,'corrections':unresolved,'file':dest},ensure_ascii=False))
if __name__=='__main__':main()

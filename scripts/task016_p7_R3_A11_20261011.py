"""Independent raw-recompute of owner historical-original R3 four-PDF custody / Crossref identity.
Checks mechanical source pointers, not chemical structure eligibility.
"""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write
B=Path('outputs/task016-p7/v1');O=B/'manual_grabbed_R3_A3_reconciled_20261011'
def get(p):return json.loads((ROOT/p).read_text())
def sha(p):
 h=hashlib.sha256()
 with (ROOT/p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
checks=[]
def ck(x,msg):
 if not x:raise RuntimeError('A11_R3_FAIL '+msg)
 checks.append(msg)
def main():
 r=get(O/'R3_A3_4original_crosscheck_and_G6_documentary_questions.json')
 raw=get(B/'manual_grabbed_R3_20261011/R3_custody_receipt.json')
 http=get(B/'manual_grabbed_R3_A3_20261011/A3_http_identity_ledger.json')
 expo=[json.loads(x) for x in (ROOT/O/'R3_4original_permanent_exposure.jsonl').read_text().splitlines() if x.strip()]
 old16=get(B/'verification-v32-pending-original-source-inventory/named_pending_original_inventory.json')
 ck(len(r['R3_13_16'])==4,'four_source_identity_records')
 ck(len(raw['rows'])==4,'four_owner_custody_records')
 ck(len(http['results'])==http['planned']==http['executed']==4,'four_crossref_calls_conserved')
 ck(len(expo)==4,'four_permanent_exposure_records')
 ck(all(i['family']=='SS' for i in old16['items'] if i['source_identifier'] in [x['requested_DOI'] for x in r['R3_13_16']]),'frozen_v32_SS_family')
 for row in r['R3_13_16']:
  no=row['number'];other=next(v for v in raw['rows'] if v['no']==no)
  req=next(v for v in http['results'] if v['source_no']==no)
  ex=next(v for v in expo if v['source_no']==no)
  ck(sha(row['file'])==row['file_sha256'],'raw_preserved_'+no)
  ck(sha(other['origin'])==row['file_sha256'],'source_original_unchanged_'+no)
  ck((ROOT/row['file']).stat().st_mode&0o222==0,'archive_read_only_'+no)
  ck(row['bytes']==(ROOT/row['file']).stat().st_size,'byte_count_'+no)
  ck(req['status_code']==200 and req['metadata']['DOI']==row['requested_DOI'],'crossref_official_DOI_'+no)
  ck(sha(req['raw']['path'])==req['raw']['sha256'],'crossref_raw_SHA_'+no)
  ck(row['PDF_title_token_coverage']>=0.72 and row['PDF_volume_first_page_found'],'pdf_title_and_vol_'+no)
  text=subprocess.run(['pdftotext','-layout',str(ROOT/row['file']),'-'],capture_output=True,text=True,check=True).stdout
  pages=[x for x in text.split('\f') if x.strip()]
  ck(len(pages)==row['original_pdf_pages'],'page_count_'+no)
  for a in row['chemical_text_anchor']:
   page=pages[a['page']-1]
   ck(hashlib.sha256(page.encode()).hexdigest()==a['page_text_sha256'],'page_SHA_'+no+'_'+str(a['page']))
   ck(re.search(re.escape(a['anchor']),page,re.I) is not None,'page_anchor_'+no+'_'+str(a['page']))
  ck(ex['original_sha256']==row['file_sha256'] and ex['fresh_candidate_eligible'] is False,'source_history_nonfresh_'+no)
  ck(row['G6_reaction_admitted'] is False,'G6_cannot_promote_'+no)
 for name,freeze in [('C','outputs/task016-p7/v1/C/E02/stages/G4_SCOPE_FREEZE.json'),('SS','outputs/task016-p7/v1/SS/E02/stages/G4_SCOPE_FREEZE.json')]:
  want={'C':'09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46','SS':'a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f'}[name]
  ck(sha(freeze)==want,name+' G4_SHA_unchanged')
 ck(r['historical_16_document_requests_unavailable_remaining']==0,'16_original_request_gaps_closed')
 ck(r['full_P7_G5_fresh_discovery_completed'] is False,'G5_fresh_discovery_still_open')
 ck(r['source_chemistry_reaction_admitted']==0 and r['fresh_C']==0 and r['fresh_SS']==0,'science_gate_not_falsely_passed')
 result={'task':'TASK-016-P7','role':'A11_independent_raw_byte_and_imprint_anchor_checker',
 'passed':len(checks),'failed':0,'checks':checks,
 'input_result_sha256':sha(O/'R3_A3_4original_crosscheck_and_G6_documentary_questions.json'),
 'source_13_16_PDF_identity':4,'historical_access_list':'16_of_16_received',
 'scientific_independent_chemistry':'not_done','fresh':0,'A_B_E_cells':0,'metrics':None}
 rel=O/'A11_R3_identity_custody_check.json'
 if (ROOT/rel).exists():raise RuntimeError('immutable_output_exists')
 write('TASK-016-P7',str(rel),json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'A11_checks':len(checks),'failed':0,'path':str(rel)}))
if __name__=='__main__':main()

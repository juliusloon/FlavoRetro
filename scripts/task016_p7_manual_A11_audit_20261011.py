"""A11 independent bounded recheck of A3 effective identity, physical receipts and frozen-state invariants."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write
D=Path('outputs/task016-p7/v1');O=D/'manual_grabbed_A3_reconciled_20261011'
def sha(p):
 h=hashlib.sha256()
 with (ROOT/p).open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def data(p):return json.loads((ROOT/p).read_text())
checks=[]
def check(cond,message):
 if not cond:raise RuntimeError('A11_FAIL '+message)
 checks.append({'name':message,'passed':True})
def main():
 c=data(O/'A3_owner_intake_inventory_reconciliation.json')
 inv=data(D/'manual_grabbed_intake_20261011/custody_manifest.json')
 v1=data(D/'manual_grabbed_A3_20261011/A3_raw_authoritative_metadata.json')
 rawledger=data(D/'manual_grabbed_A3_20261011/physical_HTTP_ledger.json')
 r2=data(D/'manual_grabbed_A3_R2_20261011/A3_corrected_11.json')
 original=data(D/'verification-v32-pending-original-source-inventory/named_pending_original_inventory.json')
 check(len(c['owner_16_items'])==16,'16 historical inventory slots mapped')
 check(len(rawledger['records'])==12,'R1 12 actual HTTP planned/executed')
 check(r2['HTTP']==1,'R2 one corrected DOI request counted')
 check(rawledger['planned']==rawledger['attempted']==12,'R1 plan/execution conservation')
 check(c['A3_crossref_HTTP']['HTTP_total']==13,'total visible HTTP 13')
 check(sum(q['bytes'] for q in rawledger['records'])==c['A3_crossref_HTTP']['bytes_v1'],'R1 byte conservation')
 check(r2['bytes']==c['A3_crossref_HTTP']['bytes_v2'],'R2 byte conservation')
 check(r2['v1_incorrect_DOI_HTTP404_kept'],'old false DOI 404 preserved explicitly')
 check(r2['official_DOI']=='10.1073/pnas.2012745117','corrected PNAS DOI from PDF + publisher metadata')
 for q in rawledger['records']:
  if q.get('raw'):
   check(sha(q['raw']['path'])==q['raw']['sha256'],'R1 raw checksum '+q['source_no'])
 check(sha(r2['raw_pointer']['path'])==r2['raw_pointer']['sha256'],'R2 raw checksum')
 sr={r['source_no']:r for r in v1['sources']}
 for r in c['owner_16_items']:
  n=r['owner_number']
  matches=[x for x in original['items'] if x['source_identifier'].lower()==r['inventory_identifier'].lower()]
  check(len(matches)==1,'source '+n+' linked to single v32 entry')
  if int(n)>12:
   check(r['owner_provided_original'] is False and r['owner_access_state']=='permission_unavailable_not_a_chemical_rejection','13-16 unpermitted remain blocked '+n)
   continue
  check(sha(r['file'])==r['file_sha'],'owner source PDF checksum '+n)
  if n=='10':
   check(r['inventory_family']=='C' and r['prior_manual_family_hint']=='SS','10 family correction documented')
   check(r['bibliographic_publisher_pdf_DOI_title_crosscheck'].startswith('SI_related'),'10 SI attachment link not over-certified')
  else:
   check(r['bibliographic_publisher_pdf_DOI_title_crosscheck']=='pass','main source official identity '+n)
   check(r['authoritative_metadata_DOI_match'] and r['publisher_pdf_DOI_literal'],'main DOI literal and authoritative match '+n)
   check(r['title_normalized_token_overlap']>=0.72,'main title coverage '+n)
   rid='10.1073/pnas.2012745117' if n=='11' else sr[n]['metadata']['DOI']
   check(r['metadata_DOI'].lower()==rid.lower(),'main original Crossref DOI '+n)
  check(r['fresh'] is False and r['structure_and_assay_qualification']=='not_completed','source not falsely fresh '+n)
 for axis in ('C','SS'):
  x=inv['G4_current_sha'][axis]
  check(sha(x['path'])==x['sha256'],'G4 original SHA not changed '+axis)
 check(c['source_records_added_to_fresh']==0,'no fresh sources admitted')
 check(c['formal_G6_full_graph_reaction_admission']==0,'no G6 complete graph falsely admitted')
 out={'task':'TASK-016-P7','agent_role':'A11_raw_to_result_recomputer','scope':'source identity and custody; no chemical graph, G6 or human approval',
      'checks':checks,'passed':len(checks),'failed':0,
      'result_sha256':sha(O/'A3_owner_intake_inventory_reconciliation.json'),
      'fresh_C':0,'fresh_SS':0,'scientific_ABE_cells':0}
 rel=O/'A11_independent_originals_identity_audit.json'
 if (ROOT/rel).exists():raise RuntimeError('immutable')
 write('TASK-016-P7',str(rel),json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'A11_pass':len(checks),'A11_fail':0,'result':str(rel)},ensure_ascii=False))
if __name__=='__main__':main()

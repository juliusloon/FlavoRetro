"""TASK-016-P7 owner PDF 13-16 immutable intake. Historical/design-only; no G6 fresh."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
TASK='TASK-016-P7'; REL=Path('outputs/task016-p7/v1/manual_grabbed_R3_20261011')
DEST=Path('data/raw/task016-p7/manual_grabbed_20261011/R3_13_16')
SOURCE=Path('temp/manual_grabbed')
RECORDS={
'13':('13-sutter1975.pdf','10.1016/0003-9861(75)90485-3','Free Reversibility of the UDP-Glucose: Flavonol 3-O-Glucosyltransferase Reaction','1975'),
'14':('14-10.1515_znc-1979-9-1014.pdf','10.1515/znc-1979-9-1014','UDP-Glucose: Glucosyltransferase Activity Involved in the Biosynthesis of Flavonol Triglucosides in Pisum sativum L. Seedlings','1979'),
'15':('15-10.1515_znc-1984-0609.pdf','10.1515/znc-1984-0609','Common Identity of UDP-Glucose:Anthocyanidin 3-O-Glucosyltransferase and UDP-Glucose: Flavonol 3-O-Glucosyltransferase in Flowers of Petunia hybrida','1984'),
'16':('16-10.1515_znc-1997-3-403.pdf','10.1515/znc-1997-3-403','UDP-Glucose: Flavonol 7-O-glucosyltransferase Activity in Flower Extracts of Chrysanthemum segetum','1997')}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def timestamp():return datetime.now(timezone.utc).isoformat()
def jwrite(name,obj):
 path=REL/name
 if (ROOT/path).exists():raise RuntimeError('IMMUTABLE_DESTINATION_ALREADY_EXISTS '+str(path))
 write(TASK,str(path),json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 return {'path':str(path),'sha256':sha(ROOT/path)}
def main():
 if (ROOT/REL).exists() or (ROOT/DEST).exists():raise RuntimeError('R3 already exists')
 base='outputs/task016-p7/v1/manual_grabbed_A3_reconciled_20261011/A3_owner_intake_inventory_reconciliation.json'
 frozen='outputs/task016-p7/v1/verification-v32-pending-original-source-inventory/named_pending_original_inventory.json'
 assert (ROOT/base).is_file() and (ROOT/frozen).is_file()
 plan={'task':TASK,'at':timestamp(),'source':'owner_user_supplied_four_HISTORIC_main_article_PDFs',
 'approval_type':'agent_delegated','source_numbers':list(RECORDS),
 'legacy_16_inventory_sha256':sha(ROOT/frozen),'prior_12_identity_receipt_sha256':sha(ROOT/base),
 'source_original_read_exposure':'assistant_already_read_first_page_excerpts_before_this_precontract_in_same_turn',
 'prospective_G5_before_first_scientific_read':False,
 'historical_development_exposure':True,'fresh_eligible':False,'G6_reaction_qualified':False,
 'source_identity_vs_chemistry_distinct':True,'do_not_change_frozen_G4':True,
 'permissions_and_redistribution':'owner_supplied_permission_not_redistribution_clearance',
 'HTTP_requests':0,'read_MCTS':False,'write_G7':False}
 pr=jwrite('precontract.json',plan)
 rows=[]
 for no,(filename,doi,title,year) in RECORDS.items():
  p=ROOT/SOURCE/filename
  if not p.is_file():raise FileNotFoundError(str(p))
  magic=p.open('rb').read(5)
  if magic != b'%PDF-':raise RuntimeError('NOT_PDF '+filename)
  original_hash=sha(p)
  dest=ROOT/DEST/filename
  dest.parent.mkdir(parents=True,exist_ok=True)
  shutil.copyfile(p,dest)
  if sha(dest)!=original_hash:raise RuntimeError('COPY_CHECKSUM_ERROR')
  dest.chmod(0o444)
  info=subprocess.run(['pdfinfo',str(dest)],capture_output=True,text=True,check=True)
  mo=re.search(r'^Pages:\s*(\d+)',info.stdout,re.M)
  if not mo:raise RuntimeError('PAGES_MISSING')
  text=subprocess.run(['pdftotext','-f','1','-l','1','-layout',str(dest),'-'],capture_output=True,text=True,check=True).stdout
  # A3 provisional imprint triage: real source title/pages/year must be reconciled with official DOI metadata later.
  if not text or len(text)<500:raise RuntimeError('NO_SUBSTANTIVE_FIRST_PAGE')
  key={'13':'Reversibility','14':'Triglucosides','15':'Petunia','16':'Chrysanthemum'}[no]
  if key.casefold() not in text.casefold():raise RuntimeError('PDF_HEADER_UNEXPECTED_'+no)
  row={'no':no,'requested_DOI':doi,'anticipated_title_for_verification':title,'publication_year_expected':year,
   'origin':str((SOURCE/filename)),'preserved_raw':str((DEST).relative_to(ROOT)),
   'bytes':p.stat().st_size,'sha256':original_hash,'pdf_pages':int(mo.group(1)),
   'PDF_magic':True,'title_header_anchor':key,'title_header_anchor_present':True,
   'full_article_text_available':True,'source_identity':'metadata_crosscheck_required',
   'prior_development_exposure':True,'fresh_holdout_admitted':False,
   'G6_structured_chemical_admission':False,'original_relicensed':False,
   'name_or_summary_not_reaction_complete':True}
  rows.append(row)
  event(TASK,'owner_original_R3_sha256_custody',number=no,origin=row['origin'],
        preserved=row['preserved_raw'],sha256=original_hash,bytes=row['bytes'],pages=row['pdf_pages'])
 receipt={'task':TASK,'at':timestamp(),'precontract':pr,'owner_PDF_13_16_count':4,
 'owner_source_original_immutable':True,'sha256_matches_all':True,'originals_unmodified':True,
 'new_bytes':sum(x['bytes'] for x in rows),'rows':rows,'numbered_access_gap_remaining':0,
 'publication_identity': 'not_yet_A3_crossref_verified',
 'fresh_C':0,'fresh_SS':0,'new_G7':False,'new_MCTS':0,'metrics':None,
 'already_science_exposed_pre_intake':True,'human_reviewed':False}
 out=jwrite('R3_custody_receipt.json',receipt)
 print(json.dumps({'numbered_main_pdf_received':4,'bytes':receipt['new_bytes'],'pages':{x['no']:x['pdf_pages'] for x in rows},'receipt':out['path']},ensure_ascii=False))
if __name__=='__main__':main()

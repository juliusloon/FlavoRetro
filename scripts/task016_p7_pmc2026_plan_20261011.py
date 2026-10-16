"""Preregister first prospective C source original acquisition: PMC13564134 isoorientin.
Do not read JATS body until G5 stage binds its original SHA.
"""
from pathlib import Path
import hashlib,json,datetime,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
M=O/'G5_metadata_executed.json'
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
 m=json.loads((ROOT/M).read_text())
 v=[x for x in m['metadata_only_candidates'] if x.get('DOI')=='10.1016/j.abiote.2026.100085']
 assert len(v)==1 and v[0]['PMCID']=='PMC13564134' and v[0]['family']=='C'
 # historical scan lexical, NO study article science read
 roots=[B/'exposure_ledger.jsonl',B/'governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl',
        B/'manual_grabbed_A3_reconciled_20261011/permanent_manual_science_exposure_v1.jsonl',
        B/'manual_grabbed_R3_A3_reconciled_20261011/R3_4original_permanent_exposure.jsonl']
 counts={}
 for p in roots:
  s=(ROOT/p).read_text().lower()
  counts[str(p)]={'DOI_exact_occurrences':s.count('10.1016/j.abiote.2026.100085'),
                  'PMCID_exact_occurrences':s.count('pmc13564134'),'sha256':sha(p)}
 plan={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'source_family':'C','source_axis_scope_sha256':sha(B/'C/E02/scope_manifest.json'),
  'frozen_G4_sha256':sha(B/'C/E02/stages/G4_SCOPE_FREEZE.json'),
  'metadata_source':str(M),'metadata_SHA':sha(M),'source_DOI':v[0]['DOI'],
  'source_PMCID':v[0]['PMCID'],'official_PMC_fullTextXML_URL':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13564134/fullTextXML',
  'source_identity_first':'require JATS DOI PMCID title original verification',
  'plan_HTTP_max':1,'per_object_bytes_max':5000000,'no_user_credentials_or_paywall_bypass':True,
  'scientific_content_to_be_read_ONLY_after_original_download_and_G5_SHA_stage_freeze':True,
  'candidate_prior_exposure_exact_lexical_counts':counts,
  'exact_tokens_not_proof_of_alias_or_cohort_closure':True,
  'source_qualifed_not_claimed':True,'fresh_not_claimed':True,'G6_full_graph_not_claimed':True,
  'full_A4_A5_source_graph_extraction_mandatory':True,'read_model_outcomes':False,
  'new_source_model_MCTS':0}
 p=O/'C_PMC13564134_G5_original_acquisition_precontract.json'
 if (ROOT/p).exists():raise RuntimeError('prereg exists')
 write(T,str(p),json.dumps(plan,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 event(T,'C_PMC13564134_G5_original_acquisition_plan',plan_sha256=sha(p),
      source_original_science_read=False)
 print(json.dumps({'preregistered':str(p),'prior_exact_exposure_counts':counts},ensure_ascii=False))
if __name__=='__main__':main()

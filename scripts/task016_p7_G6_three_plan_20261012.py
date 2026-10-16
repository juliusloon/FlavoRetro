"""P7 precontract: resolve 3 G6 source/closure gaps without upgrading fresh.
Part 2 may fetch authoritative chemical structures ONLY after separate URL preregistration.
"""
from pathlib import Path
import json,datetime,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
O=B/'G6_three_decisions_20261012_v1'
files={
 'A6_prior_exposure':B/'SS/E01_permanent_exposure/permanent_chemical_exposure_ledger.jsonl',
 'A6_prior_exposure_v2':B/'SS/E01_permanent_exposure/v2/permanent_chemical_exposure_ledger.jsonl',
 'A6_prior_exposure_effective':B/'epochs/SS-E01/closure_resolution_v1/effective_permanent_exposure_ledger.jsonl',
 'prior_reaction_eligibility':B/'reaction_eligibility_ledger_v1/ledger_summary_v1.json',
 'C_G5':B/'prospective_G6_round_20261011_v1/C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json',
 'C_original':Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML'),
 'Iris_official_PMC_HTML':Path('data/raw/task016-p7/C/E02/C-E02-R45-Iris-public-body-access-v1/C-E02-RAW-42da14340a624d77a5153eeb97a7846a.article_version'),
 'Iris_official_SI_advertised_plan':B/'C/E02/fresh/C-E02-R46-Iris-advertised-assets-v1/advertised_asset_plan.json',
 'Iris_owner_SI':Path('data/raw/task016-p7/manual_grabbed_20261011/10-SI-cbic70486-sup-0001-suppdata-s1.pdf'),
 'Pea_original_PDF':Path('data/raw/task016-p7/manual_grabbed_20261011/R3_13_16/14-10.1515_znc-1979-9-1014.pdf'),
 'G4_C':B/'C/E02/stages/G4_SCOPE_FREEZE.json',
 'G4_SS':B/'SS/E02/stages/G4_SCOPE_FREEZE.json'
}
def sha(p):
 h=hashlib.sha256()
 with (ROOT/p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def main():
 if (ROOT/O).exists():raise RuntimeError('immutable path exists')
 for v in files.values():assert (ROOT/v).is_file(),str(v)
 pre={'task':T,'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'approval_type':'owner_explicit_request_three_decisions','human_reviewed':False,
  'inputs':{k:{'path':str(v),'sha256':sha(v)} for k,v in files.items()},
  'A6_name_only':'12 original record content+history provenance check; name metadata not a complete reaction; ruling only about name evidence, not complete closure',
  'source10':'decide official PMCID to SI title/advertised attachment linkage from existing caches; distinguish binary identity',
  'source14':'decide whether extant 1979 original states specific inner-sugar O2; no guessed site; no paper-wide reaction exclusion',
  'PMC13564134_graph':'original JATS primary source names + separately preregistered PubChem authoritative records, disjoint A4/A5 extraction; no hand written molecule',
  'preexisting_studies_were_scientifically_exposed':True,
  'originals_read_only':True,'no_G4_or_existing_G6_edit':True,
  'no_G7_or_runtime_model_outcome_read':True,
  'physical_HTTP_allowed_before_separate_query_plan':0,
  'fresh_admitted_at_start':0,'result_must_distinguish_fact_inference_missing':True}
 p=O/'three_workstreams_precontract.json'
 write(T,str(p),json.dumps(pre,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'P7_G6_three_workstreams_precontract',sha256=sha(p),file_count=len(files))
 print(json.dumps({'plan':str(p),'sha256':sha(p),'inputs':len(files)}))
if __name__=='__main__':main()

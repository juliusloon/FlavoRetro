"""Pre-register two-axis P7 fresh candidate metadata scouting before ANY NEW science reading.
Exactly three independent discovery mechanisms: EuropePMC indexed text, Crossref DOI search,
OpenAlex forward-citation chase of *already exposed* source articles. No full abstracts read.
This is G5 scouting only; 0 fresh reaction admission.
"""
from pathlib import Path
import hashlib,json,sys,datetime,urllib.parse
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1')
OUT=B/'prospective_G6_round_20261011_v1'
def sha(p):
 h=hashlib.sha256()
 with (ROOT/p).open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def entry(route,fam,q,url,why):
 return {'route':route,'family':fam,'query':q,'url':url,'purpose':why,
         'max_requests':1,'max_results':20,'read_abstracts':False,'science_body_read':False}
def main():
 if (ROOT/OUT).exists():raise RuntimeError('immutable')
 queries=[]
 ep=[
 ('C','TITLE_ABS:(flavone AND C-glycosyltransferase AND 6) OR TITLE_ABS:(flavonoid AND 6-C-glucosyltransferase)'),
 ('C','TITLE_ABS:(flavone AND direct AND C-glucosylation)'),
 ('SS','TITLE_ABS:(flavonol AND 2-O-glucosyltransferase AND glycoside)'),
 ('SS','TITLE_ABS:(flavonol AND glucoside AND glucosyltransferase AND sophoroside)')]
 for f,q in ep:
  url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(
      {'query':q,'format':'json','pageSize':20,'resultType':'core'})
  queries.append(entry('europepmc_fulltext_index',f,q,url,'indexed publication identity, not abstract chemical evidence'))
 cp=[('C','flavone 6-C-glycosyltransferase directly'),
     ('C','flavone C6 glycosylation flavonoid UDP-glycosyltransferase'),
     ('SS','flavonol 3-O-glucoside 2-O glucosyltransferase sophoroside'),
     ('SS','flavonol 3-O-galactoside 2-O glucosylation enzyme')]
 for f,q in cp:
  url='https://api.crossref.org/works?'+urllib.parse.urlencode(
      {'query.bibliographic':q,'rows':'20','select':'DOI,title,container-title,published,issued,type'})
  queries.append(entry('crossref_publisher_DOI_bibliography',f,q,url,'bibliographic title/DOI list, do not infer chemical reaction from name'))
 seeds=[('C','10.1074/jbc.M109.009258'),('SS','10.1021/acs.jafc.4c03824')]
 for f,doi in seeds:
  url='https://api.openalex.org/works/https://doi.org/'+urllib.parse.quote(doi,safe='/')
  queries.append(entry('openalex_forward_citation_network',f,doi,url,'resolve previously-exposed seed id for prospective citing literature list'))
 meta={'task':T,'timestamp':now(),'approval_type':'agent_delegated','no_human_reviewed_claim':True,
       'round':'one_dedicated_prospective_metadata_round','search_routes':3,
       'scopes':{f:{'G4_sha256':sha(B/f/'E02/stages/G4_SCOPE_FREEZE.json'),
                     'scope_sha256':sha(B/f/'E02/scope_manifest.json')} for f in ('C','SS')},
       'frozen_G4_inputs_protected':True,'previous_exposure_sha256':sha(B/'exposure_ledger.jsonl'),
       'current_manual_development_exposure_sha256':[sha(B/'manual_grabbed_A3_reconciled_20261011/permanent_manual_science_exposure_v1.jsonl'),
       sha(B/'manual_grabbed_R3_A3_reconciled_20261011/R3_4original_permanent_exposure.jsonl')],
       'prior_epoch_ledger_sha256':sha(B/'epoch_ledger.jsonl'),
       'name_and_source_alias_review_before_any_fresh':True,'candidate_meta_only_until_prospective_G5_SCIENCE_gate':True,
       'new_source_PDF_science_reads':0,'new_MCTS':0,'G7':False,
       'HTTP_requested_max':12,'page_max_per_query':1,'attachments_max':0,'download_max_bytes_per_request':500000,
       'queries':queries,'forward_citation_execute_only_after_seed_ID_metadata_verified':True,
       'allowed_provider_methods':['Crossref','EuropePMC','OpenAlex'],
       'failure_policy':'fail_or_defer; no access bypass; do not claim saturation from one round',
       'A4_A5_independent_extraction_for_qualified_originals':'not_started',
       'holdout_read':False,'model_outcome_read':False}
 p=OUT/'G5_metadata_query_plan.json'
 write(T,str(p),json.dumps(meta,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
 event(T,'prospective_G5_discovery_plan_frozen',path=str(p),sha256=sha(p),queries=len(queries),three_routes=True)
 print(json.dumps({'plan':str(p),'sha':sha(p),'queries':len(queries),'routes':3},ensure_ascii=False))
if __name__=='__main__':main()

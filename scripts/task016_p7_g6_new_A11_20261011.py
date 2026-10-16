"""A11 independent recomputation, SS metadata alias exclusion, C permanent exposure registration.
No source made fresh or full graph eligible. Existing archived originals and G4 are immutable.
"""
import hashlib,json,sys
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
from scripts.task016_p7_orchestrate import sha_file,verify_stage_chain
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'prospective_G6_round_20261011_v1'
R2=B/'prospective_G6_SS_targeted_metadata_R2_20261011'
SRC=Path('data/raw/task016-p7/prospective_G6_round_20261011_v1/PMC13564134.original_JATS_XML')
G5=O/'C-PMC13564134/stages/G5_FRESH_HOLDOUT_ACQUIRE.json'
G6=O/'C-PMC13564134/stages/G6_IDENTITY_STRUCTURE_ADMIT.json'
def load(p):return json.loads((ROOT/p).read_text())
def put(p,v):
 if (ROOT/p).exists():raise RuntimeError('immutable existing '+str(p))
 write(T,str(p),json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
checks=[]
def check(x,label):
 if not x:raise RuntimeError('INDEPENDENT_A11_FAIL '+label)
 checks.append(label)
def main():
 src=sha_file(ROOT/SRC)
 a3=load(O/'C_PMC13564134_A3_original_front_and_exposure.json')
 a4=load(O/'C_PMC13564134_A4_independent_source_read.json')
 a5=load(O/'C_PMC13564134_A5_independent_source_read.json')
 a6=load(O/'C_PMC13564134_A6_source_name_closure_and_graph_gaps.json')
 check(src==a3['original_sha256'],'official JATS original unchanged')
 check(src==a4['source_sha256']==a5['source_sha256'],'extractors source SHA bound')
 check(a4['agent_role']=='A4' and a5['agent_role']=='A5','extractor roles different')
 check(a4['read_other_extractor_output']==a5['read_other_extractor_output']==False,'no cross-reader output reads')
 check(a4['extraction_id']!=a5['extraction_id'],'process identifiers different')
 check(not a4['complete_reaction_structure_extracted'] and not a5['structure_complete'],'dual complete graphs NOT supplied')
 for role in (a4,a5):
  for fld in ['acceptor_smiles','donor_smiles','product_smiles']:
   check(role[fld] is None,'no invented '+role['agent_role']+' '+fld)
 tree=etree.parse(str(ROOT/SRC));ids={i.get('pub-id-type'):''.join(i.itertext()).strip() for i in tree.xpath('.//front//article-id')}
 check(ids['doi']==a3['official_DOI'] and ids['pmcid']==a3['official_PMCID'],'front identity DOI/PMCID')
 check(verify_stage_chain(ROOT/G5,sha_file(ROOT/G5))['stage']=='G5_FRESH_HOLDOUT_ACQUIRE','G5 immutable chain')
 check(verify_stage_chain(ROOT/G6,sha_file(ROOT/G6))['stage']=='G6_IDENTITY_STRUCTURE_ADMIT','G6 immutable chain')
 check(a6['A4_output_SHA']==sha_file(ROOT/O/'C_PMC13564134_A4_independent_source_read.json'),'A4 SHA A6 binding')
 check(a6['A5_output_SHA']==sha_file(ROOT/O/'C_PMC13564134_A5_independent_source_read.json'),'A5 SHA A6 binding')
 check(a6['structure_complete'] is False and a6['fresh_admitted'] is False,'no scientific grade promotion')
 prior=[json.loads(l) for l in (ROOT/B/'governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl').read_text().splitlines() if l.strip()]
 hits=[r for r in prior if 'partial-target-name:isoorientin' in [t.lower() for t in r.get('closure_tokens',[])]]
 check(len(hits)==a6['prior_named_target_row_count'],'isoorientin history name exposure count')
 check(len(hits)>0,'target-specific prior design exposure FOUND')
 r2=load(R2/'R2_search_results.json')
 check(r2['HTTP_attempts']==6,'SS 6 actual queries')
 check(r2['fresh_reaction_complete']==0,'SS metadata not elevated to G6')
 ss=[]
 groups={'PMC4494776':'10.1186/s12870-015-0504-7',
         'PMC4282749':'10.1111/tpj.12580',
         'PMC5856881':'10.1007/s00425-017-2822-5'}
 for pmcid,doi in groups.items():
  find=[x for x in r2['candidates'] if x.get('DOI','').lower()==doi.lower()]
  check(len(find)==1,'SS DOI found '+doi)
  counts={str(p): (ROOT/p).read_text().lower().count(pmcid.lower()) for p in (
    B/'exposure_ledger.jsonl',B/'governance/prior_exposure_inventory_v1/prior_exposure_rows.jsonl')}
  check(sum(counts.values())>0,'SS DOI -> PMCID historical alias '+doi)
  ss.append({'PMCID':pmcid,'DOI':doi,'old_exposure_rows_token_counts':counts,
   'metadata_qualified':False,'source_unique_group':False,'fresh_reaction_admitted':False,
   'reason':'same original PMCID prior chemistry/design exposed, DOI alone not fresh'})
 ss_path=R2/'SS_R2_three_O2_or_related_primary_source_historical_closure.json'
 put(ss_path,{'task':T,'historical_aligned_groups':ss,'new_source_unique_groups':0,
  'metadata_candidates_total':r2['unique'],'non_matching_candidates_chemical_identity':'unassessed',
  'G6_new_SS_fresh':0,'saturation_not_proven':True})
 expo=O/'C_PMC13564134_post_read_permanent_exposure.jsonl'
 if (ROOT/expo).exists():raise RuntimeError('exposure already recorded')
 exposure={'task':T,'family':'C','epoch_id':'C-E02','DOI':a3['official_DOI'],
 'PMCID':a3['official_PMCID'],'source_original':str(SRC),'source_sha256':src,
 'A3_sha256':sha_file(ROOT/O/'C_PMC13564134_A3_original_front_and_exposure.json'),
 'A4_sha256':sha_file(ROOT/O/'C_PMC13564134_A4_independent_source_read.json'),
 'A5_sha256':sha_file(ROOT/O/'C_PMC13564134_A5_independent_source_read.json'),
 'A6_sha256':sha_file(ROOT/O/'C_PMC13564134_A6_source_name_closure_and_graph_gaps.json'),
 'source_science_read_after_G5_stage':True,
 'source_article_studied_in_this_epoch':True,'permanent_development_exposure':True,
 'target_name_isoorientin_previously_exposed':True,'future_fresh_eligible':False,
 'source_cohort_reaction_graph_closure_incomplete':True,'fresh_C':0}
 write(T,str(expo),json.dumps(exposure,ensure_ascii=False,sort_keys=True)+'\n')
 check(sha_file(ROOT/expo)==hashlib.sha256((ROOT/expo).read_bytes()).hexdigest(),'new exposure receipt SHA valid')
 audit=O/'A11_C_original_and_SS_R2_alias_verification.json'
 put(audit,{'task':T,'agent_role':'A11','checked':len(checks),'failed':0,'checks':checks,
   'source_DOI':a3['official_DOI'],'source_sha':src,'G5_SHA':sha_file(ROOT/G5),
   'G6_SHA':sha_file(ROOT/G6),'SS_3_prior_O2_groups':ss,
   'SS_source_graphs_new':0,'C_full_structural_graphs_new':0,'fresh_C':0,'fresh_SS':0,
   'read_model_outcome':False,'human_reviewed':False})
 event(T,'P7_C_A11_source_text_extraction_checked_SS_aliases_audited',A11=len(checks),
      C_source_original=src,SS_groups_previously_exposed=3,fresh=0)
 print(json.dumps({'A11_pass':len(checks),'SS_prior_exposed_O2_groups':3,
   'C_new_original_study_A3':True,'A4_A5_graph_complete':False,
   'isoorientin_prior_name_exposure':len(hits),
   'fresh_C':0,'fresh_SS':0,'audit':str(audit)},ensure_ascii=False))
if __name__=='__main__':main()

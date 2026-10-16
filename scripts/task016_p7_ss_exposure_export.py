"""Export all actually read SS-E01 chemistry for independent permanent exposure closure.
A5 final extraction outputs are bound from role manifests and never decoded here.
"""
from __future__ import annotations
import hashlib,json,re,unicodedata,xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from scripts.operate import write
from scripts.task016_p7_closure_harness import canonical,closure_tokens,source_tokens,reaction_graph
ROOT=Path(__file__).resolve().parents[1]; BASE='outputs/task016-p7/v1/SS/'; OUT=BASE+'E01_permanent_exposure/'; TASK='TASK-016-P7'
NOW=datetime.now(timezone.utc).isoformat(); cache={}; inventory={}; read_inputs={}
def sha(path):
 p=ROOT/path
 if path not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  cache[path]=h.hexdigest()
 return cache[path]
def bind(path,pointer='',kind='actual_review_artifact',expected=None,decode=True):
 if not path:return None
 p=ROOT/path; exists=p.is_file()
 actual=sha(path) if exists and decode else None
 if expected and actual is not None and expected!=actual:raise ValueError('SHA mismatch '+path)
 inventory[path]={'path':path,'sha256':expected or actual,'actual_sha256_verified_by_exporter':actual,
  'bytes':p.stat().st_size if exists else None,'exists':exists,'artifact_kind':kind,
  'A5_output_content_decoded':False,'independent_hash_verification_required':not decode}
 return dict(path=path,sha256=expected or actual,json_pointer=pointer,artifact_kind=kind)
def load(path):
 read_inputs[path]=sha(path);return json.loads((ROOT/path).read_text())
def rows(path):
 read_inputs[path]=sha(path);return [json.loads(x) for x in (ROOT/path).read_text().splitlines() if x.strip()]
def norm(s):
 if not isinstance(s,str) or not s.strip():return None
 return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s).casefold()).strip()
def partial(role,name):return role+':'+norm(name) if norm(name) else None
def save(name,value,jsonl=False):
 path=OUT+name
 if (ROOT/path).exists():raise RuntimeError('immutable output exists '+path)
 content=''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in value) if jsonl else json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 write(TASK,path,content);return dict(path=path,sha256=sha(path))
# Safe role-manifest binding: no A5 final graph file is opened or parsed.
roles={}
for key,rel in [('Diosmin','root_A5_Diosmin/role_A5_manifest.json'),('Buckwheat','root_A5_buckwheat2018/role_A5_manifest.json'),('Narcissoside','root_A5_Narcissoside2025/role_A5_manifest.json'),('public_SI','root_public_SI_independent_review/role_A5_manifest_v2.json')]:
 path=BASE+rel;r=load(path); outputs=[]
 for op,digest in r.get('output_file_sha',{}).items():outputs.append(bind(op,kind='A5_review_output_not_decoded',expected=digest,decode=False))
 roles[key]={'manifest':bind(path,kind='A5_role_manifest_metadata_only'),'review_recorded_at':r.get('timestamp'),
  'first_actual_chemical_review_at':None,'output_file_bindings':outputs,'counts':r.get('counts'),
  'read_other_extractor_output':False,'manifest_metadata_read_only':True}
 for ip,digest in r.get('input_manifest_sha',{}).items():
  if (ROOT/ip).is_file():bind(ip,kind='A5_actual_source_input_or_role_manifest',expected=digest)
timings=rows(BASE+'source_batch_timing_final_v3.jsonl'); timing={r['batch_id']:r for r in timings};bind(BASE+'source_batch_timing_final_v3.jsonl')
for r in timings:
 for path,digest in r.get('raw_inputs_sha256',{}).items():bind(path,kind='raw_source_or_preregistered_recovery',expected=digest)
 if r.get('raw_only_manifest_path'):bind(r['raw_only_manifest_path'],kind='raw_only_input_manifest',expected=r['raw_only_manifest_sha256'])
# Graphs already actually read by this A4. Match only explicit source names; unresolved graphs remain null.
graphs={}
for i,r in enumerate(rows(BASE+'design_extractor_A4.jsonl'),1):
 for role,field in [('acceptor','acceptor'),('product','target')]:
  db=next(d for d in r['provenance']['database_identity'] if d['role']==role)
  graphs[norm(r['source_names'][role])]={'canonical_smiles':canonical(r[field]),'CID':db['CID'],
    'origin':bind(BASE+'design_extractor_A4.jsonl','line:'+str(i)),'raw_identity':bind(db['raw_path'],kind='official_machine_structure_identity',expected=db['raw_sha256'])}
 donor=canonical(r['donor'])
for i,r in enumerate(rows(BASE+'fresh_candidate_A4_target_history_screen.jsonl'),1):
 graphs[norm(r['source_standard_name'])]={'canonical_smiles':canonical(r['target_canonical']),'CID':r['CID'],
  'origin':bind(BASE+'fresh_candidate_A4_target_history_screen.jsonl','line:'+str(i)),
  'raw_identity':bind(r['machine_structure_input_path'],kind='official_machine_structure_identity',expected=r['machine_structure_input_sha256'])}
# Existing A4 official identity chain and source standards explicitly identify these aliases.
aliases=[('kaempferol 3-O-glucoside','astragalin'),('naringenin 7-O-glucoside','prunin'),('quercetin-3-O-glucoside','quercetin 3-O-glucoside')]
for a,b in aliases:graphs[norm(a)]=graphs[norm(b)]
# Literal source identities are read from the original JATS metadata, never guessed from candidate hints.
sources={}
def add_source(source_id,raws,batch,review_artifacts,reason=None):
 doi=source_id[4:] if source_id.startswith('DOI:') else None;pmcid=source_id if source_id.startswith('PMC') else None;pmid=None
 for raw in raws:
  if str(raw).endswith('.xml'):
   rt=ET.parse(ROOT/raw).getroot();ids={n.get('pub-id-type'):n.text for n in rt.findall('./front/article-meta/article-id')}
   doi=ids.get('doi',doi);pmcid=ids.get('pmcid',pmcid);pmid=ids.get('pmid',pmid)
 r={'source_id':source_id,'doi':doi,'pmcid':pmcid,'pmid':pmid,'raw_source_bindings':[bind(raw,kind='chemically_read_raw_source') for raw in raws],
  'review_artifact_bindings':review_artifacts,'batch_id':batch,'timing':timing.get(batch), 'reason':reason}
 sources[source_id]=r;return r
for i,r in enumerate(rows(BASE+'fresh_source_chemical_dispositions_current.jsonl'),1):
 add_source(r['source_id'],[r['source_raw_path']],'OA_supplement_9_originals',
  [dict(**bind(BASE+'fresh_source_chemical_dispositions_current.jsonl','line:'+str(i)),review_recorded_at=r['chemical_read_at'])],r['reason'])
sp=next(r for r in rows(BASE+'fresh_original_source_intake.jsonl') if r.get('resolved_pmcid')=='PMC3285110')
add_source('PMC3285110',[sp['xml']['path']],'initial_40_original_intake',[dict(**bind(BASE+'fresh_original_source_intake.jsonl','selection_id:'+sp['selection_id']),review_recorded_at=None)],'SpnG polyketide rhamnosyltransferase original chemically read; outside flavonoid domain; exact review time missing')
fg=load(BASE+'fresh_Fg2_SI_binary_text_preview.json')
add_source('DOI:10.1007/s11103-013-0133-1',[fg['raw_source_path'],'data/raw/task016-p7/SS/303b1b15a3b810f082a6291cd0ffec2201cac3dc49a593c9e4543b52f1f0079d.attempt-1.publisher_html'],'Fg2_public_SI',[dict(**bind(BASE+'fresh_Fg2_SI_binary_text_preview.json'),review_recorded_at=fg['chemically_read_at'])])
col=load(BASE+'fresh_collinearity2025_SI_text.json')
add_source('DOI:10.1007/s00425-025-04742-w',[col['raw_source_path']],'Collinearity2025_complete_public_SI',[dict(**bind(BASE+'fresh_collinearity2025_SI_text.json'),review_recorded_at=col['chemically_read_at']),bind(BASE+'fresh_collinearity2025_SI_image_manifest.json')])
buck=load(BASE+'fresh_buckwheat2018_A4_original_review.json')
add_source(buck['source_id'],[buck['raw_input_path']],'Buckwheat2018_complete_PDF',[dict(**bind(BASE+'fresh_buckwheat2018_A4_original_review.json'),review_recorded_at=buck['extracted_at'])])
for path,digest in buck['source_view_sha256'].items():bind(path,kind='A4_actually_viewed_source_image',expected=digest)
nar=load(BASE+'fresh_narcissoside2025_common_raw_input_manifest.json')
add_source('DOI:10.1021/acs.jafc.4c12187',[r['path'] for r in nar['official_SI_files']],'Narcissoside2025_complete_SI',[dict(**bind(BASE+'fresh_narcissoside2025_A4_original_review.json'),review_recorded_at=timing['Narcissoside2025_complete_SI']['documented_chemical_review_completed_no_later_than']),bind(BASE+'fresh_narcissoside2025_SI_text.txt'),bind(BASE+'fresh_narcissoside2025_A4_SI_xlsx_all_rows.jsonl')])
sources['DOI:10.1021/acs.jafc.4c12187']['pmid']='40105789'
oh=load(BASE+'fresh_Ohashi2015_public_preview_A4_disposition.json')
add_source(oh['source_id'],[oh['raw_path']],'Ohashi2015_public_preview',[dict(**bind(BASE+'fresh_Ohashi2015_public_preview_A4_disposition.json'),review_recorded_at=oh['at'])])
# Bind additional actual donor read and source-image artifacts without inventing a source donor reaction.
donrev=load(BASE+'fresh_PMC11527692_donor_original_review.json')
sources['PMC11527692']['review_artifact_bindings'].append(bind(BASE+'fresh_PMC11527692_donor_original_review.json'))
for path in (ROOT/(BASE+'derived_narcissoside2025_source_views')).glob('*.png'):bind(str(path.relative_to(ROOT)),kind='A4_source_image_generated_actual_view_subset_2_5_9_10')
for src,key in [('PMC11527692','Diosmin'),('DOI:10.1080/09168451.2018.1491286','Buckwheat'),('DOI:10.1021/acs.jafc.4c12187','Narcissoside'),('DOI:10.1007/s11103-013-0133-1','public_SI'),('DOI:10.1007/s00425-025-04742-w','public_SI')]:sources[src].setdefault('independent_review_bindings',[]).append(roles[key])

def exposure(entity_id,kind,src,acceptor=None,product=None,site=None,origins=None,recorded=None,raw=None,donor_actual=False):
 s=sources[src];ag=graphs.get(norm(acceptor));pg=graphs.get(norm(product));a=ag['canonical_smiles'] if ag else None;t=pg['canonical_smiles'] if pg else None
 unresolved=sorted(set(filter(None,[partial('partial-acceptor-name',acceptor),partial('partial-target-name',product),partial('partial-site',site)])))
 assay='SS-E01:internal-assay:'+entity_id
 row={'exposure_id':'SS-E01:'+kind+':'+entity_id,'task':TASK,'epoch_id':'SS-E01','family':'SS','exposure_type':'permanent_development_chemical_exposure',
  'development_exposed':True,'eligible_for_fresh_holdout':False,'evidence_eligible':False,'human_reviewed':False,'entity_kind':kind,
  'source_id':src,'doi':s['doi'],'pmcid':s['pmcid'],'pmid':s['pmid'],'reaction_id':entity_id if kind=='reaction_candidate' else None,
  'assay_id':assay,'assay_id_origin':'internal pointer key; not asserted source-assigned assay ID',
  'source_assay_evidence_pointers':origins or [],'acceptor_source_name':acceptor,'partial_target_source_name':product,'site_claim':site,'site':site,
  'acceptor_smiles':a,'product_smiles':t,'target_graph':t,'donor_smiles':donor if donor_actual else None,
  'donor_actual_assay_evidence_present':donor_actual,'known_database_graph_identity':{'acceptor':ag,'product':pg},
  'source_binding':s,'first_actual_chemical_review_at':None,
  'first_review_timestamp_status':'exact first review not explicitly recorded; no inference from later artifact creation',
  'review_recorded_at':recorded,'review_time_semantics':'existing completed/recorded review, not claimed first chemical access',
  'origins':origins or [],'raw_chemical_fields':raw or {},'unresolved_partial_identity_tokens':unresolved,
  'partial_identity_resolution_required':bool(unresolved),'read_model_outcomes':False,'read_other_extractor_output':False,'registered_at':NOW}
 tokens=set(unresolved);tokens.add('source-local-assay:'+src+'|'+entity_id)
 # All actually known non-donor molecular graphs are permanently exposed, irrespective of endpoint role.
 if a:tokens.add('target:'+a)
 row['closure_tokens']=sorted(tokens);row['source_tokens']=sorted(source_tokens(row));row['reaction_signature']=reaction_graph(row)
 row['closure_tokens']=sorted(closure_tokens(row));row['field_completeness']={'source':True,'target_graph':t is not None,'acceptor_graph':a is not None,
  'donor_graph':donor_actual,'site':site is not None,'reaction_signature':row['reaction_signature'] is not None,'evidence_pointer':bool(origins)}
 return row
candidates=[]
main=rows(BASE+'E01_final_A4_candidate_universe.jsonl')
for i,r in enumerate(main,1):
 ptrs=[bind(BASE+'E01_final_A4_candidate_universe.jsonl','line:'+str(i))]
 for p in r.get('source_evidence_pointers',[]):ptrs.append(bind(p['path'],json.dumps({k:v for k,v in p.items() if k!='path'},ensure_ascii=False),kind='actual_candidate_source_pointer'))
 if 'Buckwheat2018' in r['candidate_id']:
  ptrs.extend([bind(BASE+'fresh_buckwheat2018_A4_Table2_candidate_universe.jsonl','line:'+str(r['source_row'])),bind(BASE+'fresh_buckwheat2018_A4_original_review.json')])
 if 'Narcissoside2025' in r['candidate_id']:ptrs.extend(sources[r['source_id']]['review_artifact_bindings'])
 site=r.get('site_claim');donor_actual='Buckwheat2018' in r['candidate_id']
 if r['candidate_id'].endswith('Table2:01'):site='parent_Glcp_O6'
 e=exposure(r['candidate_id'],'reaction_candidate',r['source_id'],r.get('acceptor_source_name'),r.get('product_source_name'),site,ptrs,
   r.get('reviewed_at',r.get('extracted_at')),r,donor_actual)
 e['disposition']=r['disposition'];e['qualified_reaction_reference']=False;candidates.append(e)
assert len(candidates)==28 and Counter(r['disposition'] for r in candidates)=={'rejected':18,'deferred':10}
source_rows=[exposure(src,'source',src,origins=s['review_artifact_bindings'],recorded=next((b.get('review_recorded_at') for b in s['review_artifact_bindings'] if b.get('review_recorded_at')),None),raw={'reason':s['reason']}) for src,s in sources.items()]
assert len(source_rows)==15
aux=[]
# Whole SI F1-F8 isolated compounds: literal lossy preview labels, no enzyme arrow or guessed stereo.
for label in range(1,9):
 match=re.search(r'(Kaempferol.*?\(F'+str(label)+r'\))',fg['text'],re.S)
 # Select the final heading before its label; earlier NMR prose is not part of its name.
 heading=match.group(1)[match.group(1).rfind('Kaempferol'):].rsplit(' (F',1)[0].strip()
 aux.append(exposure('Fg2:isolated:F'+str(label),'isolated_compound_partial_identity','DOI:10.1007/s11103-013-0133-1',product=heading,
  origins=[bind(BASE+'fresh_Fg2_SI_binary_text_preview.json','/text/(F'+str(label)+')')],recorded=fg['chemically_read_at'],raw={'source_compound_label':'F'+str(label),'literal_lossy_source_heading':heading,'reaction_evidence':False,'complex_structure_guessed':False}))
# AUTG25 captions were actually read. Product identity/site are left null: caption alone names only substrate.
for num,name in [(2,'kaempferol'),(3,'quercetin')]:
 aux.append(exposure('Narcissoside2025:AUTG25:S'+str(num),'outside_SS_assay_partial_identity','DOI:10.1021/acs.jafc.4c12187',acceptor=name,
  origins=[bind(BASE+'fresh_narcissoside2025_SI_text.txt','Figure S'+str(num))],recorded=timing['Narcissoside2025_complete_SI']['documented_chemical_review_completed_no_later_than'],raw={'source_caption':'AUTG25 converting substrate '+name,'product_not_completed_by_name_inference':True}))
# All tissue endpoint cells, including explicit 0.00 +-0.01, remain biological observations, never assays.
for i,r in enumerate(rows(BASE+'fresh_buckwheat2018_A4_Table3_all_cells.jsonl'),1):
 name=r['analyte'];e=exposure('Buckwheat2018:Table3:'+str(i),'biological_endpoint','DOI:10.1080/09168451.2018.1491286',product=name,
  origins=[bind(BASE+'fresh_buckwheat2018_A4_Table3_all_cells.jsonl','line:'+str(i))],recorded=r['extracted_at'],raw=r)
 for component in r.get('c_glucosylflavones_sum') or []:
  e['closure_tokens'].append(partial('partial-target-name',component));e['unresolved_partial_identity_tokens'].append(partial('partial-target-name',component))
 aux.append(e)
# Actually read subscription abstract names; unknown structures remain null.
for name in oh['source_names']:
 if name=='UDP-Rha':continue
 aux.append(exposure('Ohashi2015:preview:'+name,'source_preview_partial_identity',oh['source_id'],product=name,
  origins=[bind(BASE+'fresh_Ohashi2015_public_preview_A4_disposition.json','/source_names')],recorded=oh['at'],raw={'preview_only':True,'full_assay_source_not_retrieved':True}))
# Public SI actually used 3Rut positional-isomer standards for unavailable 7Rut products.
for name,ptr in [('nicotiflorin','FigureS2d proxy standard 3Rut'),('rutin','FigureS2e proxy standard 3Rut')]:
 aux.append(exposure('Collinearity2025:observed-proxy:'+name,'observed_reference_standard','DOI:10.1007/s00425-025-04742-w',product=name,
  origins=[bind(col['raw_source_path'],ptr,kind='actual_candidate_source_pointer')],recorded=col['chemically_read_at'],raw={'not_the_7Rut_product':True}))
# Preserve actually inspected historical source-first design names as design exposure, not future holdout chemistry.
historical=[]
for i,r in enumerate(rows(BASE+'E02_source_first_design_inventory.jsonl'),1):
 ts=set();bindings=[]
 for s in r['source_support']:
  bind(s['raw_path'],kind='historical_already_exposed_source',expected=s['raw_sha256']);ts.update(source_tokens(s));bindings.append(s)
 for key in ('source_named_acceptors','source_named_products'):
  ts.update(filter(None,(partial('partial-acceptor-name' if key.endswith('acceptors') else 'partial-target-name',n) for n in r.get(key,[]))))
 historical.append({'exposure_id':'SS-E01:historical-design-reread:'+r['candidate_id'],'task':TASK,'epoch_id':'SS-E01',
  'development_exposed':True,'eligible_for_fresh_holdout':False,'entity_kind':'historical_source_design_only',
  'source_support':bindings,'closure_tokens':sorted(ts),'target_graph':None,'reaction_signature':None,
  'first_actual_chemical_review_at':None,'origins':[bind(BASE+'E02_source_first_design_inventory.jsonl','line:'+str(i))],
  'source_names':{k:r.get(k) for k in ['source_named_acceptors','source_named_products']},'guard_built':False,
  'fresh_chemistry_extracted':False,'read_other_extractor_output':False})
# Discovery hints are recorded separately: a hint cannot erase chemistry exposure from another record.
hints=[]
exposed_source_tokens=set().union(*(set(r['source_tokens']) for r in source_rows))
for rel in ['fresh_discovery_hits.jsonl','fresh_discovery_retry_hits.jsonl','fresh_supplemental_hits.jsonl','fresh_substrate_source_batch2/hits.jsonl']:
 for i,r in enumerate(rows(BASE+rel),1):
  toks=source_tokens({'pmcid':r.get('pmcid'),'doi':r.get('doi')});raw=r.get('raw_response')
  hints.append({'hint_id':rel+':line:'+str(i),'entity_kind':'metadata_only_hint','chemical_exposure_by_this_record':False,
   'source_id':r.get('pmcid') or r.get('doi') or r.get('pmid') or r.get('discovery_key'),
   'doi':r.get('doi'),'pmcid':r.get('pmcid'),'pmid':r.get('pmid'),'title':r.get('title'),
   'query_id_namespaced':str(Path(BASE+rel).parent)+'|'+str(r.get('query_id')),
   'source_tokens':sorted(toks),'same_source_chemically_exposed_elsewhere_in_E01':bool(toks&exposed_source_tokens),
   'historical_source_hint':r.get('historical_source'),'origin':bind(BASE+rel,'line:'+str(i),kind='metadata_only_hint_inventory'),
   'raw_metadata_response':bind(raw,kind='metadata_only_query_response') if raw else None,
   'reaction_graph':None,'target_graph':None,'chemical_fields_extracted':False})
assert len(hints)==754
allrows=candidates+source_rows+aux+historical
partial_index={}
for r in allrows:
 for token in r.get('unresolved_partial_identity_tokens',[]) or [t for t in r['closure_tokens'] if t.startswith('partial-')]:partial_index.setdefault(token,[]).append(r['exposure_id'])
outputs=[save('candidate_chemical_exposure_28.jsonl',candidates,True),save('source_chemical_exposure_15.jsonl',source_rows,True),
 save('auxiliary_actual_chemical_observations.jsonl',aux,True),save('historical_design_rereads.jsonl',historical,True),
 save('permanent_chemical_exposure_ledger.jsonl',allrows,True),save('metadata_only_hints.jsonl',hints,True),
 save('unresolved_partial_identity_index.json',{'created_at':NOW,'tokens':partial_index,
  'policy':'Permanent development exposure. Independent A6 must resolve source-supported aliases and structure identities before admitting any future candidate; unmatched/new names are not proof of freshness. Unknown graphs stay null. Donor-only identities do not merge all source closures.',
  'supported_existing_A4_identity_aliases':[{'source_name':a,'known_A4_name':b,'known_graph':graphs[norm(b)]} for a,b in aliases]})]
# Source inventory includes current originals, failed/recovery snapshot pointers and actual review physical artifacts.
outputs.append(save('raw_and_review_artifact_inventory.jsonl',sorted(inventory.values(),key=lambda r:r['path']),True))
checks={'candidate_rows':len(candidates),'candidate_dispositions':dict(Counter(r['disposition'] for r in candidates)),
 'actual_chemical_sources':len(source_rows),'auxiliary_chemical_observation_rows':len(aux),'historical_design_reread_rows':len(historical),
 'permanent_chemical_exposure_rows':len(allrows),'metadata_only_hint_rows':len(hints),'unresolved_partial_tokens':len(partial_index),
 'unknown_graphs_remain_null':all(r['product_smiles'] is None for r in candidates if not r['known_database_graph_identity']['product']),
 'no_unproven_donor_full_reaction_tokens':all(r['reaction_signature'] is None for r in candidates if not r['donor_actual_assay_evidence_present']),
 'all_original_28_candidate_IDs_retained':set(r['candidate_id'] for r in main)==set(r['reaction_id'] for r in candidates),
 'all_inventory_files_exist':all(r['exists'] for r in inventory.values()),
 'A5_final_output_content_not_read':True,'first_review_missing_times_not_invented':all(r['first_actual_chemical_review_at'] is None for r in allrows),
 'explicit_zero_preserved':sum(bool(r['raw_chemical_fields'].get('explicit_zero')) for r in aux),
 'not_detected_rows_preserved':sum(r['raw_chemical_fields'].get('value_status')=='not_detected' for r in candidates),
 'scope_freeze_sha256_unchanged':sha(BASE+'scope_freeze.json')=='97d102c59b4d37de3cf50a4d6f0c1df43816f7eca4c119313d89f3aed06e9b07'}
assert all(checks[k] for k in ['unknown_graphs_remain_null','no_unproven_donor_full_reaction_tokens','all_original_28_candidate_IDs_retained','all_inventory_files_exist','scope_freeze_sha256_unchanged'])
outputs.append(save('export_integrity_checks.json',checks))
manifest={'task_id':TASK,'epoch_id':'SS-E01','agent_role':'A2/A4 exposure archive export; not A6 adjudication','approval':'agent_delegated',
 'created_at':NOW,'input_file_sha256':read_inputs,'output_bindings':outputs,'counts':checks,'independent_A5_review_role_bindings':roles,
 'read_holdout':True,'read_model_outcomes':False,'read_other_extractor_output':False,'A5_final_outputs_decoded':False,
 'evidence_eligible':False,'scientific_model_runs':0,'scope_modified':False,'closure_registration_status':'pending_root_A6_global_ledger_registration',
 'epoch_end_status':'root18.1 decision pending; no source saturation or budget exhaustion claim','future_E02_design_qualification_authorized_by_this_export':False,
 'timing_policy':'Current export time is real; completed-review times retained with semantics, exact first actual chemical review missing remains null; late-binding G5 cannot be retrospectively repaired.'}
final=save('role_A2_A4_permanent_exposure_export_manifest.json',manifest);print(json.dumps({'manifest':final,'counts':checks,'outputs':outputs},ensure_ascii=False,indent=2))

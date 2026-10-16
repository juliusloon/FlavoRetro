"""Conserve bounded source rows, failed bytes and unfinished identities; no exhaustive chemical claim."""
import sys,json,hashlib,html,re,xml.etree.ElementTree as ET
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write
from flavoretro.resources import sha
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'outputs/task016-p2/v1';Q=ROOT/'outputs/task016-p2/v2'
def rows(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()] if p.exists() else []
def save(n,v,jl=False):write('TASK-016-P2',str((Q/n).relative_to(ROOT)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in v) if jl else json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
articles={}
for n in ['article_acquisition_manifest.json','article_acquisition_addendum.json','article_acquisition_extension.json']:
 for a in json.loads((R/n).read_text()):articles[a['pmcid']]=a
attempts=rows(R/'acquisition_attempts.jsonl');reserved=rows(R/'acquisition_reservations.jsonl');external=rows(R/'external_discovery_receipts.jsonl')
queries=[];query_records=[]
for n in ['discovery_manifest.json','alternate_discovery_manifest.json','lightweight_discovery_manifest.json']:
 for qi,q in enumerate(json.loads((R/n).read_text())):
  f=q['raw'];j={};query_id=n+':'+str(qi)
  if f['status']=='raw_available':
   try:j=json.loads((ROOT/f['path']).read_text())
   except json.JSONDecodeError:pass
  if 'resultList' in j:entries=j['resultList'].get('result',[]);hits=j.get('hitCount');provider='EuropePMC'
  elif 'esearchresult' in j:entries=[dict(pmcid='PMC'+i,title=None) for i in j['esearchresult'].get('idlist',[])];hits=int(j['esearchresult'].get('count',0));provider='NCBI'
  elif isinstance(j.get('message'),dict):entries=j['message'].get('items',[]);hits=j['message'].get('total-results');provider='Crossref'
  else:entries=[];hits=None;provider=q.get('provider',f['provider'])
  queries.append(dict(query_id=query_id,query=q.get('label',q.get('term')),provider=provider,url=q.get('url',f['url']),raw_path=f['path'],raw_sha256=f['sha256'],status=f['status'],hit_count=hits,retrieved_rows=len(entries),unacquired_rows=None if hits is None else max(0,hits-len(entries)),pagination_complete=None if hits is None else hits<=len(entries)))
  for i,e in enumerate(entries):
   query_records.append(dict(query_id=query_id,row=i,record=e,raw_path=f['path'],raw_sha256=f['sha256'],disposition='metadata_only_no_PMC_identifier' if not e.get('pmcid') else 'retained_metadata_source_discovery'))
save('source_query_inventory.json',queries);save('source_query_record_dispositions.jsonl',query_records,True)
# Complete deduplicated metadata universe (including non-PMC Crossref and lightweight rows).
metadata={}
def add(e,origin):
 pmc=e.get('pmcid');doi=e.get('doi',e.get('DOI'));doi=doi.lower() if isinstance(doi,str) else None
 key='PMC:'+pmc if pmc else 'DOI:'+doi if doi else 'ID:'+str(e.get('source',origin))+':'+str(e.get('id',hashlib.sha256(json.dumps(e,sort_keys=True).encode()).hexdigest()))
 title=e.get('title');title=' '.join(title) if isinstance(title,list) else title
 if key not in metadata:metadata[key]=dict(metadata_key=key,pmcid=pmc,doi=doi,title=title,origins=[])
 metadata[key]['origins'].append(origin)
for e in rows(R/'article_discovery_records.jsonl'):add(e,'inherited_or_initial_metadata')
for e in json.loads((R/'article_intake_addendum.json').read_text())['records']:add(e,'alternate_gene_query_metadata')
for e in rows(R/'lightweight_metadata.jsonl'):add(e,'lightweight_semantic_metadata')
for r in query_records:add(r['record'],r['query_id']+':'+str(r['row']))
plan={r['pmcid'] for r in json.loads((R/'lightweight_article_plan.json').read_text())['records']}
inherited_pmc={r['provenance'].get('pmcid') for r in rows(Q/'runtime_instances.jsonl')}
unresolved={r.get('pmcid') for r in rows(Q/'unresolved_instances.jsonl')}
for r in metadata.values():
 pmc=r['pmcid'];a=articles.get(pmc)
 r['disposition']='acquired_source_identity_pending_or_build' if a and a['status']=='fulltext_available' else 'source_attempt_failed_or_license_pending' if a else 'pending_source_only_title_candidate_not_acquired' if pmc in plan else 'metadata_retained_not_selected_in_bounded_intake'
 r['runtime_source']=pmc in inherited_pmc;r['new_assay_admitted']=False;r['model_outputs_used_for_selection']=False
save('metadata_dispositions.jsonl',sorted(metadata.values(),key=lambda r:r['metadata_key']),True)
allfiles={r['path']:{**r,'origin':'new_P2_attempt'} for r in attempts}
for f in rows(R/'reused_files.jsonl'):
 if f['path'] not in allfiles:allfiles[f['path']]={**f,'origin':'reused_immutable_prior'}
for a in articles.values():
 for f in a.get('files',[]):
  if f.get('path') and f['path'] not in allfiles:allfiles[f['path']]={**f,'origin':'reused_immutable_prior'}
for f in allfiles.values():
 f['disposition']='retained_available_source_bytes' if f['status']=='raw_available' else 'retained_failure_response_or_partial_bytes'
 f['hash_verified']=sha(ROOT/f['path'])==f['sha256'];assert f['hash_verified'] and (ROOT/f['path']).stat().st_size==f['bytes']
save('file_dispositions.jsonl',sorted(allfiles.values(),key=lambda r:r['path']),True)
segments=rows(R/'article_evidence_segments.jsonl')+rows(R/'article_evidence_extension.jsonl');unique={ (r['pmcid'],r['raw_sha256'],r['locator']):r for r in segments }
save('record_dispositions.jsonl',[dict(record_type='source_segment',record_id=':'.join(k),raw_path=r['raw_path'],text_sha256=r['text_sha256'],disposition='source_context_only_not_individual_assay_admission') for k,r in sorted(unique.items())]+[dict(record_type='inherited_confirmed_instance',record_id=r['instance_id'],disposition='runtime_build_calibration_only') for r in rows(Q/'runtime_instances.jsonl')]+[dict(record_type='withdrawn_provisional_encoding',record_id=r['instance_id'],disposition='retained_unresolved_not_runtime') for r in rows(Q/'provisional_withdrawn_instances.jsonl')],True)
negatives=[]
for pmc,locator,acceptor,donor in [('PMC9786081','body//p[17]','prenylflavonol source-tested acceptors','UDP-glucose'),('PMC9786081','body//p[17]','prenylflavonol source-tested acceptors','UDP-rhamnose'),('PMC4494776','body//p[30]','K3-O-rhamnosyl-(1→4)-[rhamnosyl-(1→6)-glucoside]','UDP-glucose'),('PMC4494776','body//p[30]','K3-O-rhamnosyl-(1→4)-[glucosyl-(1→6)-glucoside]','UDP-glucose'),('PMC4494776','body//p[30]','K3-O-glucoside','UDP-arabinose'),('PMC4494776','body//p[30]','K3-O-glucoside','UDP-glucuronic acid'),('PMC6255700','body//p[20]','cyanidin3,5-O-diglucoside','UDP-glucose'),('PMC6255700','body//p[21]','quercetin3-O-glucoside','UDP-glucose'),('PMC6255700','body//p[20]','cyanidin','UDP-glucose'),('PMC6255700','body//p[22]','source-tested Ib3GGT/At3GGT acceptors','UDP-galactose'),('PMC6255700','body//p[22]','source-tested Ib3GGT/At3GGT acceptors','UDP-arabinose')]:
 s=next(r for r in unique.values() if r['pmcid']==pmc and r['locator']==locator)
 negatives.append(dict(pmcid=pmc,locator=locator,raw_path=s['raw_path'],raw_sha256=s['raw_sha256'],text_sha256=s['text_sha256'],acceptor_source_label=acceptor,donor_source_label=donor,source_outcome='explicit no activity/no product/not detected; qualitative',numeric_yield=None,numeric_zero_asserted=False,scope='source enzyme and assay only; not universal reaction negative or scope-guard validation',review_type='agent_delegated',human_reviewed=False))
save('negative_instances.jsonl',negatives,True)
# The v1 selection sentence remains immutable history; current qualified rows/counts override it.
save('role_interpretation.json',dict(split_sha256=sha(Q/'development_split_manifest.json'),qualified_runtime_instances=85,new_admitted=0,withdrawn=2,fresh_holdout=0,authoritative_fields=['files_sha256','counts','qualification','actual qualified runtime rows'],superseded_historical_selection_sentence='v2 split inherited its v1 selection narrative mentioning two C8 build cases; qualification explicitly withdraws both and runtime contains only 85 inherited cases',raw_history_mutated=False,new_source_extension_did_not_change_runtime=True))
observed_paths={str(p.relative_to(ROOT)) for p in (ROOT/'data/raw/task016-p2').rglob('*') if p.is_file()};known_paths={r['path'] for r in attempts};assert observed_paths==known_paths
summary=dict(schema_version=1,scope='bounded source/API intake; pending sources, source identity, upstream overlap and model training overlap remain explicit',new_HTTP_attempts=len(attempts),external_tool_request_units=sum(r['request_units'] for r in external),external_tool_internal_HTTP_attempts='not exposed; no exact count assertion',new_raw_bytes=sum(r['bytes'] for r in attempts),raw_file_count=len(observed_paths),raw_file_difference=len(observed_paths^known_paths),completed_reservations=len(reserved),pending_reservations=len({(r['url'],r['attempt']) for r in reserved}-{(r['url'],r['attempt']) for r in attempts}),metadata_records=len(metadata),query_rows=len(query_records),query_record_dispositions=len(query_records),record_disposition_difference=0,queries=len(queries),article_ids=len(articles),available_articles=sum(a['status']=='fulltext_available' for a in articles.values()),new_available_article_versions=len({r['url'] for r in attempts if r['content_role']=='fullTextXML' and r['status']=='raw_available'}),new_attempted_article_versions=len({r['url'] for r in attempts if r['content_role']=='fullTextXML'}),new_attachment_attempted_files=len({r['url'] for r in attempts if r['content_role']=='supplement'}),new_attachment_available_files=len({r['url'] for r in attempts if r['content_role']=='supplement' and r['status']=='raw_available'}),reuse_file_count=sum(r['origin']=='reused_immutable_prior' for r in allfiles.values()),source_segment_records=len(unique),confirmed_inherited_instances=85,new_confirmed_instances=0,withdrawn_provisional_instances=2,inherited_unresolved_P1_contexts=12,source_candidates_unresolved=len(rows(Q/'unresolved_instances.jsonl')),source_negative_records=len(negatives),pending_title_selected_articles=sum(r['pmcid'] in plan and r['pmcid'] not in articles for r in metadata.values()),status_counts=dict(Counter(r['status'] for r in attempts)),HTTP_status_counts=dict(Counter(str(r['status_code']) for r in attempts)),by_content_role=dict(Counter(r['content_role'] for r in attempts)),limits=dict(source_bytes=2*1024**3,HTTP_attempts=2500,metadata=5000,new_articles=120,new_attachments=240,max_workers=4,max_attempts_per_URL=2),chemical_universe_exhausted=False)
assert summary['new_raw_bytes']<=summary['limits']['source_bytes'] and len(attempts)+summary['external_tool_request_units']<=2500 and len(metadata)<=5000 and summary['new_attempted_article_versions']<=120 and summary['new_attachment_attempted_files']<=240
assert len(reserved)==len(attempts) and summary['pending_reservations']==0 and max(Counter(r['url'] for r in attempts).values())<=2
save('source_yield_inventory.json',summary)
save('source_registry.json',dict(articles=sorted(articles.values(),key=lambda r:r['pmcid']),inventory_sha256=sha(Q/'source_yield_inventory.json'),files_sha256={n:sha(Q/n) for n in ['metadata_dispositions.jsonl','file_dispositions.jsonl','record_dispositions.jsonl','negative_instances.jsonl','source_query_inventory.json','source_query_record_dispositions.jsonl']},old_unresolved_reference='outputs/task016-p1/v2/unresolved_instances.jsonl',identity='no new admitted single-step reaction; acquired source records are not executable evidence'))
print(json.dumps(summary,ensure_ascii=False,indent=2))

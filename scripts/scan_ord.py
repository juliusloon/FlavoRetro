"""Full row scan of a pinned ORD Parquet, isolated from active resources.

Screening representation: provided reaction (CX)SMILES; if absent, explicit ORD
reactant/product SMILES. No role repair, atom mapping, chemical admission or blind split.
"""
import argparse,collections,functools,hashlib,json,multiprocessing,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'outputs/validation/task015-dependencies'))
import pyarrow.parquet as pq
from google.protobuf.json_format import MessageToDict
from ord_schema.proto import reaction_pb2 as pb
from rdkit import Chem,rdBase
from flavoretro.triage import load_rules,Screener
from scripts.operate import digest,event,write

SCREEN=None

def initialize():
 global SCREEN
 rules,_=load_rules();SCREEN=Screener(rules)
 rdBase.DisableLog('rdApp.error');rdBase.DisableLog('rdApp.warning')

@functools.lru_cache(maxsize=50000)
def quick(smiles):
 mol=Chem.MolFromSmiles(smiles) if smiles else None
 if mol is None:return ('parse_failure',())
 # All v1 queries have at least 15 atoms; this is a safe substructure prerequisite.
 found=tuple(k for k,q in SCREEN.patterns.items() if mol.GetNumAtoms()>=q.GetNumAtoms() and mol.HasSubstructMatch(q,useChirality=False))
 return ('generic_candidate' if any(a.GetAtomicNum()==0 for a in mol.GetAtoms()) else 'parsed',found)

def component_smiles(comp):
 ids=[x.value for x in comp.identifiers if x.type in (pb.CompoundIdentifier.SMILES,pb.CompoundIdentifier.CXSMILES)]
 return ids[0] if ids else None

def representation(rx):
 ids=[x for x in rx.identifiers if x.type in (pb.ReactionIdentifier.REACTION_SMILES,pb.ReactionIdentifier.REACTION_CXSMILES)]
 if ids:
  raw=ids[0].value;core=raw.strip().split(' ',1)[0];sides=core.split('>')
  if len(sides)!=3:return [],'reaction_identifier',{'malformed_reaction_identifier':True,'identifier_count':len(ids)},raw
  components=[]
  for role,part in [('reactant',sides[0]),('product',sides[2])]:
   if part:
    components.extend({'role':role,'structure':{'canonical_smiles':s,'status':'parsed'}} for s in part.split('.'))
  issues={'identifier_count':len(ids),'cx_extension_ignored_for_structural_screen':core!=raw.strip(),'agent_side_not_screened':bool(sides[1])}
  return components,'reaction_identifier',issues,raw
 components=[]
 for input in rx.inputs.values():
  for c in input.components:
   if c.reaction_role==pb.ReactionRole.REACTANT:
    s=component_smiles(c);components.append({'role':'reactant','structure':{'canonical_smiles':s,'status':'parsed' if s else 'missing'}})
 for o in rx.outcomes:
  for c in o.products:
   s=component_smiles(c);components.append({'role':'product','structure':{'canonical_smiles':s,'status':'parsed' if s else 'missing'}})
 return components,'explicit_components',{},None

def process(batch):
 group,start,rows=batch;stats=collections.Counter();scaffolds=collections.Counter();glyco=collections.Counter();categories=collections.Counter();candidates=[];unknown=[]
 for offset,item in enumerate(rows):
  index=start+offset;stats['rows']+=1
  try:
   rx=pb.Reaction.FromString(item['reaction'])
  except Exception as e:
   stats['unknown']+=1;stats['protobuf_parse_failure']+=1;unknown.append({'row':index,'row_group':group,'id':item['reaction_id'],'reason':'protobuf_parse_failure','error':str(e)});continue
  stats['protobuf_parsed']+=1;components,rep,issues,raw_smiles=representation(rx);stats['representation:'+rep]+=1
  if rx.reaction_id!=item['reaction_id']:issues['reaction_id_mismatch']=True;stats['reaction_id_mismatch']+=1
  statuses=[];found=set();roles=set()
  for c in components:
   status,names=quick(c['structure']['canonical_smiles']);statuses.append(status);found.update(names);roles.add(c['role'])
   if status!='parsed':c['structure']['status']=status
  if not components or roles!={'reactant','product'}:issues['missing_reaction_side']=True
  if issues.get('malformed_reaction_identifier') or issues.get('missing_reaction_side') or any(s!='parsed' for s in statuses):
   stats['rows_with_structural_issues']+=1;issues['component_statuses']=statuses
  for status in statuses:stats['components:'+status]+=1
  if found:
   stats['candidate']+=1
   row={'id':item['reaction_id'],'components':components};features=SCREEN.reaction(row)
   # Bound the unbounded v1 diagnostic cache when scanning a new large source.
   if SCREEN.molecule.cache_info().currsize>10000:SCREEN.molecule.cache_clear()
   scaffolds.update(found);categories.update(features['structural_categories'])
   if features['domain_glycoside_candidate']:stats['domain_glycoside_candidate']+=1
   for role in ['reactant','product']:
    glyco.update({role+':'+family:count for family,count in features[role+'_domain_sites'].items()})
   measurements=[]
   for oi,outcome in enumerate(rx.outcomes):
    for pi,product in enumerate(outcome.products):
     for measurement in product.measurements:
      if measurement.type==pb.ProductMeasurement.YIELD:
       present=measurement.HasField('percentage') and measurement.percentage.HasField('value')
       value=measurement.percentage.value if present else None
       measurements.append({'outcome_index':oi,'product_index':pi,'percentage_present':present,'value':value,'measurement':MessageToDict(measurement,preserving_proto_field_name=True)})
   stats['candidate_with_patent']+=bool(rx.provenance.patent)
   stats['candidate_with_procedure']+=bool(rx.notes.procedure_details)
   stats['candidate_with_yield']+=bool(any(m['percentage_present'] for m in measurements))
   stats['candidate_with_zero_yield']+=bool(any(m['percentage_present'] and m['value']==0 for m in measurements))
   candidate={'id':item['reaction_id'],'source_row':index,'row_group':group,'protobuf_sha256':hashlib.sha256(item['reaction']).hexdigest(),'representation':rep,'raw_reaction_smiles':raw_smiles,'components':components,'issues':issues,'features':features,'patent':rx.provenance.patent or None,'source_doi':rx.provenance.doi or None,'source_doi_meaning':'as supplied; dataset DOI may not identify the patent or reaction','yield_measurements':measurements,'raw_ord':MessageToDict(rx,preserving_proto_field_name=True),'human_review_status':'not_performed','production_eligible':False,'split':'development_exposed','training_overlap':'unknown'}
   candidates.append(candidate)
  elif issues.get('malformed_reaction_identifier') or issues.get('missing_reaction_side') or any(s!='parsed' for s in statuses):
   stats['unknown']+=1;unknown.append({'row':index,'row_group':group,'id':item['reaction_id'],'reason':'cannot_exclude_domain_with_incomplete_structure','issues':issues,'representation':rep})
  else:stats['outside_queries']+=1
 return {'group':group,'start':start,'rows':len(rows),'stats':dict(stats),'scaffolds':dict(scaffolds),'glycoside_sites':dict(glyco),'categories':dict(categories),'candidates':candidates,'unknown':unknown}

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',default='data/raw/ord/task015/source.json');p.add_argument('--output',default='outputs/coverage/task015');p.add_argument('--workers',type=int,default=4);p.add_argument('--row-groups',type=int);a=p.parse_args()
 if a.workers not in range(1,5):raise ValueError('workers must be 1..4')
 src=Path(a.source);m=json.loads(src.read_text());raw=src.parent/Path(m['file']['path']).name
 if digest(raw)!=m['file']['lfs']['oid']:raise ValueError('raw integrity mismatch')
 out=Path(a.output)
 if out.exists():raise ValueError('immutable scan output exists')
 out.mkdir(parents=True);event('TASK-015','scan_start',source=str(raw),output=str(out),workers=a.workers)
 parquet=pq.ParquetFile(raw);limit=min(a.row_groups or parquet.num_row_groups,parquet.num_row_groups)
 metadata={k.decode():v.decode() for k,v in (parquet.schema_arrow.metadata or {}).items()}
 stats=collections.Counter();scaffolds=collections.Counter();glyco=collections.Counter();categories=collections.Counter();batches=[];t=time.monotonic()
 def inputs():
  start=0
  for group in range(limit):
   rows=parquet.read_row_group(group,columns=['reaction_id','reaction']).to_pylist()
   yield group,start,rows;start+=len(rows)
 with (out/'candidates.jsonl').open('x') as cf,(out/'unknown.jsonl').open('x') as uf,multiprocessing.Pool(a.workers,initializer=initialize) as pool:
  for result in pool.imap(process,inputs(),chunksize=1):
   stats.update(result['stats']);scaffolds.update(result['scaffolds']);glyco.update(result['glycoside_sites']);categories.update(result['categories'])
   for row in result.pop('candidates'):cf.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
   for row in result.pop('unknown'):uf.write(json.dumps(row,ensure_ascii=False,sort_keys=True)+'\n')
   batches.append(result)
   if len(batches)%20==0:
    cf.flush();uf.flush();write('TASK-015',str(out/'progress.json'),json.dumps({'groups_done':len(batches),'groups_total':limit,'rows':stats['rows'],'candidates':stats['candidate'],'elapsed_seconds':round(time.monotonic()-t)})+'\n')
 if stats['rows']!=sum(parquet.metadata.row_group(i).num_rows for i in range(limit)):raise AssertionError('row count mismatch')
 if stats['rows']!=sum(stats[k] for k in ['candidate','unknown','outside_queries']):raise AssertionError('dispositions mismatch')
 summary={'task':'TASK-015','dataset_revision':m['revision'],'dataset_metadata':metadata,'total_file_rows':parquet.metadata.num_rows,'scanned_row_groups':limit,'total_file_row_groups':parquet.num_row_groups,'full_file_scan':limit==parquet.num_row_groups,'stats':dict(sorted(stats.items())),'scaffolds_multilabel':dict(sorted(scaffolds.items())),'domain_glycoside_sites_multilabel':dict(sorted(glyco.items())),'categories_multilabel':dict(sorted(categories.items())),'elapsed_seconds':round(time.monotonic()-t),'source_scope':'one consolidated ORD USPTO dataset; not all ORD','representation_policy':'provided reaction (CX)SMILES first; explicit ORD reactant/product SMILES only when reaction identifier absent; agents/workup excluded; raw preserved','limits':['v1 scaffold rules provisional; rule misses not measured','Topology presence/co-occurrence does not identify bond formation or reaction feasibility','No chemical source review or training independence established','Patent extraction may be wrong/incomplete; explicit component and reaction-identifier agreement not audited'],'production_records':0,'human_reviewed_records':0}
 write('TASK-015',str(out/'summary.json'),json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
 write('TASK-015',str(out/'batches.json'),json.dumps(batches,ensure_ascii=False,indent=2)+'\n')
 manifest={'source_manifest':str(src),'source_manifest_sha256':digest(src),'raw_sha256':digest(raw),'rules_sha256':digest('configs/domain_triage.json'),'scanner_sha256':digest(__file__),'rdkit':rdBase.rdkitVersion,'outputs':{x.name:digest(x) for x in out.iterdir() if x.is_file()},'role':'development_exposed candidates; raw/candidates not Git; no active admission'}
 write('TASK-015',str(out/'manifest.json'),json.dumps(manifest,indent=2)+'\n');event('TASK-015','scan_complete',output=str(out),summary=summary)
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

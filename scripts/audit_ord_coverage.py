"""Independent counts, raw checksums, sampled protobuf bindings, protected baseline."""
import collections,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'outputs/validation/task015-dependencies'))
import pyarrow.parquet as pq
from ord_schema.proto import reaction_pb2 as pb
from scripts.operate import write,digest
out=Path('outputs/coverage/task015-summary');summary=json.loads((out/'summary.json').read_text());datasets=json.loads((out/'datasets.json').read_text());counts=collections.Counter();rows=[];bindings=[];source_bytes=0
for ds in datasets:
 manifest=Path(ds['source_manifest']);m=json.loads(manifest.read_text());raw=manifest.parent/Path(m['file']['path']).name
 assert raw.stat().st_size==m['file']['size'];assert digest(raw)==m['file']['lfs']['oid'];source_bytes+=raw.stat().st_size
 parquet=pq.ParquetFile(raw);assert parquet.metadata.num_rows==ds['rows'];folder=Path(ds['folder']);candidate=[json.loads(l) for l in (folder/'candidates.jsonl').read_text().splitlines()];unknown=[json.loads(l) for l in (folder/'unknown.jsonl').read_text().splitlines()]
 assert len(candidate)==ds['candidates'] and len(unknown)==ds['unknown'];counts.update({'rows':parquet.metadata.num_rows,'candidate':len(candidate),'unknown':len(unknown)});rows.extend(candidate)
 sampled=candidate[:2]+candidate[-2:]+[r for r in candidate if any(y['percentage_present'] and y['value']==0 for y in r['yield_measurements'])]
 for r in sampled:
  group=r['row_group'];start=sum(parquet.metadata.row_group(i).num_rows for i in range(group));item=parquet.read_row_group(group).to_pylist()[r['source_row']-start]
  assert item['reaction_id']==r['id'];assert hashlib.sha256(item['reaction']).hexdigest()==r['protobuf_sha256'];rx=pb.Reaction.FromString(item['reaction']);assert rx.provenance.patent==(r['patent'] or '')
  bindings.append({'id':r['id'],'dataset_id':ds['dataset_id'],'row':r['source_row'],'raw_binding':'matched'})
for k,v in counts.items():assert summary['stats'][k]==v
assert source_bytes==summary['source_bytes'];assert summary['stats']['rows']==sum(summary['stats'][k] for k in ['candidate','outside_queries','unknown'])
assert summary['candidate_strict_exact_groups']==len({r['features']['normalized_reaction'] for r in rows if r['features']['normalized_reaction']})
assert summary['glycoside_candidate_rows']==sum(r['features']['domain_glycoside_candidate'] for r in rows)
assert all(r['human_review_status']=='not_performed' and r['production_eligible'] is False and r['split']=='development_exposed' and r['training_overlap']=='unknown' for r in rows)
baseline=json.loads(Path('operations/task015-baseline.json').read_text());drift=[p for p,h in baseline.items() if not Path(p).is_file() or digest(p)!=h];assert not drift,drift
cards=Path('outputs/review/task015-v2');cm=json.loads((cards/'manifest.json').read_text());assert digest(cm['input_review_path'])==cm['input_review_sha256'];assert all(digest(cards/name)==h for name,h in cm['outputs'].items())
result={'passed':True,'datasets_raw_sha256_verified':len(datasets),'source_bytes':source_bytes,'row_counts':dict(counts),'sampled_raw_bindings':bindings,'candidate_annotations_unfilled':len(rows),'protected_files_unchanged':len(baseline),'cards_input_outputs_sha256_verified':True,'scientific_validation':'not performed'}
write('TASK-015','outputs/validation/task015-audit.json',json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='sampled_raw_bindings'},ensure_ascii=False));print('sampled raw bindings',len(bindings))

"""Reconcile raw mirror scans, strict identities and local development overlap."""
import argparse,collections,csv,io,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.operate import write,digest

FAMILIES=['aryl_O_candidate','aryl_C_candidate','other_O_candidate','sugar_sugar_O_candidate']
def families(rows):
 result={}
 for family in FAMILIES:
  left=sum(bool(r['features']['reactant_domain_sites'].get(family)) for r in rows)
  right=sum(bool(r['features']['product_domain_sites'].get(family)) for r in rows)
  either=sum(bool(r['features']['reactant_domain_sites'].get(family) or r['features']['product_domain_sites'].get(family)) for r in rows)
  appearance=sum(not r['features']['reactant_domain_sites'].get(family) and bool(r['features']['product_domain_sites'].get(family)) for r in rows)
  result[family]={'reactant_records':left,'product_records':right,'either_side_records':either,'product_only_presence_records':appearance,'meaning':'topology co-occurrence/appearance only; not bond-formation proof'}
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--mirror-index',default='outputs/coverage/task015-mirror-downloads.json');p.add_argument('--uspto-output',default='outputs/coverage/task015-full');p.add_argument('--output',default='outputs/coverage/task015-summary');a=p.parse_args()
 if Path(a.output).exists():raise ValueError('preserve existing summary; choose --output')
 inventory=json.loads(Path('data/raw/ord/task015/repository-tree.json').read_text());files=[f for f in inventory['entries'] if f.get('path','').endswith('.parquet')]
 mirror=json.loads(Path(a.mirror_index).read_text())
 if len(files)!=53 or len(mirror)!=52 or any(r['status']!='download_verified' or r.get('scan_returncode')!=0 for r in mirror):raise ValueError('not all frozen mirror files successfully scanned')
 folders=[Path(a.uspto_output)]+[Path(r['output']) for r in mirror]
 out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
 scans=[];candidates=[];stat=collections.Counter();unknown_lines=0
 for folder in folders:
  summary=json.loads((folder/'summary.json').read_text());manifest=json.loads((folder/'manifest.json').read_text())
  if not summary['full_file_scan']:raise ValueError('partial scan')
  for name,expected in manifest['outputs'].items():
   if digest(folder/name)!=expected:raise ValueError('scan output hash mismatch')
  rows=[json.loads(l) for l in (folder/'candidates.jsonl').read_text().splitlines()]
  n_unknown=sum(1 for _ in (folder/'unknown.jsonl').open());unknown_lines+=n_unknown
  if len(rows)!=summary['stats'].get('candidate',0) or n_unknown!=summary['stats'].get('unknown',0):raise ValueError('raw disposition counts disagree')
  stat.update(summary['stats']);meta=summary['dataset_metadata']
  entry={'dataset_id':meta['ord.dataset_id'],'name':meta.get('ord.name'),'rows':summary['stats']['rows'],'candidates':len(rows),'glycosides':summary['stats'].get('domain_glycoside_candidate',0),'unknown':n_unknown,'folder':str(folder),'source_manifest':manifest['source_manifest'],'families':families(rows)}
  scans.append(entry)
  for row in rows:row['dataset_id']=meta['ord.dataset_id'];row['dataset_name']=meta.get('ord.name');row['scan_folder']=str(folder)
  candidates.extend(rows)
 local=[json.loads(l) for l in Path('outputs/triage/task014-final/pilot.jsonl').read_text().splitlines()];guide=[json.loads(l) for l in Path('outputs/triage/task014-final/guide.jsonl').read_text().splitlines()]
 identities=collections.defaultdict(list)
 for row in candidates:
  if row['features']['normalized_reaction']:identities[row['features']['normalized_reaction']].append(row)
 local_set={r['features']['normalized_reaction'] for r in local if r['features']['normalized_reaction']};guide_set={r['features']['normalized_reaction'] for r in guide if r['features']['normalized_reaction']}
 overlap=set(identities)&local_set;guide_overlap=set(identities)&guide_set
 glyco=[r for r in candidates if r['features']['domain_glycoside_candidate']];glyco_ids={r['features']['normalized_reaction'] for r in glyco if r['features']['normalized_reaction']}
 summary={'scope':'53 Parquet files in frozen official HF mirror, not retired historical files or unmirrored versions','revision':inventory['revision'],'datasets':len(scans),'source_bytes':sum(f['size'] for f in files),'stats':dict(sorted(stat.items())),'candidate_unique_record_ids':len({r['id'] for r in candidates}),'candidate_strict_exact_groups':len(identities),'candidate_without_strict_identity':sum(not r['features']['normalized_reaction'] for r in candidates),'glycoside_candidate_rows':len(glyco),'glycoside_strict_exact_groups':len(glyco_ids),'glycoside_patent_strings':len({r['patent'] for r in glyco if r['patent']}),'domain_glycoside_families_row_counts':families(glyco),'local_pilot_families_row_counts':families(local),'guide_families_row_counts':families(guide),'local_strict_exact_overlap_groups':len(overlap),'local_overlap_source_rows':sum(r['features']['normalized_reaction'] in overlap for r in candidates),'guide_strict_exact_overlap_groups':len(guide_overlap),'new_to_local_strict_exact_groups':len(set(identities)-local_set),'glycoside_overlap_with_local_groups':len(glyco_ids&local_set),'glycoside_new_to_local_groups':len(glyco_ids-local_set),'datasets_with_candidate':sum(s['candidates']>0 for s in scans),'datasets_with_glycoside_candidate':sum(s['glycosides']>0 for s in scans),'primary_source_verified':0,'human_reviewed':0,'production_eligible':0,'training_independence':'unknown; upstream train/validation/test labels are NOT this project blind splits','chemical_precision_recall':None,'limitations':['Nine provisional v1 scaffold queries do not define chemical recall','Strict identities retain all listed reactants/multiplicity/stereo/salts; different source conventions can prevent overlap matches','Any number of source records or strict identities is not a count of independent experimental instances','Raw USPTO and upstream processed ML splits may overlap; preserve source copies and report strict deduplication','Not all explicit ORD component structures are cross-checked against reaction identifiers','One present-zero yield is retained; missing yields remain missing, no assignment from procedure text']}
 write('TASK-015',str(out/'summary.json'),json.dumps(summary,ensure_ascii=False,indent=2)+'\n');write('TASK-015',str(out/'datasets.json'),json.dumps(scans,ensure_ascii=False,indent=2)+'\n')
 write('TASK-015',str(out/'glycoside-candidates.jsonl'),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in glyco))
 buffer=io.StringIO();writer=csv.DictWriter(buffer,fieldnames=['dataset_id','dataset_name','id','patent','patent_url','source_row','row_group','reactant_scaffolds','product_scaffolds','reactant_domain_sites','product_domain_sites','strict_overlap_with_local','human_review_status','production_eligible'],delimiter='\t',lineterminator='\n');writer.writeheader()
 for r in glyco:
  f=r['features'];writer.writerow({'dataset_id':r['dataset_id'],'dataset_name':r['dataset_name'],'id':r['id'],'patent':r['patent'],'patent_url':'https://patents.google.com/patent/'+r['patent'] if r['patent'] else '', 'source_row':r['source_row'],'row_group':r['row_group'],'reactant_scaffolds':';'.join(f['reactant_scaffolds']),'product_scaffolds':';'.join(f['product_scaffolds']),'reactant_domain_sites':json.dumps(f['reactant_domain_sites']),'product_domain_sites':json.dumps(f['product_domain_sites']),'strict_overlap_with_local':f['normalized_reaction'] in local_set,'human_review_status':r['human_review_status'],'production_eligible':False})
 write('TASK-015',str(out/'glycoside-candidates.tsv'),buffer.getvalue())
 write('TASK-015',str(out/'strict-overlap.json'),json.dumps({'local_overlap_reactions':sorted(overlap),'guide_overlap_reactions':sorted(guide_overlap),'meaning':'strict representation overlap only; zero overlap does not establish scientific or training independence'},indent=2)+'\n')
 write('TASK-015',str(out/'manifest.json'),json.dumps({'inventory_sha256':digest('data/raw/ord/task015/repository-tree.json'),'scan_manifests':{str(p/'manifest.json'):digest(p/'manifest.json') for p in folders},'local_pilot_sha256':digest('outputs/triage/task014-final/pilot.jsonl'),'outputs':{p.name:digest(p) for p in out.iterdir() if p.is_file()},'summarizer_sha256':digest(__file__)},indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

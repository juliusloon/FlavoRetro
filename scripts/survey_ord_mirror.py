"""Download and scan all other revision-pinned mirror Parquet files, within 2 GB."""
import argparse,concurrent.futures,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fetch_ord import fetch_manifest
from scripts.operate import write,event
p=argparse.ArgumentParser();p.add_argument('--fetch-only',action='store_true');p.add_argument('--output-prefix',default='outputs/coverage/task015-mirror');p.add_argument('--download-index',default='outputs/coverage/task015-mirror-downloads.json');a=p.parse_args()
x=json.loads(Path('data/raw/ord/task015/repository-tree.json').read_text());base=json.loads(Path('data/raw/ord/task015/source.json').read_text());files=[f for f in x['entries'] if f.get('path','').endswith('.parquet')]
if x['pagination']:raise ValueError('incomplete inventory')
if sum(f['size'] for f in files)>2_000_000_000:raise ValueError('total source budget exceeded')
if Path(a.download_index).exists():raise ValueError('preserve existing survey index; choose --download-index and --output-prefix')
for f in files:
 if '1158e351' not in f['path']:
  target=Path(a.output_prefix)/Path(f['path']).stem
  if target.exists() or Path(str(target)+'-command.log').exists():raise ValueError('preserve existing scan evidence; choose --output-prefix')
paths=[]
for f in files:
 if '1158e351' in f['path']:continue
 folder='data/raw/ord/task015/current-mirror/'+Path(f['path']).stem
 manifest=folder+'/source.json';m={**base,'file':f,'subset':'non-USPTO current mirror dataset; scientific role not yet reviewed'}
 if not Path(manifest).exists():write('TASK-015',manifest,json.dumps(m,indent=2)+'\n')
 paths.append(manifest)
results=[]
def fetch(path):
 try:fetch_manifest(path);return {'manifest':path,'status':'download_verified'}
 except Exception as e:return {'manifest':path,'status':'download_failed','error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for result in pool.map(fetch,paths):
  results.append(result);write('TASK-015',a.download_index,json.dumps(results,indent=2)+'\n')
if a.fetch_only:sys.exit(0)
for result in results:
 if result['status']!='download_verified':continue
 output=a.output_prefix+'/' +Path(result['manifest']).parent.name
 cmd=[sys.executable,'-B','scripts/scan_ord.py','--source',result['manifest'],'--output',output,'--workers','4']
 event('TASK-015','dataset_scan_command',argv=cmd)
 proc=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 write('TASK-015',output+'-command.log',proc.stdout);result['scan_returncode']=proc.returncode;result['output']=output
 write('TASK-015',a.download_index,json.dumps(results,indent=2)+'\n')
 if proc.returncode:print('Scan failed',result['manifest'],proc.stdout[-500:])
 else:print('Scanned',Path(result['manifest']).parent.name,flush=True)
print(json.dumps({'datasets':len(results),'download_failed':sum(r['status']=='download_failed' for r in results),'scan_failed':sum(r.get('scan_returncode',0)!=0 for r in results)}))

"""Fetch one revision-pinned ORD file; preserve failed partials, verify LFS SHA."""
import argparse, json, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import requests
from scripts.operate import event,digest,write

def fetch_manifest(path):
 manifest=Path(path);m=json.loads(manifest.read_text());root=manifest.parent
 target=root/Path(m['file']['path']).name
 expected=m['file']['lfs']['oid'];size=m['file']['size']
 if size>2_000_000_000:raise ValueError('source download budget exceeded')
 if target.exists():
  if target.stat().st_size!=size or digest(target)!=expected:raise ValueError('existing raw file mismatch; preserve and stop')
  print('Already verified',target);return
 url='https://huggingface.co/datasets/'+m['repository']+'/resolve/'+m['revision']+'/'+m['file']['path']+'?download=true'
 for attempt in (1,2):
  partial=target.with_suffix(target.suffix+f'.attempt{attempt}.partial')
  if partial.exists():raise ValueError('preserve existing partial; use a new task output')
  try:
   event('TASK-015','download_start',url=url,path=str(partial),attempt=attempt)
   with requests.get(url,stream=True,timeout=(30,60)) as r:
    r.raise_for_status();n=0;last=0
    with partial.open('xb') as f:
     for block in r.iter_content(1024*1024):
      f.write(block);n+=len(block)
      if n>size:raise ValueError('download larger than manifest')
      if time.monotonic()-last>15:
       write('TASK-015',str(root/'progress.json'),json.dumps({'phase':'download','attempt':attempt,'bytes':n,'expected':size})+'\n');last=time.monotonic()
   sha=digest(partial)
   if n!=size or sha!=expected:raise ValueError('LFS integrity mismatch')
   partial.rename(target)
   event('TASK-015','download_verified',path=str(target),sha256=sha,bytes=n)
   write('TASK-015',str(root/'download.json'),json.dumps({'url':url,'path':str(target),'bytes':n,'sha256':sha,'verified':True},indent=2)+'\n')
   print('Verified',n,sha);return
  except Exception as e:
   event('TASK-015','download_failed',attempt=attempt,error=str(e),partial=str(partial))
   print('Attempt failed:',type(e).__name__,str(e),flush=True)
   if attempt==2:raise
def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);a=p.parse_args();fetch_manifest(a.manifest)
if __name__=='__main__':main()

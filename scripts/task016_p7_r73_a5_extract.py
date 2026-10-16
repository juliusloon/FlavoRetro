"""R73 A5 independent stdlib-JATS reader. Never consumes A4 output."""
from pathlib import Path
import json, hashlib, sys, xml.etree.ElementTree as ET
from scripts.operate import write, ROOT
from scripts import task016_p7_full_qualification_harness_v4 as fq
from scripts.task016_p7_orchestrate import role_manifest
T='TASK-016-P7'
SCRIPT='scripts/task016_p7_r73_a5_extract.py'
READER='A5-R73-independent-stdlib-20261012-cano-r73_five_originals_a5'
BINDING='outputs/task016-p7/v1/governance/R73-five-originals-cross-axis-read-binding-v1/both_G5_ready_before_first_read.json'
def put(path,value):
    p=ROOT/path
    if p.exists(): raise RuntimeError('immutable output already exists: '+str(path))
    write(T,str(path),json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n')
def jsonl(path,rows):
    if (ROOT/path).exists(): raise RuntimeError('immutable output already exists: '+str(path))
    write(T,str(path),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True,allow_nan=False)+'\n' for r in rows))
def folder(f):return Path('outputs/task016-p7/v1')/f/'E02/fresh'/f'{f}-E02-R73-five-originals-full-qualification-v1'/'A5'
def bindings():
    b=json.loads((ROOT/BINDING).read_text())
    for f in ('C','SS'):
        fq.bound(b['contracts'][f]);fq.bound(b['G5'][f])
    return b
def preregister():
    b=bindings()
    for f in ('C','SS'):
        c=fq.load(b['contracts'][f]);u=fq.load(c['raw_source_universe'])
        put(folder(f)/'preregistration.json',dict(task=T,agent_role='A5',epoch_id=f+'-E02',timestamp=fq.now(),reader_id=READER,parser='stdlib xml.etree.ElementTree independently authored; indexed original-element XPath; all body paragraphs/tables/figures plus advertised links',runner=fq.pointer(SCRIPT),cross_axis_binding=fq.pointer(BINDING),contract=b['contracts'][f],G5=b['G5'][f],raw_source_universe=c['raw_source_universe'],raw_input_pointers={s['source_id']:s['raw_files'] for s in u['source_candidates']},both_axis_receipts_required_before_decode=True,read_other_extractor_output=False,read_model_outcome=False,scientific_bytes_decoded=False,prior_read_unknown_retained=True,approval_type='agent_delegated',human_reviewed=False))
    print(json.dumps({'reader_id':READER,'runner':fq.pointer(SCRIPT),'preregistered_families':['C','SS']}))
def local(t):return t.rsplit('}',1)[-1]
def parse_jats(data):
    root=ET.fromstring(data)
    paths={root:'/'+local(root.tag)+'[1]'}
    for parent in root.iter():
        counts={}
        for child in parent:
            tag=local(child.tag);counts[tag]=counts.get(tag,0)+1
            paths[child]=paths[parent]+'/'+tag+'['+str(counts[tag])+']'
    units=[];links=[];counts={'body_paragraphs':0,'body_figures':0,'body_tables':0}
    for node in root.iter():
        tag=local(node.tag);path=paths[node]
        in_body='/body[' in path
        if tag in ('p','title','fig','table-wrap','supplementary-material') and (in_body or tag=='supplementary-material'):
            text=' '.join(''.join(node.itertext()).split())
            if text: units.append({'xpath':path,'tag':tag,'text':text,'attributes':dict(node.attrib),'in_body':in_body})
        if in_body and tag=='p':counts['body_paragraphs']+=1
        if in_body and tag=='fig':counts['body_figures']+=1
        if in_body and tag=='table-wrap':counts['body_tables']+=1
        for attr,val in node.attrib.items():
            if local(attr)=='href':
                links.append({'xpath':path,'element':tag,'attribute':attr,'href':val,'text':' '.join(''.join(node.itertext()).split()),'in_body':in_body})
    return units,links,counts

def extract():
    b=bindings();contracts={f:fq.load(b['contracts'][f]) for f in ('C','SS')}
    universes={f:fq.load(contracts[f]['raw_source_universe']) for f in ('C','SS')}
    for f in ('C','SS'):
        p=json.loads((ROOT/folder(f)/'preregistration.json').read_text());assert p['reader_id']==READER and p['runner']==fq.pointer(SCRIPT)
    sources=universes['C']['source_candidates'];assert sources==universes['SS']['source_candidates']
    receipts={f:[] for f in ('C','SS')};all_units={f:[] for f in ('C','SS')};summaries={f:[] for f in ('C','SS')}
    for src in sources:
        opened={f:fq.open_for_first_scientific_read(b['contracts'][f],b['G5'][f],src['source_id'],'A5',READER) for f in ('C','SS')}
        # No XML parsing or decoding is performed until both axis receipts exist.
        for f in ('C','SS'):
            receipt=fq.load(opened[f]['receipt'])
            receipts[f].append({**receipt,'receipt_pointer':opened[f]['receipt']})
        for raw in src['raw_files']:
            payload=opened['C']['payloads'][raw['path']]
            assert hashlib.sha256(payload).hexdigest()==raw['sha256'] and payload==opened['SS']['payloads'][raw['path']]
            units,links,counts=parse_jats(payload)
            for f in ('C','SS'):
                all_units[f]+=[{**u,'source_id':src['source_id'],'raw':raw,'reader_id':READER,'scientific_read_receipt':opened[f]['receipt']} for u in units]
                summaries[f].append(dict(source_id=src['source_id'],raw=raw,counts=counts,advertised_links=links,receipt=opened[f]['receipt'],scientific_body_read=True,prior_scientific_read=None,fresh_admitted=0,permanent_future_exclusion=True))
    for f in ('C','SS'):
        jsonl(folder(f)/'permanent_read_receipts.jsonl',receipts[f])
        jsonl(folder(f)/'jats_body_units.jsonl',all_units[f])
        put(folder(f)/'jats_read_inventory.json',dict(task=T,agent_role='A5',epoch_id=f+'-E02',reader_id=READER,timestamp=fq.now(),contract_sha256=b['contracts'][f]['sha256'],sources=summaries[f],actual_sources_read=len(summaries[f]),actual_fresh_admitted=0,read_other_extractor_output=False,read_model_outcome=False))
    print(json.dumps({'reader_id':READER,'sources_per_family':len(sources),'body_paragraph_counts':[s['counts']['body_paragraphs'] for s in summaries['C']],'outputs':{f:str(folder(f)) for f in ('C','SS')}}))
if __name__=='__main__':
    {'preregister':preregister,'extract':extract}[sys.argv[1]]()

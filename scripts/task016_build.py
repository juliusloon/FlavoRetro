"""Build frozen source instances and panel BEFORE observing model coverage."""
import json,sys,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
from rdkit import Chem,rdBase
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.operate import write,event
from flavoretro.open_reactions import rhea_rows,paragraphs
from flavoretro.glycoside_expansion import extract_template,apply_template
from flavoretro.reviewed_resources import canonical_side,reaction_signature,load_review
from flavoretro.resources import sha
root=Path.cwd();out=root/'outputs/task016/v1';discovery=root/'data/raw/task016/discovery/2026-10-06'
assert not (out/'development_contract.json').exists(), 'immutable panel already frozen'
rows=list(rhea_rows(discovery/'rhea.tsv',discovery/'rhea_dirs',discovery/'rhea_smiles'))
by_id={r['lr_id']:r for r in rows if r['parse_status']=='parsed'}
papers={p.stem:p for p in (root/'data/raw/task016/europepmc/2026-10-06').glob('PMC*.xml') if p.stem!='PMC6139687'}
# Exact names identify source compounds; Rhea supplies structures/ionization.
# The 4-prime luteolin and kaempferol structures come from hydrolysis entries,
# but formation direction/donor/enzyme come exclusively from forward experiments.
seeds=[('19578','PMC5897352','OcUGT1','luteolin 7-O-glucoside (1c)', 'NMR assignment, metabolite 1c', 'O_7'),
       ('69668','PMC5897352','OcUGT1','luteolin 4′-O-glucoside (1b)', 'NMR assignment, metabolite 1b', 'O_4prime'),
       ('61181','PMC5818429','CsUGT76F1','glucosylate quercetin at the 3- or 7-hydrogen position', 'Figure 5D product assignment, LC-MS/reference standards', 'O_3'),
       ('69660','PMC5818429','CsUGT76F1','kaempferol 3-O-glucoside', 'Figure 5E product assignment, LC-MS/reference standards', 'O_3')]
instances=[];validation=[];templates=[];dispositions=[]
for lr,pmcid,enzyme,anchor,identification,position in seeds:
    record=by_id[lr];paper=papers[pmcid];xml=ET.parse(paper).getroot();pp=list(paragraphs(xml))
    evidence=next(p for p in pp if anchor in p['text'])
    if lr in ['69668','69660']:
        target=next(s for s in record['reactants'] if Chem.MolFromSmiles(s).GetNumAtoms()>10)
        acceptor=next(s for s in record['products'] if Chem.MolFromSmiles(s).GetNumAtoms()>10)
        donor=next(s for s in by_id['61181']['reactants'] if any(a.GetAtomicNum()==15 for a in Chem.MolFromSmiles(s).GetAtoms()))
    else:
        target=next(s for s in record['products'] if Chem.MolFromSmiles(s).GetNumAtoms()>10 and 'P' not in s)
        acceptor=next(s for s in record['reactants'] if 'P' not in s)
        donor=next(s for s in record['reactants'] if 'P' in s)
    condition_anchor='phosphate buffer (10' if enzyme=='OcUGT1' else 'The standard reaction mixture for enzyme assay'
    condition=next(p for p in pp if condition_anchor in p['text'])
    license_el=xml.find('.//license');lic=''.join(license_el.itertext()) if license_el is not None else None
    doi=xml.find(".//article-id[@pub-id-type='doi']").text
    identifier=f'{pmcid}:{enzyme}:{position}:{lr}'
    instance=dict(instance_id=identifier,provider='EuropePMC+Rhea',dataset='task016-open-source-v1',version='2026-10-06',record_id=record['record_id'],
                  record_type='specific_in_vitro_assay_source_annotation',review_type='agent_delegated',development_exposed=True,
                  target=target,acceptor=acceptor,donor=donor,reference_precursors=sorted([acceptor,donor]),
                  reference_signature=reaction_signature([acceptor,donor],[target]),strict_source_signature=record['strict_source_signature'],
                  rhea_context_role='formation_equation' if lr not in ['69668','69660'] else 'compound_structures_only_hydrolysis_NOT_reversed',
                  raw_reactants=record['raw_reaction_smiles'].split('>>')[0],raw_products=record['raw_reaction_smiles'].split('>>')[1],
                  structural_authority='Rhea/ChEBI encoded species; article names linked by agent; no source SMILES in article',
                  source_conditions=dict(temperature_c=50 if enzyme=='OcUGT1' else 30,pH=8 if enzyme=='OcUGT1' else 7.5,time_hours=2 if enzyme=='OcUGT1' else 1,locator=condition['locator'],specificity='source assay context; not a verified prediction condition'),
                  source_yield=dict(value=None,status='no product-specific numeric yield extracted; no inference from kinetic/activity/aggregate figure'),
                  catalyst_mode='enzymatic',required_context=dict(enzyme=enzyme,donor='UDP-alpha-D-glucose',cofactors_status='not_claimed',scope='exact registered source species only'),
                  provenance=dict(doi=doi,pmcid=pmcid,raw_path=str(paper.relative_to(root)),raw_sha256=sha(paper),locator=evidence['locator'],locator_text_sha256=hashlib.sha256(evidence['text'].encode()).hexdigest(),identification=identification,license=lic,rhea_lr_id=lr,rhea_record_id=record['record_id'],rhea_smiles_path=str((discovery/'rhea_smiles').relative_to(root)),rhea_smiles_sha256=sha(discovery/'rhea_smiles')),
                  category='primary_O_formation',position=position,prediction_conditions_verified=False,independent_chemical_validation=False,human_reviewed=False)
    instances.append(instance)
# The denominator is selected by source-quality eligibility and fixed IDs,
# independent of either generic policy's successes or failures.
instances.sort(key=lambda r:r['instance_id'])
for inst in instances:
    t=dict(template_id='task016:'+hashlib.sha256(inst['reference_signature'].encode()).hexdigest()[:16],support_instances=[inst['instance_id']],allowed_targets=[inst['target']],required_context=inst['required_context'],category=inst['category'],position=inst['position'],status='research_candidate',transfer_status='disabled_exact_registered_species_only',prediction_conditions_verified=False)
    try:
        t.update(extract_template(inst));supports=apply_template(t,inst['target']);positive=canonical_side(inst['reference_precursors']) in [o.get('precursors') for o in supports]
        negative=Chem.MolFromSmiles(inst['target']);site=t['center']['anomeric_candidate'];negative.GetAtomWithIdx(site).InvertChirality();wrong_sugar=Chem.MolToSmiles(negative,isomericSmiles=True)
        wrong_context={**t['required_context'],'enzyme':'unregistered_enzyme'}
        neg1=apply_template(t,wrong_sugar);neg2=apply_template(t,inst['target'],wrong_context)
        item=dict(template_id=t['template_id'],support_instances=t['support_instances'],support_denominator=1,support_passed=int(positive),outcomes=supports,boundary_fixtures=[dict(kind='anomeric_epimer',target=wrong_sugar,expected='reject',accepted=bool(neg1)),dict(kind='wrong_enzyme_context',context=wrong_context,expected='reject',accepted=bool(neg2))],boundary_violations=int(bool(neg1))+int(bool(neg2)))
        validation.append(item)
        assert positive and item['boundary_violations']==0, 'source/boundary gate failed'
        t['validation_status']='source_reconstruction_passed';templates.append(t)
    except Exception as exc:
        validation.append(dict(template_id=t['template_id'],support_instances=t['support_instances'],support_denominator=1,support_passed=0,status='failed',error=str(exc)))
        raise
for row in rows:
    linked=[i['instance_id'] for i in instances if i['record_id']==row['record_id']]
    reason='structure linked to separately documented forward assay' if linked else ('unadmitted reaction knowledge; specific source not established' if 'UDP' in row['raw']['Equation'] else 'support/non-glycosylation knowledge retained; not main formation')
    dispositions.append(dict(provider='Rhea',record_id=row['record_id'],record_type=row['record_type'],parse_status=row['parse_status'],disposition='linked_structure' if linked else 'retained_knowledge',reason=reason,instance_ids=linked,raw_path=str((discovery/'rhea.tsv').relative_to(root)),raw_sha256=sha(discovery/'rhea.tsv')))
metadata=json.loads((discovery/'europepmc.json').read_text())['resultList']['result']
for row in metadata:
    linked=[i['instance_id'] for i in instances if i['provenance']['pmcid']==row.get('pmcid')]
    dispositions.append(dict(provider='EuropePMC',record_id=row['id'],pmcid=row.get('pmcid'),disposition='source_assay_linked' if linked else 'metadata_only',reason='registered assay anchors' if linked else 'discovery hit is not an extracted experiment',instance_ids=linked,raw_path=str((discovery/'europepmc.json').relative_to(root)),raw_sha256=sha(discovery/'europepmc.json')))
for row in json.loads((discovery/'zenodo.json').read_text())['hits']['hits']:
    dispositions.append(dict(provider='Zenodo',record_id=str(row['id']),disposition='metadata_only',reason='no confirmed flavonoid glycoside HTE reaction table in frozen search results; no download quota',license=row['metadata'].get('license'),title=row['metadata'].get('title'),raw_path=str((discovery/'zenodo.json').relative_to(root)),raw_sha256=sha(discovery/'zenodo.json')))
# Do not re-download ORD: verify the current official mirror revision equals the frozen one.
hf=json.loads((discovery/'hf').read_text());assert hf['sha']=='93475c46949f9218e1dfb6624096025135db2add'
ord_files=sorted((root/'data/raw/ord/task015').rglob('*.parquet'));assert len(ord_files)==53
ord_reuse=[dict(path=str(p.relative_to(root)),sha256=sha(p),bytes=p.stat().st_size) for p in ord_files]
source_files=[dict(path=str(p.relative_to(root)),sha256=sha(p),bytes=p.stat().st_size) for p in sorted((root/'data/raw/task016').rglob('*')) if p.is_file()]
assert sum(r['bytes'] for r in source_files)<=5*1024**3
source_manifest=dict(schema_version=1,version='task016-open-v1',queries=json.loads((out/'discovery_manifest.json').read_text()),files=source_files,ord_reuse=dict(revision=hf['sha'],new_download_bytes=0,files=ord_reuse,coverage_scope='reuse TASK-015 frozen whole-corpus audit; no new ORD source claim'),access_failures=json.loads((out/'acquisition_attempts.json').read_text()),alternate_pmc_cloud=json.loads((out/'pmc_cloud_https_manifest.json').read_text()),source_counts=dict(rhea_records=len(rows),europepmc_discovery_records=len(metadata),zenodo_records=10,specific_assays=len(instances),exact_reference_groups=len({i['reference_signature'] for i in instances}),position_classes=len({i['position'] for i in instances})),disposition_universe='all records in frozen Rhea query + EuropePMC discovery page + Zenodo page; whole ORD counts inherited separately, not inflated into this universe',limitations=['C-glycosides: curated identity and whole-cell pathway evidence retained; no isolated single-step assay admitted','sugar-sugar: Montbretin paper acquisition failed / unavailable in frozen PMC cloud listing','HTE: discovery-only; no target-relevant table admitted'])
policy=dict(default_enabled=False,domain_cap_per_molecule=4,prior=0.2,weight=1.0,merge='existing optimized template fusion; domain exact-target guard; action metric dedup by exact precursor multiset, not template ID',filter='generic unchanged; source-bound enzymatic actions use known_hazards plus strict source/template guard, no USPTO quick-filter score interpreted as enzyme feasibility')
contract=dict(schema_version=1,version='task016-development-v1',approval_type='agent_delegated',scope='development_exposed source-instance reconstruction and candidate coverage; not blind chemical accuracy',selection_rule='all four admitted in vitro forward assay instances; source NMR/LC-MS identity, full donor, fixed instance ID ordering; no baseline result selection',instances=[i['instance_id'] for i in instances],primary_targets=sorted({i['target'] for i in instances}),support_targets=[],N=len({i['reference_signature'] for i in instances}),N_support=0,seeds=[0,1,2],candidate_stock=True,review_binding=load_review().binding,budget=dict(mode='quick',engine='optimized',seconds=12.0,iterations=20,depth=2,branching=12,nodes=120,top_k=5),worker_wall_limit=60,run_budget=120,engineering_reserved=12,policy=policy,matching='map-stripped isomeric canonical SMILES sorted component multiset; direction, stereo, isotopes, salt and multiplicity retained',training_overlap='unknown',generalization='none; v1 deliberately restricted to source-backed exact product species')
reference=[dict(instance_id=i['instance_id'],target=i['target'],reference_precursors=i['reference_precursors'],reference_signature=i['reference_signature'],included=[dict(smiles=i['acceptor'],role='acceptor',reason='substrate in source assay'),dict(smiles=i['donor'],role='donor',reason='UDP-glucose in source assay; full donor retained')],excluded=[dict(role='enzyme/buffer/solvent',reason='source catalyst/conditions; retained context, not stoichiometric molecular precursor'),dict(role='UDP and H+',reason='Rhea forward coproducts, not input precursors; strict full Rhea equation comparison separate')],strict_source_signature=i['strict_source_signature']) for i in instances]
def save(name,obj,jsonl=False):write('TASK-016',str((out/name).relative_to(root)),''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in obj) if jsonl else json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
for name,obj,jl in [('source_manifest.json',source_manifest,False),('record_dispositions.jsonl',dispositions,True),('knowledge_records.jsonl',rows,True),('instances.jsonl',instances,True),('development_contract.json',contract,False),('reference_precursors.jsonl',reference,True),('templates.jsonl',templates,True),('template_validation.jsonl',validation,True)]:save(name,obj,jl)
manifest=dict(schema_version=1,version='task016-open-v1',rdkit=rdBase.rdkitVersion,review_binding=load_review().binding,policy=policy,files_sha256={n:sha(out/n) for n in ['source_manifest.json','instances.jsonl','development_contract.json','reference_precursors.jsonl','templates.jsonl','template_validation.jsonl']},raw_dependencies_sha256={r['path']:r['sha256'] for r in source_files},claim='machine extraction / agent source annotation; no human-reviewed or independent chemical validation')
save('template_source_manifest.json',manifest)
setting=dict(version=1,default_enabled=False,manifest='outputs/task016/v1/template_source_manifest.json',manifest_sha256=sha(out/'template_source_manifest.json'),status='development_source_bound_not_production')
for name in ['configs/glycoside-expansion.json','flavoretro/assets/configs/glycoside-expansion.json']:write('TASK-016',name,json.dumps(setting,indent=2)+'\n')
print(json.dumps(dict(counts=source_manifest['source_counts'],dispositions=len(dispositions),templates=len(templates),N=contract['N'],raw_bytes=sum(r['bytes'] for r in source_files),manifest_sha256=setting['manifest_sha256']),indent=2))

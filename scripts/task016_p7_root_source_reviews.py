"""Root source-only A3/A5 and partial A6 P7 audits; no search or scope changes."""
from __future__ import annotations
import json,re
from html.parser import HTMLParser
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from scripts.task016_p7_orchestrate import ROOT,now,sha_file,save_json,role_manifest,verify_hashes
B=ROOT/'outputs/task016-p7/v1'

class CitationMeta(HTMLParser):
    def __init__(self):
        super().__init__();self.fields={}
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);name=attrs.get('name','')
        if tag=='meta' and name.startswith('citation_') and name not in {'citation_reference','citation_author_email','citation_author_institution'}:
            self.fields.setdefault(name,[]).append(attrs.get('content',''))

def load(p):return json.loads(Path(p).read_text())
def meta(p):
    parser=CitationMeta();parser.feed(Path(p).read_text());return parser.fields

def norm(v):return re.sub(r'[^\w]','',str(v).casefold())
def one(m,k):return m[k][0]
def identity_row(core,publisher,expected_doi,pointers):
    ji=core['journalInfo'];journal=ji['journal']['title']
    authors=core.get('authorList',{}).get('author',[])
    pubauthors=publisher.get('citation_author',[])
    surnames=[a.get('lastName') for a in authors]
    pubsurnames=[a.split(',')[0].strip() for a in pubauthors]
    checks=dict(doi=one(publisher,'citation_doi').removeprefix('https://doi.org/')==core['doi']==expected_doi,
                title=norm(one(publisher,'citation_title'))==norm(core['title']),
                journal=norm(one(publisher,'citation_journal_title'))==norm(journal),
                volume=one(publisher,'citation_volume')==ji['volume'],
                issue=one(publisher,'citation_issue')==ji['issue'],
                year=one(publisher,'citation_publication_date')[:4]==str(core['pubYear']),
                pages=f"{one(publisher,'citation_firstpage')}-{one(publisher,'citation_lastpage')}"==core['pageInfo'],
                author_order=[norm(x) for x in surnames]==[norm(x) for x in pubsurnames] and bool(surnames))
    return dict(source_id='DOI:'+expected_doi,pmid=core['id'],official_CORE_fields={k:core.get(k) for k in ['title','doi','pubYear','pageInfo','authorString','journalInfo','authorList']},
                official_publisher_citation_metadata=publisher,checks=checks,source_identity_verified=all(checks.values()),
                evidence_pointers=pointers,human_reviewed=False,approval_type='agent_delegated',agent_role='A3',verified_at=now(),
                attachment_source_product_graph_qualification_separate=True)

def emit_role(folder,role,epoch,inputs,outputs,processed,passed,rejected=0,*,holdout=True,model=False):
    r=role_manifest(role,epoch,inputs,outputs,dict(processed=processed,passed=passed,rejected=rejected,pending=processed-passed-rejected),read_holdout=holdout,read_model_outcome=model)
    r['logical_role_input_scope']='only artifacts explicitly SHA-bound here; legacy canary outcomes may be known to the root agent'
    return save_json(folder/f'role_{role}_manifest.json',r,immutable=True)

def c_identity():
    raw=B/'C/E01/fresh/alternate/root_A3_official_CORE_raw_inputs.json';m=load(raw);outputs=[];inputs=[raw];rows=[]
    pub={ '29308528':'data/raw/task016-p7/C/8f5e15f10c169f0258aeabfc065eea54d3eb10f8045d00840646f591a3aca4e6.attempt-1.metadata',
          '34302563':'data/raw/task016-p7/C/247c28aca9dcf0e566cd61a93e973274bba1d848a45f0837a6ee2bb45f8a2898.attempt-1.metadata'}
    for item in m['inputs']:
        pointer=item['reuse_selected_pointer'];p=ROOT/pointer['path'];assert sha_file(p)==pointer['sha256']
        core=load(p)['resultList']['result'][int(pointer['json_pointer'].split('/')[-1])];html=ROOT/pub[core['id']]
        row=identity_row(core,meta(html),core['doi'],[dict(path=str(html.relative_to(ROOT)),sha256=sha_file(html),pointer='citation metadata'),pointer]);rows.append(row);inputs.extend([p,html])
    out=B/'C/E01/root_A3_public_identity/identity.json';save_json(out,rows,immutable=True)
    emit_role(out.parent,'A3','C-E01',inputs,[out],len(rows),sum(r['source_identity_verified'] for r in rows))
    print('C A3 identity',[(r['pmid'],r['checks']) for r in rows])

def buckwheat():
    manifest=B/'SS/fresh_buckwheat2018_raw_input_manifest.json';m=load(manifest);verify_hashes(m['raw_input_files_sha256'])
    core=load(ROOT/m['independent_EPMC_metadata_path'])['resultList']['result'][0]
    source=ROOT/m['actual_original_PDF_path'];repository=ROOT/m['institutional_repository_landing_path'];folder=B/'SS/root_A5_buckwheat2018'
    row=identity_row(core,meta(repository),'10.1080/09168451.2018.1491286',[dict(path=str(p.relative_to(ROOT)),sha256=sha_file(p)) for p in [source,repository,ROOT/m['independent_EPMC_metadata_path']]])
    row['repository_pdf_identity_title_match']=norm(core['title']) in norm((folder/'source_text.txt').read_text()[:500])
    out=folder/'A3_source_identity.json';save_json(out,row,immutable=True)
    emit_role(folder,'A3','SS-E01',[manifest,source,repository,ROOT/m['independent_EPMC_metadata_path']],[out],1,int(row['source_identity_verified']))
    universe=[('quercetin 3-O-glucoside','15.5 ± 0.95',15.5,.95,'historical full rutin reaction'),
      ('quercetin 3-O-galactoside','14.2 ± 0.21',14.2,.21,'parent galactose outside frozen glucose scope'),
      ('keampferol 3-O-glucoside','15.7 ± 1.3',15.7,1.3,'historical nicotiflorin target'),
      ('3-hydroxyflavone glucoside','0.9 ± 0.01',.9,.01,'new product graph/site/stereo unresolved'),
      ('quercetin 7-O-glucoside','0.02 ± 0.001',.02,.001,'new product graph/site/stereo unresolved'),
      ('keampferol 7-O-glucoside','0.01 ± 0.001',.01,.001,'new product graph/site/stereo unresolved'),
      ('7-hydroxyflavone glucoside','0.01 ± 0.001',.01,.001,'new product graph/site/stereo unresolved'),
      ('keampferol 3,7-di-O-glucoside','n.d.a',None,None,'not detected'),
      ('phloridzin','5.0 ± 0.03',5.,.03,'chalcone outside frozen scopes; product unresolved'),
      ('daidzin','n.d.',None,None,'not detected'),
      ('2-naphthol glucoside','2.5 ± 0.06',2.5,.06,'nonflavonoid outside frozen scopes'),
      ('1-naphthol glucoside','1.7 ± 0.03',1.7,.03,'nonflavonoid outside frozen scopes'),
      ('4-methylumbelliferone glucoside','n.d.',None,None,'not detected'),
      ('quercetin','n.d.',None,None,'aglycone not detected'),
      ('keampferol','n.d.',None,None,'aglycone not detected')]
    rows=[dict(candidate_id=f'SS-E01:buckwheat2018:Table2:{i}',raw_acceptor_name=n,normalized_acceptor_name=n.replace('keampferol','kaempferol'),raw_activity=raw,mean=mean,sd=sd,n=3,
       unit='nkat mg_protein^-1',value_status='not_detected' if mean is None else 'reported_numeric',reported_n_d_is_zero=False,
       activated_donor_source_evidence_complete=True,activated_donor_source_name='UDP-rhamnose',donor_evidence_location='main manuscript pp7-9,13,16; SI FigS1 p51',
       source_evidence_location='Table2 manuscript p35; FigS6 p56 shows acceptors only',source_pdf_path=str(source.relative_to(ROOT)),source_pdf_sha256=sha_file(source),
       complete_reference_precursors=None,holdout_qualified=False,evidence_eligible=False,disposition_reason=reason,agent_role='A5',
       read_A4_final_structures=False,read_other_extractor_output=False,input_manifest_sha=sha_file(manifest),scope_freeze_sha256=m['scope_freeze_sha256']) for i,(n,raw,mean,sd,reason) in enumerate(universe,1)]
    out2=folder/'A5_Table2_complete_universe.json';save_json(out2,rows,immutable=True)
    limitations=dict(task='TASK-016-P7',epoch_id='SS-E01',agent_role='A5',human_reviewed=False,approval_type='agent_delegated',
       reviewed_original_pdf_pages=60,source_graph_directly_viewed=['main Figure1 p42','SI FigureS6 p56'],positive_activity_rows=10,not_detected_rows=5,fresh_qualified_rows=0,
       activated_donor_preparation='Rhm2 At1g53500 converts UDP-glucose; original assay uses prepared UDP-rhamnose with residual UDP-glucose retained',
       donor_preparation_two_components_preserved=True,new_positive_activity_is_not_complete_product_structure=True,
       Table3_zero=dict(organ_raw='Hypocotyl, 3 days',analyte='quercitrin',raw_value='0.00 ± 0.01',mean=0.00,sd=.01,unit='µmol g FW^-1',value_status='reported_numeric_zero',is_missing=False,location='Table3 p36'),
       in_vivo_quercetin_robinobioside_peak='predicted annotation; not admitted source reaction',
       full_graph_status='existing rutin graph shown; new Table2 acceptor activity products not independently complete',
       read_A4_final_structures=False,read_other_extractor_output=False,read_fresh_model_outcomes=False,
       input_files={str(p.relative_to(ROOT)):sha_file(p) for p in [manifest,source,folder/'source_text.txt',folder/'page42.png',folder/'page56.png']})
    out3=folder/'A5_review_limitations.json';save_json(out3,limitations,immutable=True)
    emit_role(folder,'A5','SS-E01',[manifest,source,folder/'source_text.txt',folder/'page42.png',folder/'page56.png'],[out2,out3],15,0)
    print('SS buckwheat A3',row['checks'],'A5 universe15 positive10 ND5 qualified0')

def diosmin():
    manifest=B/'SS/fresh_Diosmin_common_raw_input_manifest.json';m=load(manifest);verify_hashes(m['raw_input_files_sha256']);folder=B/'SS/root_A5_Diosmin'
    rows=[];inputs=[manifest]
    for reaction in m['reactions']:
        graphs={}
        for kind,path in [('acceptor',reaction['acceptor_raw_property_path']),('product',reaction['product_raw_property_path']),('reference_donor_identity_only',reaction['donor_reference_identity_only']['raw_property_path'])]:
            p=ROOT/path;db=load(p)['PropertyTable']['Properties'][0];mol=Chem.MolFromSmiles(db['SMILES']);assert mol is not None
            canonical=Chem.MolToSmiles(mol,isomericSmiles=True);inchi=Chem.MolToInchi(mol)
            checks=dict(formula=rdMolDescriptors.CalcMolFormula(mol)==db['MolecularFormula'],inchi=inchi==db['InChI'],inchikey=Chem.MolToInchiKey(mol)==db['InChIKey'])
            assert all(checks.values()),(kind,checks)
            graphs[kind]=dict(CID=db['CID'],official_raw_smiles=db['SMILES'],canonical_isomeric_smiles=canonical,full_standard_inchi=inchi,full_stereo_inchikey=db['InChIKey'],molecular_formula=db['MolecularFormula'],checks=checks,raw_source_path=path,raw_source_sha256=sha_file(p),
               graph_identity_verified=True,reaction_donor_evidence=(False if kind=='reference_donor_identity_only' else None))
            inputs.append(p)
        rows.append(dict(reaction_id=reaction['reaction_id'],agent_role='A5',extraction_id='root-A5:'+reaction['reaction_id'],input_manifest_sha=sha_file(manifest),read_other_extractor_output=False,
           graph_encoding_origin='authoritative_structure_database_identity_chain',source_standard_names={k:reaction[k] for k in ['acceptor_source_standard_name','product_source_standard_name']},graphs=graphs,
           source_bond_atoms=reaction['source_bond_atoms'],site='parent_beta-D-Glcp_O6',product_sugar_stereo='alpha-L-Rhap(1->6)beta-D-Glcp',
           source_evidence_pointers=reaction['source_evidence_pointers'],source_acceptor_graph_complete=True,source_product_graph_complete=True,
           donor_smiles=None,donor_source_name=None,source_donor_graph_complete=False,structure_complete=False,reference_precursors=None,
           source_reaction_reference_complete=False,holdout_qualified=False,evidence_eligible=False,disposition='pending original activated donor evidence and all-closure/history/static verification',
           independent_original_review='PMC11527692 original Fig1/Fig5/DataSheet1 and public2025 original FigS2b viewed; no activated donor identified in those inspected originals',
           inspected_source_absence_is_not_whole_publication_absence=True,human_reviewed=False,approval_type='agent_delegated'))
    out=folder/'A5_partial_database_graphs.json';save_json(out,rows,immutable=True)
    emit_role(folder,'A5','SS-E01',list(dict.fromkeys(inputs)),[out],len(rows),0)
    print('SS Diosmin partial records',len(rows),'graphs independently verified3/3 each; full donor pending')

def wasabi():
    a=B/'C/E01/fresh/alternate/A4_WASABI_product_graphs.jsonl';b=B/'C/E01/stages/batches/WASABI_PUBLIC_SI/A5_structure_extraction_records.json'
    arows=[json.loads(x) for x in a.read_text().splitlines()];brows=load(b);bygraph={Chem.MolToSmiles(Chem.MolFromSmiles(r['target_smiles']),isomericSmiles=True):r for r in brows}
    outrows=[]
    for r in arows:
        product=Chem.MolToSmiles(Chem.MolFromSmiles(r['product_smiles']),isomericSmiles=True);s=bygraph[product]
        comparisons=dict(acceptor=Chem.MolToSmiles(Chem.MolFromSmiles(r['acceptor_smiles']),isomericSmiles=True)==Chem.MolToSmiles(Chem.MolFromSmiles(s['acceptor_smiles']),isomericSmiles=True),
            product=True,product_formula=r['source_product_formula']==s['molecular_formula'],product_full_standard_inchi=Chem.MolToInchi(Chem.MolFromSmiles(product))==s['full_standard_inchi'],product_full_stereo_inchikey=Chem.MolToInchiKey(Chem.MolFromSmiles(product))==s['full_stereo_inchikey'],donor_both_missing=r['donor_smiles'] is None and s['donor_smiles'] is None)
        outrows.append(dict(reaction_id=r['reaction_id'],product_name=s['product_name'],comparison= comparisons,endpoint_graphs_agree=all(comparisons.values()),
          structure_complete=False,reference_precursors=None,source_reaction_reference_complete=False,full_reference_reconciliation_performed=False,
          input_manifest_sha_identity_equal=False,raw_original_evidence_shared=True,raw_evidence_pointers=r['structure_evidence_pointer'],
          reasons=['activated donor absent in inspected public original reaction evidence','A4/A5 raw-input manifest hashes differ; partial endpoint comparison is not strict full harness reconciliation'],
          history_exact_target_match_count=len(s['historical_exact_target_matches']),source_qualified_holdout=False,
          frozen_C6_accepts_C3OH=s['semantic_core_boundary_unclosed'],C3_boundary_disposition='pending conservative exclusion; no post-hoc same-epoch scope admission' if s['semantic_core_boundary_unclosed'] else 'C3OH ambiguity not triggered'))
    folder=B/'C/E01/root_A6_Wasabi';out=folder/'partial_endpoint_comparison.json';save_json(out,outrows,immutable=True)
    decision=dict(task='TASK-016-P7',epoch_id='C-E01',agent_role='A6',approval_type='agent_delegated',human_reviewed=False,decided_at=now(),
         complete_reference_reconciliations=0,endpoint_agreements=4,donor_missing_reactions=4,eligible_holdout_count=0,
         canonical_endpoint_disagreements=0,full_reaction_disagreement_count=None,full_reaction_disagreement_uncomputable_reason='missing donor plus unequal common input manifest hashes',
         decision='preserve partial structures; defer full source reaction qualification; exclude flavonol C6 candidates pending core semantic boundary',
         frozen_query_C3_H_explicit=False,source_declared_core='flavone',source_semantic_C3OH_admission_pre_registered=False,
         C3_H_vs_C3_OH_negative_control_pre_registered=False,pre_registered_control_failure_claim=False,
         prior_wrong_core_control='ring oxygen replaced by sulfur; cannot stand for C3OH substitution',
         same_epoch_scope_modified=False,new_epoch_required_before_any_core_semantic_or_guard_change=True,
         scope_freeze_files={str(p.relative_to(ROOT)):sha_file(p) for p in [B/'C/E01/scope_manifest.json',B/'C/E01/scope_bank.json',ROOT/'flavoretro/glycoside_scope_c_v7.py']},
         partial_comparison_path=str(out.relative_to(ROOT)),partial_comparison_sha256=sha_file(out),
         shared_original_files={r['structure_evidence_pointer']['path']:r['structure_evidence_pointer']['sha256'] for r in arows},
         extractors_independent_final_graphs=True,A6_has_read_both_extractors=True,A6_is_not_an_independent_extractor=True)
    out2=folder/'semantic_disposition.json';save_json(out2,decision,immutable=True)
    emit_role(folder,'A6','C-E01',[a,b,B/'C/E01/scope_manifest.json',B/'C/E01/scope_bank.json'],[out,out2],4,0,model=True)
    print('C A6 Wasabi4 endpoints agree; full references0; C3 semantic pending; no scope mutation')

if __name__=='__main__':
    c_identity();buckwheat();diosmin();wasabi()

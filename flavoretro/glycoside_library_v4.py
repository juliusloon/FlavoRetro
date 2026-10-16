"""Opt-in v4 source-supported P3 scopes; activity stays unknown.

Chains the qualified P2/v2 v3 payload with the P3 build-only increment
(3 scoped templates).  Default behaviour, v1/v2/v3 namespaces and the
17-stock review view are unchanged; v4 loads only through the explicit
glycoside_library_version='v4' request path."""
import json,time
from pathlib import Path
from rdkit import Chem,rdBase
from rdkit.Chem import rdChemReactions,rdFMCS
from aizynthfinder.chem import TemplatedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
from . import glycoside_library as v2
from . import glycoside_library_v3 as v3
from .workspace import root,config,AssetError
from .resources import sha
from .reviewed_resources import canonical_side,reaction_signature,load_review
from .open_glycoside_library import normalize_species

def _c3_context_ok(acceptor_smi,target_smi):
    """Aliphatic C3 of a 2-hydroxyflavanone: conserved acceptor, single
    C-glycosidic link, site bonded to C4(=O) and C2(OH)(aryl)O."""
    acceptor,target=Chem.MolFromSmiles(acceptor_smi),Chem.MolFromSmiles(target_smi)
    if acceptor is None or target is None:return False
    mcs=rdFMCS.FindMCS([acceptor,target],timeout=5,ringMatchesRingOnly=True,completeRingsOnly=True,bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms!=acceptor.GetNumAtoms():return False
    query=Chem.MolFromSmarts(mcs.smartsString)
    conserved=target.GetSubstructMatch(query,useChirality=True)
    if not conserved or not target.HasSubstructMatch(acceptor,useChirality=True):return False
    inside=set(conserved);added=set(range(target.GetNumAtoms()))-inside
    links=[b for b in target.GetBonds() if (b.GetBeginAtomIdx() in inside)!=(b.GetEndAtomIdx() in inside)]
    if len(links)!=1 or not added:return False
    b=links[0]
    anomeric=b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx()
    site=b.GetOtherAtomIdx(anomeric)
    siteatom=target.GetAtomWithIdx(site)
    if siteatom.GetAtomicNum()!=6 or siteatom.GetIsAromatic():return False
    neighbours=[n for n in siteatom.GetNeighbors() if n.GetIdx()!=anomeric]
    if len(neighbours)!=2:return False
    has_carbonyl=any(n.GetAtomicNum()==6 and any(bb.GetBondType()==Chem.BondType.DOUBLE and bb.GetOtherAtom(n).GetAtomicNum()==8 for bb in n.GetBonds()) for n in neighbours)
    has_flavanone_ol=any(n.GetAtomicNum()==6 and any(x.GetAtomicNum()==8 and x.GetTotalNumHs()>=1 and x.GetFormalCharge()==0 and x.GetDegree()==1 for x in n.GetNeighbors()) and any(x.GetIsAromatic() for x in n.GetNeighbors()) and any(x.GetAtomicNum()==8 and x.IsInRing() for x in n.GetNeighbors()) for n in neighbours)
    return has_carbonyl and has_flavanone_ol

def _ss_context_ok(acceptor_smi,donor_smi,target_smi,mode):
    """Sugar-sugar O site: conserved acceptor, single link with the anomeric
    carbon on the transferred side; 'ring' accepts ring-carbon parents (1->2/
    3/4), 'exocyclic' accepts the glucose C6 CH2 (1->6)."""
    acceptor,donor,target=[Chem.MolFromSmiles(s) for s in (acceptor_smi,donor_smi,target_smi)]
    if any(m is None for m in (acceptor,donor,target)):return False
    mcs=rdFMCS.FindMCS([acceptor,target],timeout=5,ringMatchesRingOnly=True,completeRingsOnly=True,bondCompare=rdFMCS.BondCompare.CompareOrderExact)
    if mcs.canceled or mcs.numAtoms!=acceptor.GetNumAtoms():return False
    query=Chem.MolFromSmarts(mcs.smartsString)
    conserved=target.GetSubstructMatch(query,useChirality=True)
    if not conserved or not target.HasSubstructMatch(acceptor,useChirality=True):return False
    inside=set(conserved);added=set(range(target.GetNumAtoms()))-inside
    links=[b for b in target.GetBonds() if (b.GetBeginAtomIdx() in inside)!=(b.GetEndAtomIdx() in inside)]
    if len(links)!=1 or not added:return False
    b=links[0]
    anomeric=b.GetBeginAtomIdx() if b.GetBeginAtomIdx() in added else b.GetEndAtomIdx()
    site=b.GetOtherAtomIdx(anomeric)
    siteatom=target.GetAtomWithIdx(site)
    if siteatom.GetAtomicNum()!=8:return False
    others=[x for x in siteatom.GetNeighbors() if x.GetIdx()!=anomeric]
    if len(others)!=1:return False
    other=others[0]
    if mode=='ring':
        if not (other.IsInRing() and other.GetAtomicNum()==6):return False
    else:
        if not (not other.IsInRing() and other.GetAtomicNum()==6 and other.GetDegree()==2 and any(n.IsInRing() and n.GetAtomicNum()==6 for n in other.GetNeighbors())):return False
    frag_map={}
    glycan=Chem.PathToSubmol(target,[bb.GetIdx() for bb in target.GetBonds() if bb.GetBeginAtomIdx() in added and bb.GetEndAtomIdx() in added],atomMap=frag_map)
    glycan.GetAtomWithIdx(frag_map[anomeric]).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    return donor.HasSubstructMatch(glycan,useChirality=True)

def p3_scope_center_allowed(t,target,products):
    scope=t['scope'];center=scope['center_class']
    acceptor,donor=products
    if canonical_side([Chem.MolToSmiles(donor,isomericSmiles=True)])!=t['donor']:return False
    if not any(target.HasSubstructMatch(Chem.MolFromSmarts(c)) for c in scope['acceptor_cores']):return False
    for pat in scope['parent_glycan_patterns']:
        if not acceptor.HasSubstructMatch(Chem.MolFromSmarts(pat),useChirality=True):return False
    ts=Chem.MolToSmiles(target,isomericSmiles=True)
    acs=Chem.MolToSmiles(acceptor,isomericSmiles=True)
    ds=Chem.MolToSmiles(donor,isomericSmiles=True)
    if center=='C_hydroxyflavanone_C3':return _c3_context_ok(acs,ts)
    if center=='rhamnoside_glucoside_O2':return _ss_context_ok(acs,ds,ts,'ring')
    if center=='rhamnoside_glucoside_O6':return _ss_context_ok(acs,ds,ts,'exocyclic')
    return False

def scope_center_allowed(t,target,products):
    scope=t.get('scope')
    if scope and scope.get('namespace')=='task016_p3':return p3_scope_center_allowed(t,target,products)
    return v2.scope_center_allowed(t,target,products)

def apply_template(t,target,context=None):
    if context is not None and context!=t['required_context']:return []
    normalized=normalize_species(target)['normalized']
    if t['template_role']=='exact_instance_template' and normalized not in t['allowed_targets']:return []
    mol=Chem.MolFromSmiles(normalized);rxn=rdChemReactions.ReactionFromSmarts(t['smarts']);rxn.GetSubstructParams().useChirality=True
    outcomes=[]
    for index,products in enumerate(rxn.RunReactants([mol])):
        try:
            for p in products:Chem.SanitizeMol(p)
            v2.restore_conserved_double_bond_stereo(products,mol)
            if not scope_center_allowed(t,mol,products):continue
            value=canonical_side([Chem.MolToSmiles(p,isomericSmiles=True) for p in products])
            if value:outcomes.append(dict(outcome_index=index,precursors=value))
        except (ValueError,RuntimeError):continue
    return outcomes

class LibraryRetroReaction(TemplatedRetroReaction):
    def _apply_with_rdkit(self):
        from aizynthfinder.chem import TreeMolecule
        from functools import partial
        rxn=rdChemReactions.ReactionFromSmarts(self.smarts);rxn.GetSubstructParams().useChirality=True
        normalized=v2.neutral_mol(self.mol.mapped_mol)
        for atom in normalized.GetAtoms():atom.SetAtomMapNum(0)
        t=self.metadata['library_template']
        outcomes=[];raw_indices=[]
        for raw_index,products in enumerate(rxn.RunReactants([normalized])):
            try:
                for p in products:Chem.SanitizeMol(p)
                v2.restore_conserved_double_bond_stereo(products,normalized)
                if not scope_center_allowed(t,normalized,products):continue
                fn=partial(self._inherit_atom_mapping,exclude_nums=set(self.mol.mapping_to_index.keys()))
                value=tuple(TreeMolecule(parent=self.mol,rd_mol=p,sanitize=True,mapping_update_callback=fn) for p in products)
                outcomes.append(value);raw_indices.append(raw_index)
            except (ValueError,RuntimeError):continue
        self.metadata['raw_outcome_indices']=raw_indices
        self._reactants=tuple(outcomes);return self._reactants

class Registry(v3.Registry):
    """Validates the P3 increment and chains the qualified v3 payload."""
    def __init__(self,path,expected):
        path=Path(path)
        if not path.is_file() or sha(path)!=expected:raise AssetError('v4 manifest absent or hash drift')
        m=json.loads(path.read_text())
        if m.get('schema_version')!=2 or m['rdkit']!=rdBase.rdkitVersion:raise AssetError('v4 schema or environment drift')
        for rel,h in m['files_sha256'].items():
            p=(path.parent/rel).resolve()
            if not p.is_relative_to(path.parent.resolve()) or not p.is_file() or sha(p)!=h:raise AssetError('v4 build payload drift: '+rel)
        load_review(m['review_binding']);self.settings=m['policy']
        self.p3_templates=[json.loads(l) for l in (path.parent/'templates.jsonl').read_text().splitlines()]
        self.p3_instances={r['instance_id']:r for r in [json.loads(l) for l in (path.parent/'runtime_instances.jsonl').read_text().splitlines()]}
        if any(r.get('template_role')!='development_build' for r in self.p3_instances.values()):raise AssetError('holdout instance in runtime registry')
        self.v3_registry=v3.load_registry()
        self.templates=self.v3_registry.templates+self.p3_templates
        self.instances={**self.v3_registry.instances,**self.p3_instances}
        self.by_id={t['template_id']:t for t in self.templates}
        if len(self.by_id)!=len(self.templates):raise AssetError('duplicate v4 template ID')
        self.binding=dict(version=m['version'],manifest=str(path.relative_to(root())),manifest_sha256=expected,chained_v3=self.v3_registry.binding)
        for t in self.p3_templates:
            if t['validation_status']!='source_reconstruction_passed':raise AssetError('unvalidated v4 template')
            for identifier in t['support_instances']:
                r=self.p3_instances[identifier]
                if canonical_side(r['reference_precursors']) not in [o['precursors'] for o in apply_template(t,r['target'])]:raise AssetError('v4 support replay drift')
    def evidence(self,reaction):
        t=self.by_id.get(reaction.metadata.get('template_id'))
        if t is None or reaction.metadata.get('domain_binding')!=self.binding or reaction.smarts!=t['smarts'] or reaction.metadata.get('required_context')!=t['required_context']:raise RejectionException('v4 provenance invalid')
        actual=canonical_side([m.smiles for m in reaction.reactants[reaction.index]])
        if actual not in [o['precursors'] for o in apply_template(t,reaction.mol.smiles)]:raise RejectionException('v4 outcome outside validated scope')
        normalized=normalize_species(reaction.mol.smiles)['normalized'];sig=reaction_signature([actual],[normalized])
        matches=[self.instances[i] for i in t['support_instances'] if self.instances[i]['reference_signature']==sig]
        ns='task016_p3' if (t.get('scope') or {}).get('namespace')=='task016_p3' else 'task016_p2'
        return dict(namespace=ns,binding=self.binding,template_id=t['template_id'],template_source_support=True,source_instance_ids=t['support_instances'],exact_seed_instance_match=bool(matches),exact_instance_match=bool(matches),prediction_conditions_verified=False,yield_value=None,actionable=False,evidence_closed=False,independent_chemical_validation=False,human_reviewed=False,scope_applicability=t.get('scope',{'mode':'exact_instance'}),transfer_status='exact_build_source_reconstruction' if matches else 'scope_transfer_candidate_unverified_activity',required_context=t['required_context'],provenance=[self.instances[i]['provenance'] for i in t['support_instances']],original_conditions_copied=False,inherited_template=ns=='task016_p2')

def load_registry(expected=None):
    s=config('glycoside-library-v4.json');r=Registry(root()/s['manifest'],s['manifest_sha256'])
    if expected is not None and r.binding!=expected:raise AssetError('v4 binding changed during run')
    return r

class GlycosideExpansion(ExpansionStrategy):
    def __init__(self,key,config,domain_binding=None,**kwargs):
        ExpansionStrategy.__init__(self,key,config,**kwargs);self.registry=load_registry(domain_binding);self.profiling=dict(template_attempts=0,generation_seconds=0.,generated_actions=0)
    def get_actions(self,molecules,cache_molecules=None):
        actions=[];priors=[];start=time.monotonic()
        for mol in molecules:
            count=0
            for t in self.registry.templates:
                self.profiling['template_attempts']+=1
                if not apply_template(t,mol.smiles):continue
                if count>=self.registry.settings['domain_cap_per_molecule']:break
                a=LibraryRetroReaction(mol,smarts=t['smarts'],use_rdchiral=False,metadata=dict(policy_name=self.key,template_id=t['template_id'],template=t['smarts'],library_template=t,domain_binding=self.registry.binding,required_context=t['required_context']))
                if not a.reactants:continue
                for index in range(len(a.reactants)):self.registry.evidence(a.copy(index=index))
                actions.append(a);priors.append(self.registry.settings['prior']);count+=1
        self.profiling['generation_seconds']+=time.monotonic()-start;self.profiling['generated_actions']+=len(actions);return actions,priors

class DomainAwareQuickFilter(QuickKerasFilter):
    def __init__(self,key,config,domain_binding=None,**kwargs):
        QuickKerasFilter.__init__(self,key,config,**kwargs);self.registry=load_registry(domain_binding)
    def apply(self,reaction):
        if reaction.metadata.get('policy_name')=='glycoside':
            e=self.registry.evidence(reaction);reaction.metadata['task016_evidence']=e;reaction.metadata['filter_path']='known_hazards + validated v4 scope guard; activity unverified';reaction.metadata.setdefault('review',{})['task016_p3']=e;return
        QuickKerasFilter.apply(self,reaction)

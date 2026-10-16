"""Opt-in v2 glycoside templates with build-only support and bounded scope transfer."""
import json,time
from pathlib import Path
from rdkit import Chem,rdBase
from rdkit.Chem import rdChemReactions
from aizynthfinder.chem import TemplatedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
from .workspace import root,config,AssetError
from .resources import sha
from .reviewed_resources import canonical_side,reaction_signature,load_review
from .open_glycoside_library import normalize_species,structural_formation
FLAVONE='O=c1cc(-c2ccccc2)oc2ccccc12'

def neutral_mol(mol):
    result=Chem.Mol(mol)
    for atom in result.GetAtoms():
        if atom.GetAtomicNum()==8 and atom.GetFormalCharge()==-1 and atom.GetDegree()==1:
            n=atom.GetNeighbors()[0]
            acidic=n.GetAtomicNum()==15 or n.GetIsAromatic() or (n.GetAtomicNum()==6 and any(b.GetBondType()==Chem.BondType.DOUBLE and b.GetOtherAtom(n).GetAtomicNum()==8 for b in n.GetBonds()))
            if acidic and atom.GetBonds()[0].GetBondType()==Chem.BondType.SINGLE:
                atom.SetFormalCharge(0);atom.SetNumExplicitHs(1);atom.SetNoImplicit(True)
    Chem.SanitizeMol(result)
    Chem.AssignStereochemistry(result,cleanIt=True,force=True)
    return result

def restore_conserved_double_bond_stereo(products, parent):
    for product in products:
        by_parent={int(a.GetProp('react_atom_idx')):a.GetIdx() for a in product.GetAtoms() if a.HasProp('react_atom_idx')}
        for bond in parent.GetBonds():
            if bond.GetStereo()==Chem.BondStereo.STEREONONE:continue
            i,j=bond.GetBeginAtomIdx(),bond.GetEndAtomIdx();neighbors=list(bond.GetStereoAtoms())
            if i not in by_parent or j not in by_parent or len(neighbors)!=2 or any(k not in by_parent for k in neighbors):continue
            child=product.GetBondBetweenAtoms(by_parent[i],by_parent[j])
            if child is None or child.GetBondType()!=bond.GetBondType():continue
            if child.GetBeginAtomIdx()!=by_parent[i]:neighbors.reverse()
            child.SetStereoAtoms(*(by_parent[k] for k in neighbors));child.SetStereo(bond.GetStereo())
        Chem.SetDoubleBondNeighborDirections(product)

def scope_center_allowed(t,target,products):
    scope=t.get('scope')
    if not scope:return True
    acceptor,donor=products
    # Exact donor and nonanomeric stereo are immutable; local SMARTS cannot relax these.
    if canonical_side([Chem.MolToSmiles(donor,isomericSmiles=True)])!=t['donor']:return False
    try:formation=structural_formation(Chem.MolToSmiles(acceptor,isomericSmiles=True),t['donor'],Chem.MolToSmiles(target,isomericSmiles=True))
    except ValueError:return False
    if formation['family']!=t['category']:return False
    if scope['center_class']=='glucoside_O2':
        # Full beta-D-glucosyl context is in the reaction SMARTS; target must retain
        # at least one source-supported flavonoid structural family (not named targets).
        return any(target.HasSubstructMatch(Chem.MolFromSmarts(s)) for s in scope['acceptor_cores'])
    q=Chem.MolFromSmarts('O=[c:4]1[c:3][c:2](-[c:101]2[c:102][c:103][c:104][c:105][c:106]2)[o:1][c:109]2[c:8][c:7][c:6][c:5][c:110]12')
    matches=target.GetSubstructMatches(q,uniquify=False)
    if not matches:return False
    owner=next(a for a in target.GetAtomWithIdx(formation['product_atom_indices']['acceptor_site']).GetNeighbors() if a.GetIdx()!=formation['product_atom_indices']['anomeric'])
    q3=next(a.GetIdx() for a in q.GetAtoms() if a.GetAtomMapNum()==3)
    if not any(owner.GetIdx() in match and ((owner.GetIdx()==match[q3])==(scope['center_class']=='flavonol_O3')) for match in matches):return False
    # Supported finite decoration classes only: OH, OMe and one transferred glycan.
    center=formation['product_atom_indices'];allowed=set(center['added'])|set(matches[0]);allowed.add(center['acceptor_site'])
    decoration_atoms=set()
    for atom in target.GetAtoms():
        if atom.GetIdx() in allowed:continue
        if atom.GetAtomicNum()!=8:continue
        neighbors=list(atom.GetNeighbors())
        if atom.GetFormalCharge()!=0 or any(b.GetBondType()!=Chem.BondType.SINGLE for b in atom.GetBonds()):continue
        core_neighbors=[a for a in neighbors if a.GetIdx() in set(matches[0]) and a.GetIsAromatic() and a.GetAtomicNum()==6]
        if len(core_neighbors)!=1:continue
        if len(neighbors)==1 and atom.GetTotalNumHs()==1:
            decoration_atoms.add(atom.GetIdx())
        elif len(neighbors)==2:
            methyl=next(a for a in neighbors if a.GetIdx()!=core_neighbors[0].GetIdx())
            if methyl.GetAtomicNum()==6 and not methyl.GetIsAromatic() and methyl.GetDegree()==1 and methyl.GetTotalNumHs()==3 and methyl.GetFormalCharge()==0:
                decoration_atoms.update([atom.GetIdx(),methyl.GetIdx()])
    if any(a.GetIdx() not in allowed|decoration_atoms for a in target.GetAtoms()):return False
    return True

def apply_template(t,target,context=None):
    if context is not None and context!=t['required_context']:return []
    normalized=normalize_species(target)['normalized']
    if t['template_role']=='exact_instance_template' and normalized not in t['allowed_targets']:return []
    mol=Chem.MolFromSmiles(normalized);rxn=rdChemReactions.ReactionFromSmarts(t['smarts']);rxn.GetSubstructParams().useChirality=True
    outcomes=[]
    for index,products in enumerate(rxn.RunReactants([mol])):
        try:
            for p in products:Chem.SanitizeMol(p)
            restore_conserved_double_bond_stereo(products,mol)
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
        normalized=neutral_mol(self.mol.mapped_mol)
        # Keep atom indices for inherited mappings and conserved E/Z restoration.
        for atom in normalized.GetAtoms():atom.SetAtomMapNum(0)
        t=self.metadata['library_template']
        outcomes=[];raw_indices=[]
        for raw_index,products in enumerate(rxn.RunReactants([normalized])):
            try:
                for p in products:Chem.SanitizeMol(p)
                restore_conserved_double_bond_stereo(products,normalized)
                if not scope_center_allowed(t,normalized,products):continue
                fn=partial(self._inherit_atom_mapping,exclude_nums=set(self.mol.mapping_to_index.keys()))
                value=tuple(TreeMolecule(parent=self.mol,rd_mol=p,sanitize=True,mapping_update_callback=fn) for p in products)
                outcomes.append(value);raw_indices.append(raw_index)
            except (ValueError,RuntimeError):continue
        self.metadata['raw_outcome_indices']=raw_indices
        self._reactants=tuple(outcomes);return self._reactants

class Registry:
    def __init__(self,path,expected):
        path=Path(path)
        if not path.is_file() or sha(path)!=expected:raise AssetError('v2 manifest absent or hash drift')
        m=json.loads(path.read_text())
        if m.get('schema_version')!=2 or m['rdkit']!=rdBase.rdkitVersion:raise AssetError('v2 schema or environment drift')
        for rel,h in m['files_sha256'].items():
            p=(path.parent/rel).resolve()
            if not p.is_relative_to(path.parent.resolve()) or not p.is_file() or sha(p)!=h:raise AssetError('v2 build payload drift: '+rel)
        for rel,h in m['raw_dependencies_sha256'].items():
            p=(root()/rel).resolve()
            if not p.is_relative_to(root()) or not p.is_file() or sha(p)!=h:raise AssetError('v2 build source drift: '+rel)
        load_review(m['review_binding']);self.settings=m['policy']
        self.templates=[json.loads(l) for l in (path.parent/'templates.jsonl').read_text().splitlines()]
        self.instances={r['instance_id']:r for r in [json.loads(l) for l in (path.parent/'runtime_instances.jsonl').read_text().splitlines()]}
        if any(r['template_role']!='development_build' for r in self.instances.values()):raise AssetError('holdout instance in runtime registry')
        self.by_id={t['template_id']:t for t in self.templates}
        self.binding=dict(version=m['version'],manifest=str(path.relative_to(root())),manifest_sha256=expected)
        if len(self.by_id)!=len(self.templates):raise AssetError('duplicate v2 template ID')
        for t in self.templates:
            if t['validation_status']!='source_reconstruction_passed':raise AssetError('unvalidated v2 template')
            for identifier in t['support_instances']:
                r=self.instances[identifier]
                if canonical_side(r['reference_precursors']) not in [o['precursors'] for o in apply_template(t,r['target'])]:raise AssetError('v2 support replay drift')
    def evidence(self,reaction):
        t=self.by_id.get(reaction.metadata.get('template_id'))
        if t is None or reaction.metadata.get('domain_binding')!=self.binding or reaction.smarts!=t['smarts'] or reaction.metadata.get('required_context')!=t['required_context']:raise RejectionException('v2 provenance invalid')
        actual=canonical_side([m.smiles for m in reaction.reactants[reaction.index]])
        if actual not in [o['precursors'] for o in apply_template(t,reaction.mol.smiles)]:raise RejectionException('v2 outcome outside validated scope')
        normalized=normalize_species(reaction.mol.smiles)['normalized'];sig=reaction_signature([actual],[normalized])
        matches=[self.instances[i] for i in t['support_instances'] if self.instances[i]['reference_signature']==sig]
        return dict(namespace='task016_p1',binding=self.binding,template_id=t['template_id'],template_source_support=True,source_instance_ids=t['support_instances'],exact_seed_instance_match=bool(matches),exact_instance_match=bool(matches),prediction_conditions_verified=False,yield_value=None,actionable=False,evidence_closed=False,independent_chemical_validation=False,human_reviewed=False,scope_applicability=t.get('scope',{'mode':'exact_instance'}),transfer_status='exact_build_source_reconstruction' if matches else 'scope_transfer_candidate_unverified_activity',required_context=t['required_context'],provenance=[self.instances[i]['provenance'] for i in t['support_instances']],original_conditions_copied=False)

def load_registry(expected=None):
    s=config('glycoside-library-v2.json');r=Registry(root()/s['manifest'],s['manifest_sha256'])
    if expected is not None and r.binding!=expected:raise AssetError('v2 binding changed during run')
    return r
class GlycosideExpansion(ExpansionStrategy):
    def __init__(self,key,config,domain_binding=None,**kwargs):
        super().__init__(key,config,**kwargs);self.registry=load_registry(domain_binding);self.profiling=dict(template_attempts=0,generation_seconds=0.,generated_actions=0)
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
    def __init__(self,key,config,domain_binding=None,**kwargs):super().__init__(key,config,**kwargs);self.registry=load_registry(domain_binding)
    def apply(self,reaction):
        if reaction.metadata.get('policy_name')=='glycoside':
            e=self.registry.evidence(reaction);reaction.metadata['task016_evidence']=e;reaction.metadata['filter_path']='known_hazards + validated v2 scope guard; activity unverified';reaction.metadata.setdefault('review',{})['task016_p1']=e;return
        super().apply(reaction)

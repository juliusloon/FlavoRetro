"""Generic flavanone ring-opening suggestion. No individual target-answer lookup."""
import hashlib,json,time
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from aizynthfinder.chem import SmilesBasedRetroReaction
from aizynthfinder.context.policy import ExpansionStrategy
from aizynthfinder.context.policy.filter_strategies import QuickKerasFilter
from aizynthfinder.utils.exceptions import RejectionException
RULE_ID='FF-OPEN-E-v1'
PRIOR=0.25
SUPPORT_DOIS=['10.1002/anie.202107182','10.3390/molecules27061781']
SMARTS='[O:1]=[C:2]1[CH2:3][C;H1:4](-[c:5]2[c:6][c:7][c:8][c:9][c:10]2)[O;X2:11][c:12]2[c:13][c:14][c:15][c:16][c:17]21'
QUERY=Chem.MolFromSmarts(SMARTS)
MAP={a.GetAtomMapNum():a.GetIdx() for a in QUERY.GetAtoms()}


def canonical(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('unparseable structure')
    for a in mol.GetAtoms():a.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol,isomericSmiles=True)


def connectivity(mol):
    value=Chem.Mol(mol);Chem.RemoveStereochemistry(value)
    for a in value.GetAtoms():a.SetAtomMapNum(0)
    return Chem.MolToSmiles(value,isomericSmiles=False)


def precursors(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None:raise ValueError('unparseable target')
    if len(Chem.GetMolFrags(mol))!=1 or any(a.GetFormalCharge() or a.GetIsotope() or a.GetNumRadicalElectrons() for a in mol.GetAtoms()):return []
    matches=mol.GetSubstructMatches(QUERY,uniquify=True)
    if len(matches)!=1:return []
    match=matches[0];index=lambda n:match[MAP[n]]
    carbonyl,alpha,beta,aryl,oxygen=(index(n) for n in [2,3,4,5,11])
    original_tags={a.GetIdx():a.GetChiralTag() for a in mol.GetAtoms()}
    product=Chem.RWMol(mol)
    for a in product.GetAtoms():a.SetAtomMapNum(0)
    product.RemoveBond(beta,oxygen)
    bond=product.GetBondBetweenAtoms(alpha,beta);bond.SetBondType(Chem.BondType.DOUBLE)
    for ix in [alpha,beta,oxygen]:
        a=product.GetAtomWithIdx(ix);a.SetNumExplicitHs(0);a.SetNoImplicit(False)
    product.GetAtomWithIdx(beta).SetChiralTag(Chem.ChiralType.CHI_UNSPECIFIED)
    candidate=product.GetMol();Chem.SanitizeMol(candidate);Chem.AssignStereochemistry(candidate,cleanIt=True,force=True)
    double=candidate.GetBondBetweenAtoms(alpha,beta)
    double.SetStereoAtoms(carbonyl,aryl) if double.GetBeginAtomIdx()==alpha else double.SetStereoAtoms(aryl,carbonyl)
    double.SetStereo(Chem.BondStereo.STEREOE);Chem.SetDoubleBondNeighborDirections(candidate)
    assert len(Chem.GetMolFrags(candidate))==1
    assert candidate.GetNumAtoms()==mol.GetNumAtoms()
    assert rdMolDescriptors.CalcMolFormula(candidate)==rdMolDescriptors.CalcMolFormula(mol)
    for ix,tag in original_tags.items():
        if ix!=beta:assert candidate.GetAtomWithIdx(ix).GetChiralTag()==tag
    # Reclosure checks connectivity only: C2 stereoselectivity is not predicted.
    back=Chem.RWMol(candidate);back.AddBond(beta,oxygen,Chem.BondType.SINGLE);b=back.GetBondBetweenAtoms(alpha,beta);b.SetBondType(Chem.BondType.SINGLE);b.SetStereo(Chem.BondStereo.STEREONONE)
    for b in back.GetBonds():b.SetBondDir(Chem.BondDir.NONE)
    rebuilt=back.GetMol();Chem.SanitizeMol(rebuilt)
    assert connectivity(rebuilt)==connectivity(mol)
    text=Chem.MolToSmiles(candidate,isomericSmiles=True)
    parsed=Chem.MolFromSmiles(text);assert parsed is not None
    doubles=[b for b in parsed.GetBonds() if b.GetBondType()==Chem.BondType.DOUBLE and b.GetStereo()==Chem.BondStereo.STEREOE]
    assert doubles
    return [text]


def evidence(reaction):
    if reaction.metadata.get('policy_name')!='flavanone_opening' or reaction.metadata.get('template_id')!=RULE_ID:raise RejectionException('wrong graph-rule identity')
    allowed=precursors(reaction.mol.smiles)
    actual=sorted(canonical(m.smiles) for m in reaction.reactants[reaction.index])
    if len(actual)!=1 or actual[0] not in allowed:raise RejectionException('outside exact recomputed graph-rule scope')
    return dict(rule_id=RULE_ID,source_record_type='general_source_class_graph_hypothesis',class_support_dois=SUPPORT_DOIS,exact_source_instance_match=False,scope_transfer_evidence=False,source_reconstruction=False,precursor_geometry_convention='E source-class candidate; no exclusivity claim',C2_stereoselectivity_predicted=False,enzyme_or_activity_predicted=False,conditions_prediction_verified=False,yield_predicted=False,human_reviewed=False,independent_chemical_validation=False,evidence_closed=False,actionable=False,boundary='New graph candidate; class source support does not prove this target transformation, enzyme activity, conditions, purity, safety or supply.')


class FlavanoneOpening(ExpansionStrategy):
    def __init__(self,key,config,**kwargs):
        self.binding = load_binding(kwargs.pop("scope_binding", None))
        super().__init__(key,config,**kwargs)
        if key!='flavanone_opening':raise ValueError('rule policy key must be explicit')
        self.profiling=dict(lookups=0,generated_actions=0,generation_seconds=0.0)
    def get_actions(self,molecules,cache_molecules=None):
        started=time.monotonic();actions=[];priors=[]
        for mol in molecules:
            self.profiling['lookups']+=1
            for value in precursors(mol.smiles):
                metadata=dict(policy_name=self.key,template_id=RULE_ID,template_code=RULE_ID,classification='generic_flavanone_opening_E_candidate',source_record_type='general_source_class_graph_hypothesis')
                actions.append(SmilesBasedRetroReaction(mol,reactants_str=value,metadata=metadata));priors.append(PRIOR);self.profiling['generated_actions']+=1
        self.profiling['generation_seconds']+=time.monotonic()-started
        return actions,priors


class GraphRuleQuickFilter(QuickKerasFilter):
    def __init__(self,key,config,**kwargs):
        self.binding = load_binding(kwargs.pop("scope_binding", None))
        super().__init__(key,config,**kwargs)
    def apply(self,reaction):
        if reaction.metadata.get('policy_name')=='flavanone_opening':
            reaction.metadata['task022_scope_hypothesis']=evidence(reaction)
            reaction.metadata['filter_path']='KnownHazards and reviewed-evidence retained; exact graph-rule scope check instead of USPTO quick-model filter for added rule only; no forward chemistry certification'
            return
        return super().apply(reaction)

def load_binding(expected=None):
    """Bind code and class support, never consult per-target source answers."""
    from pathlib import Path
    from flavoretro.workspace import config, config_path, AssetError
    from flavoretro.resources import sha
    settings=config("flavanone-opening.json")
    if (settings.get("rule_id") != RULE_ID or settings.get("prior") != PRIOR
            or settings.get("class_support_dois") != SUPPORT_DOIS
            or settings.get("exact_target_registry") is not False
            or settings.get("independent_chemical_validation") is not False):
        raise AssetError("unsupported flavanone rule binding")
    code_sha=sha(Path(__file__))
    if settings.get("policy_sha256") != code_sha:
        raise AssetError("flavanone rule code drift")
    binding={**settings, "config_sha256": sha(config_path("flavanone-opening.json"))}
    if expected is not None and expected != binding:
        raise AssetError("flavanone binding changed during run")
    return binding

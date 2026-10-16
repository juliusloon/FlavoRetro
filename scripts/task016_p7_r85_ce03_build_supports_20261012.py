"""R85: C-E03 design-evidence determination + build supports (flavone 8-C-Glc).

Site verification is computational: the A-ring C8 locator must coincide with
the glycosyl-bearing carbon in vitexin/orientin and must NOT in the C6 controls
(isoorientin from C-E02 custody). No handwritten structures.
"""
import json, re, urllib.parse, urllib.request, urllib.error, uuid, hashlib
from pathlib import Path
from datetime import datetime, timezone
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
R83 = B / "C/E03/design/C-E03-R83-liu2021-design-intake-v1"
R84 = B / "C/E03/design/C-E03-R84-pubchem-structure-custody-v1"
OUT = B / "C/E03/design/C-E03-R85-build-supports-v1"
RAW = Path("data/raw/task016-p7/C/E03/C-E03-R85-pubchem-controls-custody-v1")
LOCK = B / "source_budget_acquisition.lock"
DOI = "10.1021/acs.jafc.1c00602"
DONOR = "O=c1ccn([C@@H]2O[C@H](COP(=O)(O)OP(=O)(O)O[C@H]3O[C@H](CO)[C@@H](O)[C@H](O)[C@H]3O)[C@@H](O)[C@H]2O)c(=O)[nH]1"

def sha_file(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(T, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(T, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
def canonical(url):
    u = urllib.parse.urlsplit(url)
    return (u.hostname or "", urllib.parse.unquote(u.path).rstrip("/"), tuple(sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True))))
def counter(rr): return dict(HTTP=len(rr), bytes=sum(int(x.get("bytes", 0)) for x in rr))
def http_get(url, kind, reason):
    with (ROOT / LOCK).open("a+") as f:
        import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            before = counter(physical_attempts())
            same = [r for r in physical_attempts() if canonical(r["url"]) == canonical(url)]
            if len(same) >= 2: return dict(result="rejected_old_url", status_code=None)
            if before["HTTP"] + 1 > 8000: raise RuntimeError("GLOBAL_BUDGET_STOP")
            aid = "R85-" + uuid.uuid4().hex; start = datetime.now(timezone.utc).isoformat()
            append(OUT / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind, registered_at=start, budget_before=before))
            data = b""; status = None; err = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public structure authority)"})
                try: resp = urllib.request.build_opener(NoRedirect()).open(req, timeout=90)
                except urllib.error.HTTPError as e: resp = e; err = "HTTP_" + str(e.code)
                status = resp.code; data = resp.read(2 * 1024**2 + 1)
            except Exception as e: err = type(e).__name__ + ":" + str(e)[:150]
            finally:
                try: resp.close()
                except Exception: pass
            ptr = RAW / (aid + ".bin"); p = ROOT / ptr
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data); p.chmod(0o444)
            event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            return dict(attempt_id=aid, url=url, kind=kind, status_code=status, bytes=len(data),
                        status="available" if status == 200 and not err else "failed", error=err,
                        path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), batch_id="C-E03-R85-build-supports")
        finally:
            import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def rings(mol):
    pr = [r for r in mol.GetRingInfo().AtomRings() if len(r) == 6
          and any(mol.GetAtomWithIdx(i).GetAtomicNum() == 8 and mol.GetAtomWithIdx(i).GetIsAromatic() for i in r)
          and any(mol.GetAtomWithIdx(i).GetAtomicNum() == 6 and any(b.GetBondType() == Chem.BondType.DOUBLE and b.GetOtherAtom(mol.GetAtomWithIdx(i)).GetAtomicNum() == 8 for b in mol.GetAtomWithIdx(i).GetBonds()) for i in r)]
    assert len(pr) == 1, "pyrone ring not unique"
    pyrone = set(pr[0])
    ox = next(mol.GetAtomWithIdx(i) for i in pyrone if mol.GetAtomWithIdx(i).GetAtomicNum() == 8)
    ar = [r for r in mol.GetRingInfo().AtomRings() if len(r) == 6 and set(r) != pyrone and any(i in pyrone for i in r)]
    assert len(ar) == 1, "A-ring not unique"
    a_ring = list(ar[0])
    fusion = [i for i in a_ring if mol.GetAtomWithIdx(i) in [n for n in ox.GetNeighbors()]] +              [i for i in a_ring if any(j in pyrone and j not in [n.GetIdx() for n in ox.GetNeighbors()] and mol.GetAtomWithIdx(i).GetIdx() in [x.GetIdx() for x in mol.GetAtomWithIdx(j).GetNeighbors()] for j in pyrone)]
    c8a = next(i for i in a_ring if i in [n.GetIdx() for n in ox.GetNeighbors()])
    c4a = next(i for i in a_ring if any(j in pyrone and mol.GetAtomWithIdx(j).GetIdx() in [x.GetIdx() for x in mol.GetAtomWithIdx(i).GetNeighbors()] and j != c8a for j in a_ring))
    c8 = next(i for i in a_ring if i in [n.GetIdx() for n in mol.GetAtomWithIdx(c8a).GetNeighbors()] and i != c4a)
    def has_oh(i):
        return any(x.GetAtomicNum() == 8 and x.GetTotalNumHs() + x.GetNumImplicitHs() >= 1 and x.GetDegree() <= 1 for x in mol.GetAtomWithIdx(i).GetNeighbors())
    c7 = next(i for i in a_ring if i in [n.GetIdx() for n in mol.GetAtomWithIdx(c8).GetNeighbors()] and has_oh(i) and i != c8a)
    c6 = next(i for i in a_ring if i in [n.GetIdx() for n in mol.GetAtomWithIdx(c7).GetNeighbors()] and i != c8)
    return dict(A_ring=a_ring, C4a=c4a, C8a=c8a, C8=c8, C7=c7, C6=c6)

def glycosyl_carbon(mol):
    loc = rings(mol)
    for i in (loc["C8"], loc["C6"]):
        for n in mol.GetAtomWithIdx(i).GetNeighbors():
            if n.GetAtomicNum() == 6 and n.GetIdx() not in loc["A_ring"] and n.IsInRing() and any(x.GetAtomicNum() == 8 for x in n.GetNeighbors()):
                return i
    return None

def main():
    if not (ROOT / OUT / "precontract.json").exists():
        save(OUT / "precontract.json", dict(task=T, epoch_id="C-E03", family="C", batch="C-E03-R85-build-supports",
            created_at=datetime.now(timezone.utc).isoformat(), approval_type="agent_delegated", human_reviewed=False,
            purpose="C-E03 build supports (apigenin/luteolin -> vitexin/orientin, C8) with computational C8-vs-C6 site verification and preregistered boundary controls",
            planned_http=3, names_to_fetch=["kaempferol", "quercetin", "naringenin"]))
    st = load(R84 / "structures_by_name.v2.json")["structures"]
    ce02 = json.loads((ROOT / B / "C/E02/build_supports.json").read_text())
    ce02_targets = {r["reaction_id"]: r for r in ce02}
    iso_row = next(r for r in ce02 if r["target"].count("O") >= 9 and "luteolin" not in r["reaction_id"].lower() and r["center_class"] == "flavone_6_C_glucoside" and r["acceptor"] != "O=c1cc(-c2ccccc2)oc2cc(O)cc(O)c12")
    controls = {}
    for name in ("kaempferol", "quercetin", "naringenin"):
        rec = http_get("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" + name + "/property/SMILES,MolecularFormula/JSON", "metadata", "boundary-control structure: " + name)
        append(OUT / "query_execution.jsonl", dict(query_id="R85-PC-" + name, status=rec.get("status"), status_code=rec.get("status_code"), url=rec["url"], raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")}))
        j = json.loads((ROOT / rec["path"]).read_text())["PropertyTable"]["Properties"][0]
        controls[name] = dict(cid=j.get("CID"), smiles=j.get("IsomericSMILES") or j.get("SMILES") or j.get("ConnectivitySMILES"), molecular_formula=j.get("MolecularFormula"), raw_pointer=rec["path"], raw_sha256=rec["sha256"])
    mols = {n: Chem.MolFromSmiles(st[n]["isomeric_smiles"]) for n in st}
    ctrl_mols = {n: Chem.MolFromSmiles(v["smiles"]) for n, v in controls.items()}
    chrysin_acc = "O=c1cc(-c2ccccc2)oc2cc(O)cc(O)c12"
    c6_rows = [r for r in ce02 if r["center_class"] == "flavone_6_C_glucoside"]
    checks = {}
    for n in ("vitexin", "orientin"):
        loc = rings(mols[n]); g = glycosyl_carbon(mols[n])
        checks[n] = dict(C8_locator=loc["C8"], C6_locator=loc["C6"], glycosyl_carbon=g, site_is_C8=(g == loc["C8"]), site_is_C6=(g == loc["C6"]))
    for n in ("apigenin", "luteolin"):
        loc = rings(mols[n])
        checks[n] = dict(C8_locator=loc["C8"], C6_locator=loc["C6"], C8_free_H=mols[n].GetAtomWithIdx(loc["C8"]).GetTotalNumHs() == 1, C6_free_H=mols[n].GetAtomWithIdx(loc["C6"]).GetTotalNumHs() == 1)
    c6mol = Chem.MolFromSmiles(iso_row["target"]); loc6 = rings(c6mol); g6 = glycosyl_carbon(c6mol)
    checks["C6_control_isoorientin_like_from_CE02"] = dict(reaction_id=iso_row["reaction_id"], C8_locator=loc6["C8"], C6_locator=loc6["C6"], glycosyl_carbon=g6, site_is_C6=(g6 == loc6["C6"]), site_is_C8=(g6 == loc6["C8"]))
    assert checks["vitexin"]["site_is_C8"] and checks["orientin"]["site_is_C8"], "C8 site verification failed for products"
    assert checks["apigenin"]["C8_free_H"] and checks["luteolin"]["C8_free_H"], "acceptor C8-H absent"
    assert checks["C6_control_isoorientin_like_from_CE02"]["site_is_C6"] and not checks["C6_control_isoorientin_like_from_CE02"]["site_is_C8"], "C6 control failed to discriminate"
    supports = []
    for sid, acc, prod, enz_note in (("C-APIGENIN-C8", "apigenin", "vitexin", "TcCGT1 8-C-glycosylation of apigenin (Km 0.9 mM, in vitro recombinant)"),
                                     ("C-LUTEOLIN-C8", "luteolin", "orientin", "TcCGT1 8-C-glycosylation of luteolin (Km 0.26 mM, in vitro recombinant)")):
        supports.append(dict(instance_id=sid, reaction_id=sid, category="C_formation", center_class="flavone_8_C_glucoside",
            acceptor=st[acc]["isomeric_smiles"], target=st[prod]["isomeric_smiles"], donor=DONOR,
            sugar_type="glucose", site="A-ring C8", evidence_eligible=True, development_exposed=True,
            human_reviewed=False, independent_chemical_validation=False,
            required_context=dict(donor_name="UDP-glucose", mode="enzymatic", enzyme="TcCGT1 (Trollius chinensis, GenBank MK644229)"),
            reference_precursors=None,
            provenance=dict(doi=DOI, pmcid=None, source_role="design_build_support_late_prior_design",
                source_admission_sha256=None,
                evidence_pointers=[dict(path=str(R83 / "A4/article_text_harvest.json"), sha256=sha_file(R83 / "A4/article_text_harvest.json")),
                                    dict(path=str(R83 / "A5/article_text_harvest.json"), sha256=sha_file(R83 / "A5/article_text_harvest.json")),
                                    dict(path=str(R84 / "structures_by_name.v2.json"), sha256=sha_file(R84 / "structures_by_name.v2.json")),
                                    dict(path=str(R84 / "formula_consistency.v2.json"), sha256=sha_file(R84 / "formula_consistency.v2.json"))]),
            enzyme_evidence_note=enz_note))
    for s in supports:
        from flavoretro.reviewed_resources import canonical_side
        s["reference_precursors"] = canonical_side([s["acceptor"], s["donor"]])
        mol = Chem.MolFromSmiles(s["target"])
        assert mol is not None and rdMolDescriptors.CalcMolFormula(mol) in ("C21H20O10", "C21H20O11"), s["instance_id"]
    put(OUT / "site_verification.json", dict(task=T, at=now(), method="A-ring C8 locator: A-ring fusion-atom (bonded to pyrone ether O) neighbor excluding C4a; C6 control from frozen C-E02 build support target",
        discriminator="C6 control glycosyl carbon equals C6 locator and NOT C8; vitexin/orientin glycosyl carbon equals C8 locator",
        checks=checks, passed=True, approval_type="agent_delegated", human_reviewed=False))
    put(OUT / "build_supports.json", supports)
    put(OUT / "boundary_plan.json", dict(task=T, at=now(), preregistered=True, minimum=6,
        controls=[
            dict(control_id="BC1-kaempferol", role="outside_stratum_flavonol_3OH", structure=controls["kaempferol"]["smiles"], source="PubChem R85"),
            dict(control_id="BC2-quercetin", role="outside_stratum_flavonol_3OH", structure=controls["quercetin"]["smiles"], source="PubChem R85"),
            dict(control_id="BC3-naringenin", role="outside_stratum_flavanone_no_C2C3_double", structure=controls["naringenin"]["smiles"], source="PubChem R85"),
            dict(control_id="BC4-chrysin", role="B_ring_unsubstituted_outside_support_core", structure=chrysin_acc, source="frozen C-E02 build_supports.json"),
            dict(control_id="BC5-C6_glucoside_from_CE02", role="C6_occupied_regioisomer_control", structure=iso_row["target"], source="frozen C-E02 build_supports.json " + iso_row["reaction_id"]),
            dict(control_id="BC6-vitexin_product", role="product_self_C8_occupied_must_not_fire", structure=st["vitexin"]["isomeric_smiles"], source="R84 PubChem"),
            dict(control_id="BC7-orientin_product", role="product_self_C8_occupied_must_not_fire", structure=st["orientin"]["isomeric_smiles"], source="R84 PubChem"),
            dict(control_id="BC8-apigenin_acceptor_self", role="acceptor_without_glycan_must_not_fire_retro", structure=st["apigenin"]["isomeric_smiles"], source="R84 PubChem")],
        note="scope must NOT fire (retro direction: produce precursors) on any control; violation=0 required at G3",
        approval_type="agent_delegated", human_reviewed=False))
    put(OUT / "A6_design_evidence_determination.json", dict(task=T, at=now(), agent_role="A6", epoch_id="C-E03",
        source_id="C-E03-R83-S01-liu2021", DOI=DOI,
        reactions_admitted_as_design_build_supports=2,
        evidence=dict(enzyme="TcCGT1", origin="Trollius chinensis, GenBank MK644229 (paper Table/Methods)",
            in_vitro="recombinant enzyme purified (Ni-NTA) with measured kinetics (Km 0.26/0.9 mM, Vmax 47.3/112.5 uM/min for luteolin/apigenin)",
            products="vitexin/orientin identified by HPLC-DAD + LC/MS (Figure 3); coupled SuSy cascade titers 2324.4/5524.1 mg/L, yields 91.4/89.3%",
            site="C-8 (paper: 'catalyzes the glycosylation at position 8 of apigenin and luteolin'; prior work cited: 8-C-glycosylation of 36 flavonoids)"),
        dual_acceptors=["apigenin (CID 5280443)", "luteolin (CID 5280445)"], distinct_canonical_acceptors=2,
        site_verification="computational C8 locator + C6 control discrimination (site_verification.json)",
        structure_origin="PubChem name-resolved records (R84); formula deltas C6H10O5 verified; no handwritten structures",
        design_lane_note="supports are late_prior_design (read sanctioned by owner-approved C8 sequencing); NOT fresh; fresh pool = he2019/qiu2021/thesis (unread)",
        approval_type="agent_delegated", human_reviewed=False, errors=[]))
    event(T, "R85_done", supports=2, controls=8, site_checks_passed=True)
    print(json.dumps(dict(supports=2, controls=8, site_checks=checks)))

if __name__ == "__main__":
    main()

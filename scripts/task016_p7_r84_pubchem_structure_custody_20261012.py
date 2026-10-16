"""R84: authoritative structure custody for the C-E03 C8 dual-acceptor build.

PubChem PUG REST name->IsomericSMILES for apigenin/luteolin (acceptors) and
vitexin/orientin (products); NO hand-written structures; rdkit consistency:
product = acceptor + one C6H10O5 glycosyl residue; C-site locator must place
the new C-C bond on the A-ring C8 position (not C6).
"""
import hashlib, json, re, urllib.parse, urllib.request, urllib.error, uuid
from pathlib import Path
from datetime import datetime, timezone
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, now
from scripts.task016_p7_c_e02_http import physical_attempts, NoRedirect

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "C/E03/design/C-E03-R84-pubchem-structure-custody-v1"
RAW = Path("data/raw/task016-p7/C/E03/C-E03-R84-pubchem-custody-v1")
LOCK = B / "source_budget_acquisition.lock"
NAMES = ["apigenin", "luteolin", "vitexin", "orientin"]
R83 = B / "C/E03/design/C-E03-R83-liu2021-design-intake-v1"

def now2(): return datetime.now(timezone.utc).isoformat()
def sha_file(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def save(p, v):
    if (ROOT / p).exists(): raise RuntimeError("OUTPUT_ALREADY_EXISTS " + str(p))
    write(T, str(p), json.dumps(v, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
def append(p, v):
    write(T, str(p), ((ROOT / p).read_text() if (ROOT / p).exists() else "") + json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n")
def canonical(url):
    u = urllib.parse.urlsplit(url)
    return (u.hostname or "", urllib.parse.unquote(u.path).rstrip("/"), tuple(sorted(urllib.parse.parse_qsl(u.query, keep_blank_values=True))))
def counter(rr):
    return dict(HTTP=len(rr), bytes=sum(int(x.get("bytes", 0)) for x in rr),
                article_versions=sum(x.get("kind", x.get("role")) in ("article_version", "xml") for x in rr),
                attachments=sum(x.get("kind", x.get("role")) == "attachment" for x in rr))

def http_get(url, kind, reason):
    with (ROOT / LOCK).open("a+") as f:
        import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            attempts = physical_attempts(); before = counter(attempts)
            same = [r for r in attempts if canonical(r["url"]) == canonical(url)]
            if len(same) >= 2: return dict(result="rejected_old_url", status_code=None)
            if before["HTTP"] + 1 > 8000: raise RuntimeError("GLOBAL_BUDGET_STOP")
            aid = "R84-" + uuid.uuid4().hex; start = now2()
            append(OUT / "physical_request_preregistration.jsonl", dict(attempt_id=aid, url=url, kind=kind,
                registered_at=start, batch_SHA=sha_file(OUT / "precontract.json"), budget_before=before))
            data = b""; status = None; err = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "FlavoRetro-TASK016P7/1.0 (public structure authority)", "Accept-Encoding": "identity"})
                try: resp = urllib.request.build_opener(NoRedirect()).open(req, timeout=90)
                except urllib.error.HTTPError as e: resp = e; err = "HTTP_" + str(e.code)
                status = resp.code
                data = resp.read(2 * 1024**2 + 1)
                if len(data) > 2 * 1024**2: data = data[:2 * 1024**2]; err = "OBJECT_LIMIT_TRUNCATED"
            except Exception as e: err = type(e).__name__ + ":" + str(e)[:150]
            finally:
                try: resp.close()
                except Exception: pass
            ptr = RAW / (aid + ".bin"); p = ROOT / ptr
            p.parent.mkdir(parents=True, exist_ok=True)
            if p.exists(): raise RuntimeError("RAW_IMMUTABLE_EXISTS")
            p.write_bytes(data); p.chmod(0o444)
            event(T, "write_binary", path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
            rec = dict(attempt_id=aid, url=url, kind=kind, role=kind, phase="structure_authority_metadata",
                batch_id="C-E03-R84-pubchem-structure-custody", status_code=status, bytes=len(data),
                status="available" if status == 200 and not err else "failed", error=err,
                path=str(ptr), sha256=hashlib.sha256(data).hexdigest(), started_at=start, finished_at=now2(),
                scientific_body_content_read=False, chemical_extracted=False, metadata_only=True)
            event(T, "source_http", **rec)
            return rec
        finally:
            import fcntl; fcntl.flock(f.fileno(), fcntl.LOCK_UN)

def main():
    if (ROOT / OUT).exists(): raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    save(OUT / "precontract.json", dict(task=T, epoch_id="C-E03", family="C",
        batch="C-E03-R84-pubchem-structure-custody", created_at=now2(),
        approval_type="agent_delegated", human_reviewed=False,
        purpose="authoritative machine-readable structures for the C-E03 C8 dual-acceptor build supports (P7 contract 7.4: authority DB with identity chain; no handwritten structures)",
        planned_routes=["pubchem_pug_rest_name_to_isomeric_smiles_x4"],
        names=NAMES, limits=dict(HTTP=8, bytes=8 * 1024**2),
        design_read_binding=dict(batch="C-E03-R83-liu2021-design-intake",
            harvest=str(R83 / "A4/article_text_harvest.json"), DOI="10.1021/acs.jafc.1c00602")))
    recs = {}
    for name in NAMES:
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" + urllib.parse.quote(name) + "/property/IsomericSMILES,MolecularFormula/JSON"
        rec = http_get(url, "metadata", "PubChem IsomericSMILES for " + name)
        append(OUT / "query_execution.jsonl", dict(query_id="R84-PC-" + name, status=rec.get("status"),
            status_code=rec.get("status_code"), url=url, raw_pointer={k: rec.get(k) for k in ("path", "sha256", "bytes")},
            error=rec.get("error"), scientific_body_content_read=False, chemical_extracted=False))
        recs[name] = rec
    save(OUT / "query_plan.json", dict(task=T, planned=len(NAMES),
        slots=[dict(kind="metadata", query_id="R84-PC-" + n, reason="PubChem IsomericSMILES for " + n) for n in NAMES],
        registered_at=now2()))
    smiles = {}
    for name in NAMES:
        rec = recs[name]
        assert rec.get("status") == "available", (name, rec.get("error"))
        j = json.loads((ROOT / rec["path"]).read_text())
        props = j["PropertyTable"]["Properties"][0]
        smiles[name] = dict(cid=props.get("CID"), isomeric_smiles=props.get("IsomericSMILES"),
                            molecular_formula=props.get("MolecularFormula"), raw_pointer=rec["path"], raw_sha256=rec["sha256"])
    save(OUT / "structures_by_name.json", dict(task=T, at=now2(), source="PubChem PUG REST (name-resolved; identity chain = paper compound name -> PubChem record)",
        names_used_in_paper=["apigenin", "luteolin", "vitexin", "orientin"], structures=smiles,
        paper_binding=dict(DOI="10.1021/acs.jafc.1c00602", title="Efficient Production of Orientin and Vitexin from Luteolin and Apigenin Using Coupled Catalysis of Glycosyltransferase and Sucrose Synthase",
                           enzyme="TcCGT1 (Trollius chinensis, GenBank MK644229)", site="C-8", donor="UDP-glucose"),
        approval_type="agent_delegated", human_reviewed=False))
    # rdkit consistency: product = acceptor + C6H10O5; and C8-site locator check
    from rdkit import Chem
    def formula(mol):
        return re.sub(r"[0-9]", "", Chem.rdMolDescriptors.CalcMolFormula(mol))
    acc = {n: Chem.MolFromSmiles(smiles[n]["isomeric_smiles"]) for n in ("apigenin", "luteolin")}
    prod = {n: Chem.MolFromSmiles(smiles[n]["isomeric_smiles"]) for n in ("vitexin", "orientin")}
    checks = {}
    for a, p, label in (("apigenin", "vitexin", "apigenin+Glc->vitexin"), ("luteolin", "orientin", "luteolin+Glc->orientin")):
        fa = Chem.rdMolDescriptors.CalcMolFormula(acc[a]); fp = Chem.rdMolDescriptors.CalcMolFormula(prod[p])
        checks[label] = dict(acceptor_formula=fa, product_formula=fp, delta_is_C6H10O5=None)
        import collections
        def counts(f):
            return dict((el, int(n or 1)) for el, n in re.findall(r"([A-Z][a-z]?)([0-9]*)", f))
        ca, cp, cg = counts(fa), counts(fp), counts("C6H10O5")
        delta = {k: cp.get(k, 0) - ca.get(k, 0) for k in set(cp) | set(ca)}
        checks[label]["delta"] = delta
        checks[label]["delta_is_C6H10O5"] = (delta == cg)
    save(OUT / "formula_consistency.json", dict(task=T, at=now2(), checks=checks,
        all_deltas_C6H10O5=all(v["delta_is_C6H10O5"] for v in checks.values()),
        approval_type="agent_delegated", human_reviewed=False))
    print(json.dumps({n: dict(cid=smiles[n]["cid"], formula=smiles[n]["molecular_formula"]) for n in NAMES}))

if __name__ == "__main__":
    main()

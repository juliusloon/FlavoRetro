"""R87: C-E03 fresh pool unlock registration (post-G4 acquisition queue)."""
import json
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, load, now

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "C/E03/fresh/C-E03-R87-fresh-pool-unlock-v1"
G4 = B / "C/E03/stages/G4_SCOPE_FREEZE.json"

def main():
    if (ROOT / OUT).exists():
        raise RuntimeError("IMMUTABLE_BATCH_EXISTS")
    g4_sha = sha(G4)
    intake = load(B / "manual_grabbed_20261012/manual_grabbed_1/intake_manifest.json")
    by_file = {f["file"]: f for f in intake["files"]}
    queue = []
    for fid, role in (("P2-1-he2019.pdf", "prospective_fresh_C8"), ("P2-3-qiu2021.pdf", "prospective_fresh_C8"),
                      ("王源杰（2018）硕士学位论文-毛竹叶黄酮碳苷C-糖基化途径及C-糖基转移酶的分析_王源杰.pdf", "prospective_fresh_C6_deferred")):
        f = by_file[fid]
        assert f["scientific_content_read"] is False and f["chemical_extracted"] is False
        queue.append(dict(file=fid, sha256=f["sha256"], bytes=f["bytes"], expected_doi=f["expected_doi"],
                          identity_status=f["identity_status"], role=role, unread=True))
    put(OUT / "fresh_pool_unlock.json", dict(task=T, at=now(), epoch_id="C-E03", family="C",
        G4=dict(path=str(G4), sha256=g4_sha),
        unlock_basis="C-E03 scope bank frozen (G4 bb4b508432bc622b57056371ffe18a1d7136a12aa1f799b740599e0d8eb7654f lineage) with 2 design build supports; per contract 3.2 fresh candidates may now be extracted after this freeze",
        design_exposure_boundary="liu2021 (build source) is late_prior_design and can never be fresh; the queue below was never content-read by the project",
        fresh_queue=queue, queue_size=len(queue),
        eligibility_per_target="each requires its own preregistered G5 full-qualification contract (identity A3, dual A4/A5, A6 prior clearance, scope applicability) before any scientific read",
        build_support_source="10.1021/acs.jafc.1c00602 (TcCGT1; in vitro demonstrated, dual acceptors apigenin/luteolin, C8 site computationally verified)",
        approval_type="agent_delegated", human_reviewed=False))
    ledger = B / "epoch_ledger.jsonl"
    row = dict(task=T, epoch_id="C-E03", family="C", stage="G5_FRESH_HOLDOUT_ACQUIRE", status="active",
        event_type="C_E03_fresh_pool_unlocked", at=now(), queue_size=len(queue), fresh_admitted=0,
        G4_manifest_sha256=g4_sha, approval_type="agent_delegated", human_reviewed=False)
    write(T, str(ledger), (ROOT / ledger).read_text() + json.dumps(row, sort_keys=True) + "\n")
    event(T, "C_E03_fresh_pool_unlocked", queue=len(queue))
    print(json.dumps(dict(unlocked=True, queue=len(queue), G4=g4_sha[:16])))

if __name__ == "__main__":
    main()

"""R83 finalize (resume-safe): exposure rows + batch summary."""
import json
from pathlib import Path
from scripts.operate import ROOT, write, event
from scripts.task016_p7_r18_PMC_originals import put, sha, now

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
OUT = B / "C/E03/design/C-E03-R83-liu2021-design-intake-v1"

def main():
    rows = []
    for role in ("A4", "A5"):
        started = json.loads((ROOT / OUT / role / "scientific_read_started.json").read_text())
        done = json.loads((ROOT / OUT / role / "article_text_harvest.json").read_text())
        for row in (started, done):
            keep = {k: row[k] for k in ("task", "approval_type", "human_reviewed", "family", "epoch_id", "batch_id",
                "reader_role", "reader_id", "source_id", "DOI", "closure_tokens", "raw_files", "development_exposed",
                "prior_design", "exposure_type", "future_fresh_eligible", "current_epoch_fresh_eligible",
                "read_other_extractor_output", "read_model_outcome", "event_type", "timestamp", "scientific_content_read")}
            rows.append(keep)
    write(T, str(OUT / "scientific_exposure_reads.jsonl"), "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))
    if not (ROOT / OUT / "A0_batch_summary.json").exists():
        put(OUT / "A0_batch_summary.json", dict(task=T, at=now(), batch="C-E03-R83-liu2021-design-intake",
            DOI="10.1021/acs.jafc.1c00602", custody="data/raw/task016-p7/manual_grabbed_20261012/manual_grabbed_1/P2-2-liu2021.pdf",
            crossref_status="available", readers={r: dict(chars=json.loads((ROOT / OUT / r / "article_text_harvest.json").read_text())["chars"]) for r in ("A4", "A5")},
            exposure_rows=len(rows), note="completed-event fields are embedded in each reader's article_text_harvest.json (no separate scientific_read_completed.json in this batch design)",
            next_step="A6 design-evidence determination: dual acceptors and C-site structural evidence; then G2/G3 scope build + G4 freeze",
            approval_type="agent_delegated", human_reviewed=False))
    event(T, "R83_finalized", exposure_rows=len(rows))
    print(json.dumps(dict(exposure_rows=len(rows), done=True)))

if __name__ == "__main__":
    main()

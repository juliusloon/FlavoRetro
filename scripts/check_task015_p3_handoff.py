"""Isolated browser and frozen-input checks for the TASK-015-P3 handoff."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from flavoretro.resources import sha
from scripts.operate import write

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/review/task015-p3/handoff-v2"
VALID = ROOT / "outputs/validation/task015-p3-handoff-v2"
TASK = "TASK-015-P3"


def main():
    if VALID.exists():
        raise ValueError("immutable validation output exists")
    manifest = json.loads((OUT / "manifest.json").read_text())
    packet = json.loads((OUT / "packet.json").read_text())
    assert manifest["cards"] == len(packet["cards"]) == 60
    assert manifest["glycoside_focus"] == 30
    assert sum(manifest["priorities"].values()) == 60
    assert len({x["id"] for x in packet["cards"]}) == 60
    for name, expected in manifest["outputs"].items():
        assert sha(OUT / name) == expected
    assert packet["source_hashes"]["task014_review"] == sha(ROOT / "outputs/triage/task014-final/review.jsonl")
    assert packet["source_hashes"]["task015_p1_review"] == sha(ROOT / "outputs/review/task015-p1/final-v2/review.jsonl")
    assert packet["source_hashes"]["task015_p2_crosswalk"] == sha(ROOT / "outputs/review/task015-p2/inbound-v1/card_crosswalk.tsv")
    VALID.mkdir(parents=True)
    errors = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto((OUT / "index.html").as_uri())
        assert page.locator("article.card").count() == 60
        assert page.locator("#progress").inner_text().startswith("0 / 60")
        assert page.locator("#position").inner_text().startswith("当前 1 / 13")
        assert page.evaluate("document.querySelectorAll('.mol svg').length > 0")
        page.locator("#filter").select_option("P1")
        assert page.locator("#position").inner_text().startswith("当前 1 / 25")
        page.locator("#filter").select_option("all")
        assert page.locator("#position").inner_text().startswith("当前 1 / 60")
        page.locator("#reviewer").fill("BROWSER TEST ONLY")
        page.locator("article.card:visible select[name=verdict]").select_option("agree")
        page.locator("article.card:visible input[name=structure_checked]").check()
        page.locator("article.card:visible button[type=submit]").click()
        assert page.locator("#progress").inner_text().startswith("1 / 60")
        with page.expect_download() as download:
            page.locator("#export").click()
        exported = VALID / "fixture-export.json"
        download.value.save_as(str(exported))
        envelope = json.loads(exported.read_text())
        assert envelope["status"] == "human_submission_pending_validation"
        assert envelope["split"] == "development_exposed"
        assert len(envelope["records"]) == 60
        assert sum(bool(r["review"]) for r in envelope["records"]) == 1
        assert envelope["records"][0]["review"]["reviewer_id"] == "BROWSER TEST ONLY"
        page.reload()
        assert page.locator("#progress").inner_text().startswith("1 / 60")
        other = browser.new_context(accept_downloads=True).new_page()
        other.goto((OUT / "index.html").as_uri())
        assert other.locator("#progress").inner_text().startswith("0 / 60")
        other.locator("#import").set_input_files(str(exported))
        assert other.locator("#progress").inner_text().startswith("1 / 60")
        bad = json.loads(exported.read_text())
        bad["source_hashes"]["task014_review"] = "bad"
        bad_path = VALID / "fixture-wrong-source.json"
        write(TASK, str(bad_path.relative_to(ROOT)), json.dumps(bad))
        other.locator("#import").set_input_files(str(bad_path))
        assert "导入失败" in other.locator("#message").inner_text()
        assert other.locator("#progress").inner_text().startswith("1 / 60")
        fresh = browser.new_context().new_page()
        fresh.on("pageerror", lambda error: errors.append(str(error)))
        fresh.goto((OUT / "index.html").as_uri())
        for width, height in ((1440, 1000), (390, 844), (320, 740)):
            fresh.set_viewport_size({"width": width, "height": height})
            assert not fresh.evaluate("document.documentElement.scrollWidth > innerWidth"), width
        assert not errors, errors
        browser.close()
    result = {"status": "passed", "checks": ["60 IDs/input hashes/output hashes", "empty human decisions", "priority filters", "structure SVG", "save and browser recovery", "JSON export/import", "source-hash rejection", "three viewport overflow", "zero JavaScript errors"], "fixture_only": "BROWSER TEST ONLY; not a user review"}
    write(TASK, str((VALID / "checks.json").relative_to(ROOT)), json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

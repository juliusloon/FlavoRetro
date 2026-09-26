import json, subprocess, time, urllib.request, uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from flavoretro.resources import ROOT, dumps

out = ROOT / "outputs/validation" / ("browser-" + uuid.uuid4().hex[:8])
out.mkdir(parents=True, exist_ok=False)
log = (out / "server.log").open("w")
server = subprocess.Popen(
    [sys.executable, "-B", "-m", "flavoretro.web", "--port", "8876"],
    cwd=ROOT,
    stdout=log,
    stderr=log,
)
try:
    for _ in range(50):
        try:
            urllib.request.urlopen("http://127.0.0.1:8876/api/health")
            break
        except Exception:
            time.sleep(0.2)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto("http://127.0.0.1:8876")
        page.wait_for_selector("#preset option:nth-child(2)", state="attached")
        # 拓扑标注验收（TASK-011）：糖苷 SMILES 触发家族标注、边界文案与键高亮
        page.locator("#smiles").fill("Oc1ccc(OC2OC(CO)C(O)C(O)C2O)cc1")
        page.locator("#preview").click()
        page.wait_for_selector("#topology .topology-block")
        topology_text = page.locator("#topology").inner_text()
        assert "aryl_O_candidate" in topology_text
        assert "labelled graph synthons, not reagents" in topology_text
        assert (
            "topology candidates; no independent labels or reaction feasibility"
            in topology_text
        )
        page.wait_for_function(
            "document.getElementById('molecule').src.includes('topology=1')"
        )
        page.wait_for_selector("#topology .topology-literature button")
        topology_lit_links = page.locator("#topology .topology-literature button").count()
        assert topology_lit_links > 0
        page.locator("#smiles").fill("CCOc1ccccc1")
        page.locator("#mode").select_option("balanced")
        page.locator("#search-form details").click()
        page.locator("#seconds").fill("1")
        page.locator("#iterations").fill("3")
        page.locator("#engine").select_option("optimized")
        page.locator("#top_k").fill("2")
        page.locator("#depth").fill("4")
        page.locator("#branching").fill("2")
        page.locator("#nodes").fill("7")
        page.locator("#submit").click()
        page.wait_for_function(
            "document.getElementById('message').textContent.includes('本次实时搜索完成')",
            timeout=120000,
        )
        assert "阶段 2" in page.locator("#run-meta").inner_text()
        assert page.locator(".route").count() > 0
        live = page.evaluate("lastResult")
        assert live["request"]["engine"] == "optimized" and live["request"]["top_k"] == 2
        assert all(live["request"][key] == value for key,value in (("depth",4),("branching",2),("nodes",7),("seconds",1),("iterations",3)))
        assert all(p["node_count"] <= 7 for p in live["phases"])
        assert live["resource_version"] == "v3"
        assert "模板未识别" in page.locator(".route").first.inner_text()
        with page.expect_download() as downloaded:
            page.locator("#download").click()
        downloaded.value.save_as(str(out / "export.json"))
        exported=json.loads((out / "export.json").read_text())
        assert exported["manifest"]["run_id"] == live["run_id"]
        page.screenshot(path=str(out / "desktop.png"), full_page=True)
        page.locator("[data-tab=resources]").click()
        page.locator("#kind").select_option("stock")
        page.wait_for_function(
            "document.getElementById('count').textContent.includes('共 49 条')"
        )
        page.locator("#rows button").first.click()
        assert "source_sha256" in page.locator("#record-json").inner_text()
        page.locator("#qc-filter").select_option("name_conflict")
        page.wait_for_function("document.getElementById('count').textContent.includes('共 3 条')")
        page.locator("#qc-filter").select_option("")
        page.locator("#kind").select_option("")
        page.locator("#outcome-filter").select_option("missing")
        page.wait_for_function("document.getElementById('count').textContent.includes('共 1075 条')")
        page.locator("#outcome-filter").select_option("zero")
        page.wait_for_function("document.getElementById('count').textContent.includes('共 0 条')")
        page.locator("#outcome-filter").select_option("")
        page.locator("#source-filter").select_option("note_located_token_found")
        page.wait_for_function("document.getElementById('count').textContent.includes('共 249 条')")
        page.screenshot(path=str(out / "resources.png"),full_page=True)
        page.locator("#source-filter").select_option("")
        page.locator("[data-tab=literature]").click()
        page.wait_for_selector("#literature-list .paper-card")
        literature_cards = page.locator("#literature-list .paper-card").count()
        assert literature_cards == 15
        page.locator("#teaching-catalog > summary").click()
        page.wait_for_function("document.querySelectorAll('.teaching-entry').length===27")
        assert "未识别" in page.locator("#teaching-list").inner_text()
        page.screenshot(path=str(out / "literature.png"),full_page=True)
        page.locator("[data-tab=governance]").click()
        page.wait_for_selector(".stat")
        assert page.locator(".stat").count() == 4
        page.wait_for_function("document.getElementById('foundation-status').textContent.includes('v3')")
        page.wait_for_function("document.getElementById('preflight-status').textContent.includes('formal_run_ready')")
        preflight=json.loads(page.locator("#preflight-status").inner_text())
        assert not preflight["formal_run_ready"]
        before = page.request.get("http://127.0.0.1:8876/api/runs").json()["total"]
        page.locator("#saved-run-id").fill(live["run_id"])
        page.locator("#open-run").click()
        page.wait_for_function("document.getElementById('message').textContent.includes('explicit_saved_run')")
        assert "历史运行" in page.locator("#run-meta").inner_text()
        assert page.request.get("http://127.0.0.1:8876/api/runs").json()["total"] == before
        page.locator("[data-tab=governance]").click()
        page.locator("#start-evaluation").click()
        page.wait_for_function("document.getElementById('evaluation-message').textContent.includes('running')",timeout=15000)
        busy = page.request.post("http://127.0.0.1:8876/api/search",data=json.dumps({"smiles":"CCO"}),headers={"Content-Type":"application/json"})
        assert busy.status == 429
        page.wait_for_function("document.getElementById('evaluation-message').textContent.includes('completed')",timeout=180000)
        job=json.loads(page.locator("#evaluation-json").text_content())
        assert job["status"] == "completed" and job["summary"]["completed_cells"] == 12 and job["summary"]["failures"] == 0
        assert page.locator("#evaluation-cells tr").count() == 12
        page.screenshot(path=str(out / "governance.png"),full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        mobile_overflow = {}
        for tab in ("search","resources","literature","governance"):
            page.locator(f"[data-tab={tab}]").click()
            mobile_overflow[tab] = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            page.screenshot(path=str(out / ("mobile-"+tab+".png")),full_page=True)
        page.locator("[data-tab=search]").click()
        assert not any(mobile_overflow.values()),mobile_overflow
        overflow = page.evaluate(
            "document.documentElement.scrollWidth > window.innerWidth"
        )
        page.screenshot(path=str(out / "mobile.png"), full_page=True)
        assert not overflow
        invalid = page.request.post(
            "http://127.0.0.1:8876/api/search",
            data=json.dumps({"smiles": "INVALID"}),
            headers={"Content-Type": "application/json"},
        )
        assert invalid.status == 400
        page.locator("#smiles").fill("INVALID")
        page.locator("#submit").click()
        page.wait_for_function("document.getElementById('message').textContent.includes('搜索失败')")
        # UI-only engine failure fixture; real timeout/failure recording has unit contracts.
        page.locator("#smiles").fill("CCO")
        page.route("**/api/search",lambda route: route.fulfill(status=503,content_type="application/json",body=json.dumps({"error":{"message":"engine fixture failure"}})))
        page.locator("#submit").click()
        page.wait_for_function("document.getElementById('message').textContent.includes('engine fixture failure')")
        page.unroute("**/api/search")
        assert not errors, errors
        (out / "report.json").write_text(
            dumps(
                {
                    "browser": "Chromium",
                    "python":sys.executable,
                    "desktop": [1440, 1000],
                    "mobile": [390, 844],
                    "overflow": overflow,
                    "js_errors": errors,
                    "live_search": True,
                    "two_phases": True,
                    "resource_detail": True,
                    "all_search_parameters":True,
                    "resource_filters":{"conflicts":3,"missing":1075,"zero":0,"note_token_found":249},
                    "teaching_entries":27,
                    "saved_run_no_new_mcts":True,
                    "saved_run_id":live["run_id"],
                    "manifest_export":True,
                    "development_evaluation":{"id":job["evaluation_id"],"cells":12,"failures":0},
                    "shared_gate_http_status":busy.status,
                    "formal_run_ready":False,
                    "mobile_all_pages_overflow":mobile_overflow,
                    "invalid_input_ui":True,
                    "engine_failure_ui_fixture":True,
                    "literature_cards": literature_cards,
                    "topology_block": True,
                    "topology_lit_links": topology_lit_links,
                    "invalid_http_status": invalid.status,
                    "scope": "local browser engineering acceptance, not human usability",
                }
            )
        )
        browser.close()
    print((out / "report.json").read_text())
finally:
    server.terminate()
    server.wait(timeout=10)
    log.close()

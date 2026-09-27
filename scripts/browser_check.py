import json, subprocess, time, urllib.request, uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import sync_playwright
from flavoretro.resources import ROOT, dumps

# TASK-013：在既有验收（拓扑/搜索/筛选/历史运行/12-cell/错误分支）之上，新增
# tablist 语义与键盘导航、skip link、骨架屏、触控目标、reduced-motion、
# 320/375/768/992/1280/390 六档视口四页横向溢出断言。

out = ROOT / "outputs/validation" / ("browser-" + uuid.uuid4().hex[:8])
out.mkdir(parents=True, exist_ok=False)
log = (out / "server.log").open("w")
server = subprocess.Popen(
    [sys.executable, "-B", "-m", "flavoretro.web", "--port", "8876"],
    cwd=ROOT,
    stdout=log,
    stderr=log,
)


def touch_targets(page, selectors):
    return page.evaluate(
        """sels => Object.fromEntries(sels.map(([name, sel]) => {
            const el = document.querySelector(sel);
            if (!el) return [name, null];
            const r = el.getBoundingClientRect();
            return [name, [Math.round(r.width), Math.round(r.height)]];
        }))""",
        selectors,
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
        # TASK-013 S3：skip link 为首个焦点，tablist 语义完整
        page.keyboard.press("Tab")
        assert page.evaluate("document.activeElement.classList.contains('skip-link')")
        assert page.locator("nav[role=tablist]").count() == 1
        assert page.locator("[data-tab=search]").get_attribute("role") == "tab"
        assert page.locator("[data-tab=search]").get_attribute("aria-selected") == "true"
        assert page.locator("[data-tab=resources]").get_attribute("aria-selected") == "false"
        assert page.locator("[data-tab=resources]").get_attribute("tabindex") == "-1"
        assert page.locator("#search").get_attribute("role") == "tabpanel"
        assert page.locator("#search").get_attribute("aria-labelledby") == "tab-search"
        assert page.evaluate("document.querySelectorAll('th:not([scope])').length") == 0
        # TASK-013 S3：方向键循环切换页签（roving tabindex + focus 跟随）
        page.locator("[data-tab=search]").focus()
        page.keyboard.press("ArrowRight")
        assert page.locator("[data-tab=resources]").get_attribute("aria-selected") == "true"
        assert page.evaluate("document.activeElement.dataset.tab") == "resources"
        assert not page.locator("#resources").is_hidden()
        page.keyboard.press("ArrowLeft")
        assert page.locator("[data-tab=search]").get_attribute("aria-selected") == "true"
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
        # TASK-013 S3：搜索进行中骨架屏与 aria-busy
        page.wait_for_selector('#routes[aria-busy="true"] .skeleton-card', timeout=5000)
        page.wait_for_function(
            "document.getElementById('message').textContent.includes('本次实时搜索完成')",
            timeout=120000,
        )
        assert page.evaluate("!document.getElementById('routes').hasAttribute('aria-busy')")
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
        # TASK-013：探索页触控目标 ≥44×44
        targets = touch_targets(page, [
            ["tab-search", "[data-tab=search]"],
            ["tab-resources", "[data-tab=resources]"],
            ["submit", "#submit"],
            ["preview", "#preview"],
            ["check-row", "label.check"],
            ["smiles", "#smiles"],
        ])
        for name, box in targets.items():
            assert box and box[0] >= 44 and box[1] >= 44, (name, box)
        page.screenshot(path=str(out / "desktop.png"), full_page=True)
        page.locator("[data-tab=resources]").click()
        page.locator("#kind").select_option("stock")
        page.wait_for_function(
            "document.getElementById('count').textContent.includes('共 49 条')"
        )
        page.locator("#rows button").first.click()
        assert "source_sha256" in page.locator("#record-json").inner_text()
        # TASK-013：表格按钮触控目标 ≥44×44
        row_targets = touch_targets(page, [["rows-view", "#rows button"]])
        for name, box in row_targets.items():
            assert box and box[0] >= 44 and box[1] >= 44, (name, box)
        targets.update(row_targets)
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
        # TASK-013 S2：六档视口四页横向溢出断言（移动优先断点 768/992/1280 + 390 既有档）
        overflow_report = {}
        for width, height in [(320, 700), (375, 740), (768, 900), (992, 900), (1280, 1000), (390, 844)]:
            page.set_viewport_size({"width": width, "height": height})
            for tab in ("search", "resources", "literature", "governance"):
                page.locator(f"[data-tab={tab}]").click()
                page.wait_for_timeout(120)
                overflow_report[f"{width}:{tab}"] = page.evaluate(
                    "document.documentElement.scrollWidth > window.innerWidth"
                )
                if width == 390:
                    page.screenshot(path=str(out / ("mobile-" + tab + ".png")), full_page=True)
            page.locator("[data-tab=search]").click()
            page.wait_for_timeout(120)
            page.screenshot(path=str(out / f"viewport-{width}-search.png"), full_page=True)
        assert not any(overflow_report.values()), overflow_report
        mobile_overflow = {k: v for k, v in overflow_report.items() if k.startswith("390:")}
        overflow = any(mobile_overflow.values())
        page.screenshot(path=str(out / "mobile.png"), full_page=True)
        assert not overflow
        # TASK-013 S3：prefers-reduced-motion 下无过渡动画
        page.emulate_media(reduced_motion="reduce")
        motion_free = page.evaluate(
            "getComputedStyle(document.getElementById('submit')).transitionDuration"
        )
        assert motion_free == "0s", motion_free
        page.emulate_media(reduced_motion="no-preference")
        invalid = page.request.post(
            "http://127.0.0.1:8876/api/search",
            data=json.dumps({"smiles": "INVALID"}),
            headers={"Content-Type": "application/json"},
        )
        assert invalid.status == 400
        page.locator("#smiles").fill("INVALID")
        page.locator("#submit").click()
        page.wait_for_function("document.getElementById('message').textContent.includes('搜索失败')")
        # TASK-013 S3：失败提示为 role=alert，新搜索恢复 role=status
        assert page.locator("#message").get_attribute("role") == "alert"
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
                    "viewports": [320, 375, 768, 992, 1280, 390],
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
                    "viewport_overflow_all":overflow_report,
                    "invalid_input_ui":True,
                    "engine_failure_ui_fixture":True,
                    "literature_cards": literature_cards,
                    "topology_block": True,
                    "topology_lit_links": topology_lit_links,
                    "invalid_http_status": invalid.status,
                    "aria_tablist": True,
                    "skip_link_first_focus": True,
                    "keyboard_arrow_tabs": True,
                    "skeleton_loading": True,
                    "error_role_alert": True,
                    "reduced_motion_no_transition": motion_free,
                    "touch_targets": targets,
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

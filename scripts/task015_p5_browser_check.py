# -*- coding: utf-8 -*-
"""TASK-015-P5 验收：handoff-v3 无头浏览器功能核验。

覆盖：渲染与 JS 错误、60 卡、校验拦截（亲核缺定位/收率未先亲核）、
保存→进度、localStorage 重载恢复、envelope 绑定、错哈希导入拒绝、
合法导入回灌、桌面/移动视口横向溢出与截图。

前置：本地 HTTP 服务已提供 handoff-v3/index.html。
输出：outputs/validation/task015-p5-browser/check.json 与两张截图。
"""

import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = "http://127.0.0.1:8766/"
OUT = ROOT / "outputs/validation/task015-p5-browser"
results = {"js_errors": [], "checks": {}}


def check(name, ok, detail=""):
    results["checks"][name] = {"ok": bool(ok), "detail": detail}
    return ok


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.on("pageerror", lambda e: results["js_errors"].append(str(e)))
    page.on("console", lambda m: results["js_errors"].append(m.text) if m.type == "error" else None)
    page.goto(URL, wait_until="domcontentloaded")

    check("title", "TASK-015-P5" in page.title(), page.title())
    check("progress_initial", "0 / 60" in page.locator("#progress").inner_text())
    n_cards = page.locator("article.card").count()
    check("cards_60", n_cards == 60, f"cards={n_cards}")
    pid_packet = page.evaluate("JSON.parse(document.querySelector('#packet').textContent).packet_id")
    check("packet_id_present", pid_packet.startswith("task015-p5-axes-handoff-v3-"), pid_packet)

    # 全部显示后再逐卡操作（应用为单卡显示模式）
    page.select_option("#filter", "all")
    page.wait_for_timeout(200)

    # 校验拦截 1：亲核未填定位
    page.fill("#reviewer", "TASK019-浏览器自检")
    form = page.locator("#card-1 form")
    form.locator("select[name=ps_status]").select_option("verified_primary")
    form.locator("button[type=submit]").click()
    check("reject_primary_without_locator", "具体定位" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())

    # 校验拦截 2：收率核对未先亲核
    form.locator("select[name=ps_status]").select_option("deferred")
    form.locator("select[name=yield_status]").select_option("verified")
    form.locator("button[type=submit]").click()
    check("reject_yield_before_primary", "先亲核原文" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())

    # 合法保存卡 1
    form.locator("select[name=ps_status]").select_option("verified_primary")
    form.locator("input[name=ps_locator]").fill("DOI 10.1021/op4003642, p.614, Scheme 2, compound 1")
    form.locator("textarea[name=evidence_excerpt]").fill("…afforded compound 1 in 76% isolated yield…")
    form.locator("select[name=yield_status]").select_option("verified")
    form.locator("input[name=yield_value]").fill("76% 分离收率，归属产物 1")
    form.locator("button[type=submit]").click()
    check("save_card1", "已保存" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())
    check("progress_after_save", "1 / 60" in page.locator("#progress").inner_text(),
          page.locator("#progress").inner_text())

    # SHA 校验拦截：非法哈希（前进到卡 2）
    page.locator("#next").click()
    form2 = page.locator("#card-2 form")
    form2.locator("select[name=ps_status]").select_option("verified_primary")
    form2.locator("input[name=ps_locator]").fill("patent US1234567, example 3")
    form2.locator("textarea[name=evidence_excerpt]").fill("example text")
    form2.locator("input[name=ps_sha256]").fill("not-a-hash")
    form2.locator("button[type=submit]").click()
    check("reject_bad_sha256", "64 位十六进制" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())

    # envelope 绑定检查
    env = page.evaluate("() => JSON.stringify(envelope())")
    env = json.loads(env)
    check("envelope_records_60", len(env["records"]) == 60)
    check("envelope_packet_binding", env["packet_id"] == pid_packet and len(env["source_hashes"]) == 6)
    saved1 = next(r for r in env["records"] if r["card_number"] == 1)
    check("envelope_card1_saved", saved1["review"] and saved1["review"]["ps_status"] == "verified_primary")

    # 重载恢复（localStorage）
    page.reload(wait_until="domcontentloaded")
    check("restore_after_reload", "1 / 60" in page.locator("#progress").inner_text(),
          page.locator("#progress").inner_text())

    # 导入拒绝：错 packet_id
    tampered = dict(env, packet_id="task015-p5-axes-handoff-v3-tampered")
    Path("/tmp/t19-tampered.json").write_text(json.dumps(tampered), encoding="utf-8")
    page.set_input_files("#import", "/tmp/t19-tampered.json")
    check("import_reject_wrong_packet", "不符" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())

    # 合法导入回灌
    Path("/tmp/t19-valid.json").write_text(json.dumps(env), encoding="utf-8")
    page.set_input_files("#import", "/tmp/t19-valid.json")
    check("import_valid", "已导入" in page.locator("#message").inner_text(),
          page.locator("#message").inner_text())

    # 桌面视口溢出 + 截图
    ow = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    check("desktop_no_h_overflow", ow[0] <= ow[1] + 1, f"scroll={ow[0]} client={ow[1]}")
    OUT.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(OUT / "desktop-1440.png"), full_page=False)

    # 移动视口
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(300)
    ow2 = page.evaluate("() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    check("mobile_no_h_overflow", ow2[0] <= ow2[1] + 1, f"scroll={ow2[0]} client={ow2[1]}")
    page.screenshot(path=str(OUT / "mobile-390.png"), full_page=False)

    browser.close()

results["all_ok"] = all(v["ok"] for v in results["checks"].values()) and not results["js_errors"]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "check.json").write_text(json.dumps(results, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(results, ensure_ascii=False, indent=1, sort_keys=True))

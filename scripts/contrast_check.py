"""TASK-013 对比度与 token 守卫（纯标准库）。

1. 解析 web/style.css 的 :root 自定义属性，对 docs/WEB_UI_DESIGN.md §2.1 的
   全部文字/语义配色对复测 WCAG 对比度（正文级 ≥4.5:1，装饰/大字号 ≥3:1）。
2. token 漂移守卫：硬编码 hex 色值只允许出现在 :root 块内。
输出 outputs/validation/contrast-<id>/report.json；任一失败退出码 1。
"""

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "web" / "style.css"


def parse_tokens(text):
    match = re.search(r":root\s*\{(.*?)\}", text, re.S)
    if not match:
        raise SystemExit("style.css 缺少 :root token 块")
    return dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})\b", match.group(1)))


def luminance(hex_value):
    h = hex_value.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# (前景 token, 背景 token, 最低比值, 用途)。4.5 = 正文级 AA；3.0 = 大字号/装饰/非文本。
PAIRS = [
    ("--ink", "--bg", 4.5, "正文 on 页面底"),
    ("--ink", "--surface", 4.5, "正文 on 卡片"),
    ("--ink", "--green-50", 4.5, "message 文字"),
    ("--ink", "--green-100", 4.5, "stat 数字与标签"),
    ("--ink-2", "--bg", 4.5, "次级文字 on 页面底"),
    ("--ink-2", "--surface", 4.5, "次级文字 on 卡片"),
    ("--ink-2", "--field", 4.5, "次级文字 on 输入底/叶卡"),
    ("--ink-2", "--green-50", 4.5, "tag neutral 文字"),
    ("--ink-3", "--bg", 4.5, "弱化文字下限（footer/空态）"),
    ("--ink-3", "--surface", 4.5, "弱化文字 on 卡片"),
    ("--ink-3", "--field", 4.5, "拓扑阴性说明 on 叶卡"),
    ("--accent-text", "--bg", 4.5, "eyebrow 小标签"),
    ("--accent-text", "--surface", 4.5, "summary  Disclosure on 卡片"),
    ("--green-600", "--surface", 4.5, "链接 on 卡片"),
    ("--green-700", "--surface", 4.5, "skip link on 页面"),
    ("--green-700", "--amber-50", 4.5, "教学依据链接 on 教学底"),
    ("--green-800", "--green-50", 4.5, "次级按钮/chip 文字"),
    ("--green-800", "--green-100", 4.5, "chip 文字 on 悬停底"),
    ("--green-800", "--bg", 4.5, "section-title"),
    ("--surface", "--green-600", 4.5, "主按钮文字"),
    ("--surface", "--green-700", 4.5, "主按钮悬停文字"),
    ("--amber-700", "--amber-100", 4.5, "tag 琥珀"),
    ("--amber-700", "--warning-bg", 4.5, "fact-line 声明行"),
    ("--amber-800", "--amber-50", 4.5, "教学块文字/banner"),
    ("--partial-ink", "--partial-bg", 4.5, "tag partial 未闭合"),
    ("--danger-ink", "--danger-bg", 4.5, "hazard/错误 alert"),
    ("--info-ink", "--info-bg", 4.5, "拓扑 tag"),
    ("--header-ink", "--header-bg", 4.5, "顶栏主文字"),
    ("--header-ink-2", "--header-bg", 4.5, "顶栏未选页签"),
    ("--surface", "--header-chip", 4.5, "顶栏选中页签"),
    ("--header-accent", "--header-bg", 3.0, "页签琥珀下划线（装饰）"),
    ("--green-300", "--header-bg", 3.0, "badge 描边（非文本）"),
    ("--ink", "--surface", 3.0, "焦点内环 on 浅底（双环指示浅侧）"),
    ("--amber-400", "--header-bg", 3.0, "焦点外环 on 顶栏（双环指示深侧）"),
]

# 装饰豁免（WCAG 1.4.11 装饰例外：不承载组件识别或状态信息，登记备查）
EXEMPTIONS = [
    "卡片/message 左侧 3px 强调条（--green-300，实测 2.24:1）：卡片由完整 1px 边框与底色识别，强调条纯装饰",
    "空态 60px 图形 .empty>span（--green-300）：纯装饰水印，邻近 h2/p 文本已传达全部信息",
]


def main():
    text = STYLE.read_text()
    tokens = parse_tokens(text)
    missing = [t for pair in PAIRS for t in pair[:2] if t not in tokens]
    # token 漂移守卫：去掉 :root 块与注释后不允许出现 hex 色值
    body = re.sub(r":root\s*\{.*?\}", "", text, count=1, flags=re.S)
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    drift = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", body)))
    results = []
    failures = []
    for fg, bg, minimum, note in PAIRS:
        if fg in tokens and bg in tokens:
            ratio = round(contrast(tokens[fg], tokens[bg]), 2)
            ok = ratio >= minimum
            results.append({"fg": fg, "bg": bg, "fg_value": tokens[fg], "bg_value": tokens[bg],
                            "ratio": ratio, "min": minimum, "pass": ok, "note": note})
            if not ok:
                failures.append(f"{note}: {fg}({tokens[fg]}) on {bg}({tokens[bg]}) = {ratio} < {minimum}")
    for token in sorted(set(missing)):
        failures.append("缺少 token 定义：" + token)
    for hex_value in drift:
        failures.append(":root 之外硬编码色值：" + hex_value)
    out = ROOT / "outputs/validation" / ("contrast-" + uuid.uuid4().hex[:8])
    out.mkdir(parents=True, exist_ok=False)
    report = {
        "task": "TASK-013",
        "time": datetime.now(timezone.utc).isoformat(),
        "style": "web/style.css",
        "pairs_checked": len(results),
        "all_pass": not failures,
        "failures": failures,
        "results": results,
        "decorative_exemptions": EXEMPTIONS,
        "scope": "WCAG 2.2 AA 工程复测；正文级 ≥4.5:1，装饰/大字号/非文本 ≥3:1；非人工可用性结论",
    }
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

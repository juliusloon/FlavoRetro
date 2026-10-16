"""v38: owner-originals intake + SS G5 freeze section."""
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
from scripts.operate import ROOT, write

T = "TASK-016-P7"; B = Path("outputs/task016-p7/v1")
REPORT = Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md")
STATE = Path("STATE.md")
SNAP = B / "report_snapshots"

def sha(p): return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
def pointer(p): return {"path": str(p), "sha256": sha(p)}

SECTION = """

## progress-v38-final：所有者代取原件入库与 SS G5 冻结（2026-10-12）

所有者将统一代取清单的 **11 份 PDF 原件全部送达** `temp/manual_grabbed_1/`。按 R3 manual-custody 先例完成不可变入库（SHA 绑定+首页身份核验，无科学内容阅读）：10 件 provisionally verified（5 件现代论文首页 DOI 字面命中），kho1978 弱记录标注，kamsteeg1979 实际题目为 Petunia 6″-O-鼠李糖基转移酶（越出冻结 SS-E02 scope，降为边界参考——R74 预期标题系引用语境误推，已更正记录）。

**独立审查**（审阅者 Saved agent，只读）：A11 通过（SHA 重算一致、无内容阅读、无旁路；并纠正任务书中 112.198069 系 Trapero DOI 片段的标注错误）；A6(a) 两候选标识符与全部曝光账**零相交**；A6(b) pea 1982 同队列裁定 **not_blocked**（附三条件：1979 G6 裁定文件证明其已读内容未确立内糖 O2 位点/逐酶专一性）；A6(c) morita2005 面板两分支已书面预注册。

**SS-E02-R80 G5 已冻结**（两候选：pea 1982 + Morita 2005；G5 SHA 1f0f4819…；epoch ledger R80 行；A4/A5 内容阅读解锁）。构建过程中按 supersession 先例归档了 4 份草稿（含 malformed-alias 草稿、过期合同与事件目录）。**C8 簇（Angew 2019/JAFC 2021/BioOrg 2021）内容阅读继续推迟**至 C-E03 设计/冻结时序——现在读会烧掉 prospective fresh 池。

下一步（下一批）：R80 A4/A5 双独立抽取（pdftotext 双解析器）→ A6 反应级闭包与准入 → Trapero 2012/Shi 2026/EfCGT1 密封件同批处理。本轮零 HTTP、零 MCTS、零化学检视。机器凭证：`manual_grabbed_20261012/manual_grabbed_1/intake_manifest.json`、`governance/R80-owner-originals-A11-A6-v1/`、`SS/E02/fresh/SS-E02-R80-owner-originals-full-qualification-v1/`。
"""

def main():
    rep = (ROOT / REPORT).read_text(encoding="utf-8")
    if "progress-v38-final：所有者代取原件入库" not in rep:
        write(T, str(Path("docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md.pre-v38.md")), rep)
        rep2 = rep.replace("当前权威截面 **progress-v37-final（见文末）**", "当前权威截面 **progress-v38-final（见文末）**", 1)
        if rep2 == rep: raise RuntimeError("HEADER_ANCHOR_NOT_FOUND")
        write(T, str(REPORT), rep2.rstrip("\n") + "\n" + SECTION)
    st = (ROOT / STATE).read_text(encoding="utf-8")
    if "R80 G5 已冻结" not in st:
        anchor = "统一代取清单 `outputs/task016-p7/v1/governance/R79-originals-request-v1/originals_request_list.md`（P1×2/P2×3/P3×6）已交付所有者；全局 1298 HTTP / 1,245,739,256 B。"
        if anchor not in st: raise RuntimeError("STATE_ANCHOR_NOT_FOUND")
        add = ("所有者已送达全部 11 份 PDF 原件（R38 入库：SHA 绑定+首页身份，独立 A11/A6 审查通过，pea1982 同队列 not_blocked）；"
               "SS-E02-R80 G5 已冻结（pea1982+morita2005 两候选，SHA 1f0f4819…），A4/A5 内容阅读解锁待下一批。")
        write(T, str(STATE), st.replace(anchor, anchor + add, 1))
    p = SNAP / "progress-v38-final.json"
    if not (ROOT / p).exists():
        write(T, str(p), json.dumps(dict(task=T, version="progress-v38-final",
            as_of=datetime.now(timezone.utc).isoformat(),
            status="owner_originals_intake_complete_SS_G5_frozen",
            approval_type="agent_delegated", human_reviewed=False,
            intake=pointer(B / "manual_grabbed_20261012/manual_grabbed_1/intake_manifest.json"),
            reviews={"A11": pointer(B / "governance/R80-owner-originals-A11-A6-v1/A11_independent_review.json"),
                     "A6": pointer(B / "governance/R80-owner-originals-A11-A6-v1/A6_exposure_projection_review.json")},
            g5=dict(family="SS", batch="SS-E02-R80-owner-originals-full-qualification", sources=2,
                    sha256="1f0f481932014906ccc9e1f6638f071f64eb5ac5090240decc670dcd70e62698",
                    science_reads=0, fresh_admitted=0),
            next=["A4/A5 dual extraction", "A6 reaction-level closure", "sealed trio same batch"]),
            ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(report_sha=sha(REPORT), state_sha=sha(STATE)), ensure_ascii=False))

if __name__ == "__main__":
    main()

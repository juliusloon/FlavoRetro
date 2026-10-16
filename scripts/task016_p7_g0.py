"""Approved P7 baseline; never resets an existing frozen baseline."""
import hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from scripts.operate import write, event
ROOT = Path(__file__).resolve().parents[1]
TASK = "TASK-016-P7"
OUT = ROOT / "outputs/task016-p7/v1"
CONTRACT = "docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md"
def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def save(n,v):
    write(TASK, str((OUT/n).relative_to(ROOT)), json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
def main():
    if (OUT/"approval.json").exists(): raise RuntimeError("P7 baseline already frozen")
    inherited=json.loads((ROOT/"outputs/task016-p6/v1/protected_hashes.json").read_text())
    drift=[p for p,h in inherited.items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
    if drift:
        save("g0_protection_failure.json",dict(drift=drift)); raise RuntimeError("inherited protection drift")
    mutable={CONTRACT,"STATE.md","ARCHITECTURE.md","docs/README.md","docs/tasks/README.md","docs/reports/README.md","docs/WORKBENCH_ROADMAP.md","docs/PAPER_ROADMAP.md","flavoretro/cli.py","flavoretro/contracts.py","flavoretro/worker.py","flavoretro/service.py","flavoretro/workspace.py","flavoretro/task016_runs.py","flavoretro/glycoside_scope.py"}
    protected={p:h for p,h in inherited.items() if p not in mutable}
    for folder in ["outputs/task016-p6","data/raw/task016-p6","configs","flavoretro/assets/configs","metadata","outputs/review/task015-06/v1","data/derived/v3"]:
        for p in (ROOT/folder).rglob("*"):
            r=str(p.relative_to(ROOT))
            if p.is_file() and not p.name.startswith("._") and r not in mutable: protected[r]=sha(p)
    for folder,pattern in [("scripts","task016*.py"),("tests","test_task016*.py"),("flavoretro","glycoside*.py"),("docs/tasks","TASK-016*.md"),("docs/reports","REPORT-016*.md")]:
        for p in (ROOT/folder).glob(pattern):
            r=str(p.relative_to(ROOT))
            if r not in mutable and "p7" not in p.name.lower(): protected[r]=sha(p)
    originals={}
    for r in sorted(mutable):
        if (ROOT/r).is_file():
            snapshot="operations/task016-p7-original/"+r
            write(TASK,snapshot,(ROOT/r).read_text()); originals[r]=dict(sha256=sha(ROOT/r),snapshot=snapshot)
    approved=sha(ROOT/CONTRACT)
    budgets=dict(search_attempts=600,C_first_matrix=81,SS_first_matrix=81,legacy_canary=90,engineering=60,revalidation=252,HTTP=8000,bytes=8*1024**3,article_versions=400,attachments=800,per_url_attempts=2,recovery_extra_attempts=1,concurrency=4)
    save("approval.json",dict(task=TASK,contract=CONTRACT,approved_contract_sha256=approved,approval_quote="/goal `docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md` 批准开始执行.",authorization_origin="owner explicit instruction",approval_type="agent_delegated",human_reviewed=False,approved_date="2026-10-07",created_at=datetime.now(timezone.utc).isoformat(),budgets=budgets,SI_authorized_by_contract=True,no_git_sync=True))
    save("protected_hashes.json",protected)
    save("execution_baseline.json",dict(contract_sha256=approved,git_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),git_status=subprocess.check_output(["git","status","--short"],cwd=ROOT,text=True),protected_count=len(protected),inherited_count=len(inherited),inherited_drift=drift,mutable_originals=originals,python=sys.version,platform=platform.platform(),budgets=budgets))
    for n in ["epoch_ledger.jsonl","run_ledger.jsonl"]: write(TASK,str((OUT/n).relative_to(ROOT)),"")
    text=(ROOT/CONTRACT).read_text().replace("- 状态：**Proposed（拟议，未授权执行）**。","- 状态：**In Progress（2026-10-07 已批准开始执行）**。").replace("- 执行批准：待所有者另行明确批准；批准后按实际授权类型记录，禁止写成 human_reviewed。","- 执行批准：所有者 2026-10-07 明确批准开始执行；批准和阶段决定记录 agent_delegated，非 human_reviewed；原始授权与合同 SHA 见 outputs/task016-p7/v1/approval.json。").replace("- 执行者：待批准后登记；建议主控 Cano + 多角色 subagent/harness。","- 执行者：主控 Cano + 按第四节隔离的 subagent/harness。")
    text += "\n- 2026-10-07 执行登记：所有者批准开始执行；原合同 SHA "+approved+"；批准记录 agent_delegated。独立来源/搜索硬预算按第六/十五节执行；不含 Git 同步。\n"
    write(TASK,CONTRACT,text)
    state=(ROOT/"STATE.md").read_text()
    old=next(x for x in state.splitlines() if x.startswith("TASK-016-P7（"))
    new="TASK-016-P7（2026-10-07）：[领域对齐的新底物迁移闭环与 Roadmap P2 终验](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md) **In Progress**。所有者明确批准开始执行，批准及阶段决定 agent_delegated。实际工作区基线与保护 SHA 已冻结；按独立 C/SS scope-first → freeze → fresh-holdout → epoch、角色隔离 harness 执行，搜索硬上限600、来源8000请求/8GiB/400文章/800附件。科学完成门与 formal/release 边界保持合同原值；最终结论待验收。"
    write(TASK,"STATE.md",state.replace(old,new))
    event(TASK,"g0_completed",protected=len(protected),inherited_drift=drift,approved_contract_sha256=approved)
    print(json.dumps(dict(protected=len(protected),inherited_drift=drift,approved_contract_sha256=approved)))
if __name__=="__main__": main()

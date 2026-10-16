# -*- coding: utf-8 -*-
"""TASK-015-P5 阶段 A：生成 60 卡一手来源/收率轴审核包 handoff-v3。

输入（全部只读）：
  outputs/review/task015-v2/index.html      内嵌 #payload（60 卡结构 SVG/原始事实/引用）
  outputs/review/task015-p1/final-v2/review.jsonl  P1 代理审核（来源定位、收率评估）
  outputs/review/task015-p3/handoff-v2/gap_register.tsv  优先级/来源等级/定位线索
  outputs/review/task015-p3/final/review-final-60.json   结构轴已冻结结论
  outputs/review/task015-p3/gold-v1/gold.jsonl / excluded.jsonl  gold 成员
  outputs/review/task015-p3/handoff-v2/index.html  复用其 CSS

输出：outputs/review/task015-p5-axes/handoff-v3/{index.html,packet.json,manifest.json,README.md}
确定性：无运行时时间戳；packet_id 由输入哈希派生；两次构建逐字节一致。
"""

import csv
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-09-29"
OUT = ROOT / "outputs/review/task015-p5-axes/handoff-v3"

PAYLOAD_HTML = ROOT / "outputs/review/task015-v2/index.html"
P1_REVIEW = ROOT / "outputs/review/task015-p1/final-v2/review.jsonl"
GAP_TSV = ROOT / "outputs/review/task015-p3/handoff-v2/gap_register.tsv"
FINAL60 = ROOT / "outputs/review/task015-p3/final/review-final-60.json"
GOLD = ROOT / "outputs/review/task015-p3/gold-v1/gold.jsonl"
EXCLUDED = ROOT / "outputs/review/task015-p3/gold-v1/excluded.jsonl"
V2_HTML = ROOT / "outputs/review/task015-p3/handoff-v2/index.html"


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inputs():
    page = PAYLOAD_HTML.read_text(encoding="utf-8")
    payload = json.loads(
        re.search(r'<script id="payload" type="application/json">(.*?)</script>', page, re.S).group(1)
    )
    cards = {r["id"]: r for r in payload["records"]}
    p1 = {}
    for line in P1_REVIEW.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            p1[r["id"]] = r
    gap = {}
    with open(GAP_TSV, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            gap[int(row["card_number"])] = row
    final = json.loads(FINAL60.read_text(encoding="utf-8"))
    final_by_id = {r["id"]: r for r in final["records"]}
    gold_ids = {json.loads(l)["id"] for l in GOLD.read_text(encoding="utf-8").splitlines() if l.strip()}
    # gold.jsonl 行结构兼容 dict 里带 id 或 card_number
    excluded = []
    for l in EXCLUDED.read_text(encoding="utf-8").splitlines():
        if l.strip():
            d = json.loads(l)
            excluded.append(d)
    excl_ids = set()
    for d in excluded:
        cid = d.get("id")
        if not cid:
            num = d.get("card_number")
            cid = next((r["id"] for r in final["records"] if r["card_number"] == num), None)
        if cid:
            excl_ids.add(cid)
    return cards, p1, gap, final, final_by_id, gold_ids, excl_ids


SOURCE_LEVEL_ZH = {
    "primary_instance_verified": "代理已核具体实例（agent，非亲核）",
    "export_procedure_supported": "有导出实验段支撑（未核原文）",
    "bibliography_or_abstract_only": "仅题录/摘要级线索",
    "conflict": "来源冲突待裁决",
    "unavailable": "原文不可得",
}

PS_TYPES = {"human_owner_checked_structure": "所有者亲核结构", "human_confirmed_without_structure_recheck": "人审确认（未亲核结构）", "agent_rechecked_structure_delegated": "所有者指示代理代填（agent 溯源）"}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def rel_path(p):
    if not p:
        return ""
    return str(p).replace("/home/ljx/FlavoRetro/", "")


def mol_block(comp):
    role = esc(comp.get("role", ""))
    label = {"reactant": "反应物", "product": "产物", "agent": "试剂/催化剂", "solute": "溶解组分", "solvent": "溶剂"}.get(role, role or "组分")
    svg = comp.get("svg") or ""
    st = comp.get("structure") or {}
    ikey = esc(st.get("inchikey", ""))
    smi = esc(st.get("canonical_smiles", ""))
    head = f'<div class="mol"><b>{label}</b>'
    if svg:
        head += svg
    head += f'<p class="small mono">{ikey}</p></div>'
    return head, smi


def build_card(num, rec, p1r, gapr, fin, flags):
    cid = rec["id"]
    ref = rec.get("reference") or {}
    title = ref.get("title") or "(无题名)"
    citation = ref.get("citation") or ""
    ref_status = ref.get("status") or ""
    drawn = rec.get("components_drawn") or []
    mols_main, smiles_extra = [], []
    for comp in drawn:
        if comp.get("role") in ("reactant", "product") and len(mols_main) < 4:
            head, _ = mol_block(comp)
            mols_main.append(head)
        else:
            st = comp.get("structure") or {}
            smiles_extra.append(f'{esc(comp.get("role", ""))}: {esc(st.get("canonical_smiles", ""))}')
    search_text = " ".join([str(num), title.lower(), citation.lower()])

    frozen = fin.get("review") or {}
    axis_note = f"结论 {esc(frozen.get('verdict', '—'))} · 审核者 {esc(frozen.get('reviewer_id', '—'))}（{PS_TYPES.get(frozen.get('review_mode', frozen.get('reviewer_type', '')), esc(frozen.get('review_mode', '')) or esc(frozen.get('reviewer_type', '')))}）"
    gold_badge = '<span class="pill gold">gold-v1</span>' if cid in flags["gold_ids"] else ('<span class="pill excl">excluded</span>' if cid in flags["excl_ids"] else "")

    src = (p1r or {}).get("source_assessment") or {}
    src_status = src.get("status", "")
    src_badge = f'<span class="pill">{esc(SOURCE_LEVEL_ZH.get(gapr["source_level"], gapr["source_level"]))}</span>'
    src_rows = []
    for s in src.get("sources", []) or []:
        bits = [f'<b>{esc(s.get("title", ""))}</b>']
        if s.get("doi"):
            bits.append(f'DOI: <a href="https://doi.org/{esc(s["doi"])}" rel="noopener">{esc(s["doi"])}</a>')
        if s.get("url") and not s.get("doi"):
            bits.append(f'<a href="{esc(s["url"])}" rel="noopener">{esc(s["url"])}</a>')
        if s.get("local_path"):
            bits.append(f'本地文件: <code>{esc(rel_path(s["local_path"]))}</code>')
        if s.get("evidence_locator"):
            bits.append(f'定位: {esc(s["evidence_locator"])}')
        src_rows.append("<li>" + " · ".join(bits) + "</li>")
    src_html = ("<ul>" + "".join(src_rows) + "</ul>") if src_rows else "<p class=small>无代理定位线索</p>"

    ya = (p1r or {}).get("conditions_yield_assessment") or {}
    if ya:
        yield_ctx = (
            f'<p><b>代理收率评估（agent，未亲核）：</b>status={esc(ya.get("status", ""))}；'
            f'reported={esc(ya.get("reported_raw", ""))}；{esc(ya.get("reason", ""))}</p>'
        )
    else:
        yield_ctx = '<p><b>代理收率评估：</b>无（需从原文确认是否有收率报道）</p>'
    needs = (p1r or {}).get("needs_user_material") or []
    needs_html = ("<p><b>待补材料提示：</b>" + esc("；".join(needs)) + "</p>") if needs else ""

    hint = (gapr.get("agent_missing_material") or "").strip()

    form = f'''<form class="review-form"><h3>你的两轴审核记录</h3>
<label>一手来源轴<select name="ps_status"><option value="">未处置</option><option value="verified_primary">已亲核原文中的该具体实例</option><option value="unavailable">原文不可得（写明尝试路线）</option><option value="deferred">本轮暂不核</option></select></label>
<label>亲核定位（DOI/专利号 + 页码、scheme/example、化合物号）<input name="ps_locator" placeholder="仅在选择“已亲核”后必填"></label>
<label>原文关键句/片段<textarea name="evidence_excerpt" placeholder="粘贴支撑该反应与收率归属的原文短句；选择“已亲核”后必填"></textarea></label>
<label>原文文件 SHA-256（可选，持有 PDF/HTML 时填写）<input name="ps_sha256" placeholder="64 位十六进制；可留空"></label>
<label>收率轴<select name="yield_status"><option value="">未处置</option><option value="verified">已在原文核对收率及产物归属</option><option value="not_reported">原文未报道收率</option><option value="deferred">本轮暂不核</option></select></label>
<label>收率核对说明（数值、单位、产物归属、原文位置）<input name="yield_value" placeholder="仅在选择“已核对”后必填"></label>
<label>备注（不可得原因、冲突、歧义等）<textarea name="notes"></textarea></label>
<button type="submit" class="primary">保存此卡</button> <span class="save-status" aria-live="polite"></span></form>'''

    details_extra = ""
    if smiles_extra:
        details_extra = "<details><summary>其余组分与 SMILES</summary><ul>" + "".join(f"<li class='small mono'>{s}</li>" for s in smiles_extra) + "</ul></details>"

    return f'''<article class="card" id="card-{num}" data-id="{cid}" data-priority="{esc(gapr["priority"])}" data-focus="{'yes' if gapr['glycoside_focus'] == 'True' else 'no'}" data-search="{esc(search_text)}">
<h2>卡 {num} <span class="pill">{esc(gapr["priority"])}</span> {'<span class="pill">糖苷重点</span>' if gapr["glycoside_focus"] == "True" else ""} {gold_badge}</h2>
<p class="small">{cid}</p>
<p><b>结构/分类轴（已冻结 gold-v1）：</b>{axis_note}</p>
<p><b>来源题名：</b>{esc(title)}</p>
<p class="small">引用：{esc(citation.strip())}（reference 状态：{esc(ref_status)}）</p>
<div class="mols">{"".join(mols_main)}</div>
{details_extra}
<p><b>来源等级：</b>{src_badge} <span class="small">{esc(src.get("reason", ""))}</span></p>
<p><b>代理定位线索（agent 上下文，不代替亲核）：</b></p>
{src_html}
{yield_ctx}
{needs_html}
{f'<p><b>缺口表提示：</b>{esc(hint)}</p>' if hint else ''}
{form}
</article>'''


APP_JS = r"""
const packet=JSON.parse(document.querySelector('#packet').textContent),cards=[...document.querySelectorAll('.card')],key='flavoretro:'+packet.packet_id;let saved={},history=[],position=0;const $=q=>document.querySelector(q);function message(s){$('#message').textContent=s}
const PS=['','verified_primary','unavailable','deferred'],YD=['','verified','not_reported','deferred'];
function valid(r){if(!PS.includes(r.ps_status)||!YD.includes(r.yield_status))throw Error('两轴取值无效');
if(r.ps_status==='verified_primary'){if(!r.ps_locator.trim())throw Error('已亲核原文须填具体定位');if(!r.evidence_excerpt.trim())throw Error('已亲核原文须粘贴原文关键句');if(r.ps_sha256.trim()&&!/^[0-9a-fA-F]{64}$/.test(r.ps_sha256.trim()))throw Error('SHA-256 须为 64 位十六进制');}
if(r.ps_status==='unavailable'&&!r.notes.trim())throw Error('原文不可得须在备注写明尝试路线与失败原因');
if(r.yield_status==='verified'){if(r.ps_status!=='verified_primary')throw Error('收率核对须先亲核原文');if(!r.yield_value.trim())throw Error('收率核对须填数值与归属');}
if(r.yield_status==='not_reported'&&r.ps_status!=='verified_primary')throw Error('判定“未报道收率”须先亲核原文');
if(r.ps_status===''&&r.yield_status==='')throw Error('两轴均未处置的卡无须保存');
if(!r.reviewer_id.trim())throw Error('请填写审核者姓名或代号');return r}
function visible(){const f=$('#filter').value,q=$('#find').value.trim().toLowerCase();return cards.filter(c=>(f==='all'||f==='pending'&&!saved[c.dataset.id]||f==='psdone'&&saved[c.dataset.id]&&saved[c.dataset.id].ps_status==='verified_primary'||c.dataset.priority===f)&&(q===''||c.dataset.search.includes(q)))}
function apply(c){const r=saved[c.dataset.id]||{},form=c.querySelector('form');for(const n of ['ps_locator','evidence_excerpt','ps_sha256','yield_value','notes'])form.elements.namedItem(n).value=r[n]||'';for(const n of ['ps_status','yield_status'])form.elements.namedItem(n).value=r[n]||'';c.querySelector('.save-status').textContent=r.ps_status||r.yield_status?'已保存 · '+r.reviewed_at:'尚未保存'}
function render(scroll=true){const list=visible();position=Math.max(0,Math.min(position,list.length-1));for(const c of cards)c.hidden=true;if(list.length){list[position].hidden=false;apply(list[position]);if(scroll)list[position].scrollIntoView({block:'start'});}$('#position').textContent=list.length?'当前 '+(position+1)+' / '+list.length+' · 卡 '+list[position].id.replace('card-',''):'此筛选下无卡片';const v=Object.values(saved);$('#progress').textContent=v.length+' / 60 已保存；一手来源亲核 '+v.filter(x=>x.ps_status==='verified_primary').length+'；收率核对 '+v.filter(x=>x.yield_status==='verified').length+'；原文不可得 '+v.filter(x=>x.ps_status==='unavailable').length}
function persist(){try{localStorage.setItem(key,JSON.stringify({saved,history,reviewer:$('#reviewer').value}));return true}catch(e){return false}}
for(const c of cards)c.querySelector('form').addEventListener('submit',e=>{e.preventDefault();try{const f=e.currentTarget,r={};for(const n of ['ps_status','yield_status'])r[n]=f.elements.namedItem(n).value;for(const n of ['ps_locator','evidence_excerpt','ps_sha256','yield_value','notes'])r[n]=f.elements.namedItem(n).value.trim();r.reviewer_id=$('#reviewer').value.trim();r.reviewed_at=new Date().toISOString();valid(r);history.push({id:c.dataset.id,before:saved[c.dataset.id]||null,after:r,changed_at:r.reviewed_at});saved[c.dataset.id]=r;const persisted=persist();message(persisted?'已保存本地草稿；请定期导出 JSON。':'浏览器无法保存本地草稿；当前内容仍在内存，请立即导出 JSON。');render()}catch(err){message(err.message)}});
for(const id of ['filter','find'])$('#'+id).addEventListener(id==='find'?'input':'change',()=>{position=0;render()});$('#prev').onclick=()=>{position--;render()};$('#next').onclick=()=>{position++;render()};$('#reviewer').addEventListener('change',persist);
function envelope(){return {schema_version:1,packet_id:packet.packet_id,source_hashes:packet.source_hashes,split:'development_exposed',status:'human_submission_pending_validation',reviewer_id:$('#reviewer').value.trim(),records:packet.cards.map(x=>({...x,review:saved[x.id]||null})),history}}
$('#export').onclick=()=>{const blob=new Blob([JSON.stringify(envelope(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='flavoretro-task015-p5-axes-review-'+packet.packet_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('已导出 '+Object.keys(saved).length+' / 60 卡；请把 JSON 文件交回给 Cano 校验。')};
$('#import').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>8*1024*1024)throw Error('文件超过 8 MB');const x=JSON.parse(await file.text());if(x.schema_version!==1||x.packet_id!==packet.packet_id||JSON.stringify(x.source_hashes)!==JSON.stringify(packet.source_hashes)||!Array.isArray(x.records)||x.records.length!==60)throw Error('审核包版本或源哈希不符');const ids=new Set(),next={};for(let i=0;i<60;i++){const r=x.records[i],expected=packet.cards[i];if(!r||r.id!==expected.id||r.card_number!==expected.card_number||r.source_sha256!==expected.source_sha256||ids.has(r.id))throw Error('卡号、来源或顺序不符');ids.add(r.id);if(r.review)next[r.id]=valid(r.review)}saved=next;history=Array.isArray(x.history)?x.history:[];$('#reviewer').value=x.reviewer_id||'';persist();position=0;render();message('已导入 '+Object.keys(saved).length+' / 60 卡。')}catch(err){message('导入失败：'+err.message)}finally{e.target.value=''}};
try{const old=JSON.parse(localStorage.getItem(key)||'null');if(old&&old.saved){saved=old.saved;history=old.history||[];$('#reviewer').value=old.reviewer||''}}catch(e){}
render(false);
"""


def gap_number(gapmap, card_id):
    for num, row in gapmap.items():
        if row["card_id"] == card_id:
            return num
    raise KeyError(card_id)


def main():
    cards, p1, gap, final, final_by_id, gold_ids, excl_ids = load_inputs()
    v2_css = re.search(r"<style>(.*?)</style>", V2_HTML.read_text(encoding="utf-8"), re.S).group(1)

    ordered = sorted(cards.values(), key=lambda r: gap_number(gap, r["id"]))

    source_hashes = {
        "task015_cards_payload_html": sha(PAYLOAD_HTML),
        "task015_p1_review_jsonl": sha(P1_REVIEW),
        "task015_p3_gap_register_tsv": sha(GAP_TSV),
        "task015_p3_review_final_60": sha(FINAL60),
        "task015_p3_gold_jsonl": sha(GOLD),
        "task015_p3_excluded_jsonl": sha(EXCLUDED),
    }
    pid_base = json.dumps(source_hashes, sort_keys=True)
    packet_id = "task015-p5-axes-handoff-v3-" + hashlib.sha256(pid_base.encode()).hexdigest()[:12]

    flags = {"gold_ids": gold_ids, "excl_ids": excl_ids}
    parts = []
    packet_cards = []
    for r in ordered:
        num = gap_number(gap, r["id"])
        cid = r["id"]
        src_sha = final_by_id[cid]["source_sha256"]
        packet_cards.append({"id": cid, "card_number": num, "source_sha256": src_sha})
        parts.append(build_card(num, r, p1.get(cid), gap[num], final_by_id[cid], flags))

    packet = {
        "schema_version": 1,
        "packet_id": packet_id,
        "source_hashes": source_hashes,
        "role": "owner review of primary_source and yield axes only; structure axis frozen in task015-p3-gold-v1",
        "split": "development_exposed",
        "stamp": STAMP,
        "cards": packet_cards,
    }
    packet_json = json.dumps(packet, ensure_ascii=False, indent=1).replace("</", "<\\/")

    page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TASK-015-P5 两轴人审：一手来源与收率（60 卡）</title>
<style>{v2_css}</style>
<style>.pill.gold{{background:#1a5c2a;color:#fff}}.pill.excl{{background:#6b1f1f;color:#fff}}.mono{{font-family:ui-monospace,monospace;word-break:break-all}}</style>
</head>
<body>
<a class="skip" href="#cards">跳到卡片</a>
<main><aside><div class="panel"><h2>两轴审核进度</h2><p id="progress">0 / 60 已保存</p><label>审核者姓名或代号<input id="reviewer" placeholder="实际审核者，不可代填"></label><label>查看范围<select id="filter"><option value="P0">P0：争议与否决</option><option value="P1">P1：其余糖苷重点</option><option value="P2">P2：其他对照</option><option value="all">全部 60 条</option><option value="pending">尚未保存</option><option value="psdone">已亲核原文</option></select></label><label>搜索卡号/题名<input id="find" placeholder="如 vitexin 或 39"></label><div class="actions"><button id="prev">上一条</button><button id="next">下一条</button></div><p id="position"></p></div><div class="panel"><h2>备份与交回</h2><button id="export" class="primary">导出审核 JSON</button><label>导入上次导出的 JSON<input id="import" type="file" accept=".json,application/json"></label><p id="message" role="status" aria-live="polite"></p><p class="small">交回导出的 JSON 文件即可。源哈希或卡号不符会被拒绝；旧卡与 gold-v1 不受影响。</p></div></aside><div><div class="panel"><h2>填写原则</h2><p>本包只审核<b>一手来源轴</b>与<b>收率轴</b>；结构/分类轴已在 task015-p3-gold-v1 冻结，卡面仅显示冻结结论。每卡先选“一手来源轴”处置：亲核了原文具体实例，就填定位并粘贴原文关键句；拿不到原文就选“原文不可得”并写明尝试路线。收率轴只有在你亲核原文之后才能选“已核对”，并写数值与产物归属。</p><p class="caution">代理定位线索与代理收率评估只是上下文，不等于亲核；黄色键仅为拓扑候选。这 60 张卡仍是 development_exposed，任何回传都不构成未见盲测。</p></div><div id="cards">{"".join(parts)}</div></div></main>
<script id="packet" type="application/json">{packet_json}</script>
<script>{APP_JS}</script>
</body>
</html>'''

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "packet.json").write_text(json.dumps(packet, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    readme = f"""# TASK-015-P5 两轴人审包（handoff-v3）

- packet_id：`{packet_id}`（由输入哈希派生）
- 冻结 stamp：{STAMP}
- 范围：60 卡的一手来源轴与收率轴。结构/分类轴已在 `task015-p3-gold-v1` 冻结，本包不重复审核。
- 用法：浏览器打开 `index.html`，先填审核者，逐卡处置两轴，导出 JSON 交回。
- 校验：导入/导出绑定 packet_id 与源哈希；卡序、卡号、来源 SHA 不符会拒绝。
- 边界：全部 60 卡 development_exposed；代理线索只是上下文；本包不构成盲测集，也不自动冻结任何轴——冻结在回传校验后按所有者决定另行执行。

## 源哈希

```json
{json.dumps(source_hashes, indent=2, sort_keys=True)}
```
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")

    manifest = {
        "task": "TASK-015-P5-A",
        "packet_id": packet_id,
        "stamp": STAMP,
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in [PAYLOAD_HTML, P1_REVIEW, GAP_TSV, FINAL60, GOLD, EXCLUDED, V2_HTML]},
        "outputs_sha256": {},
        "counts": {"cards": len(packet_cards)},
        "restriction": "development_exposed; no gold frozen by this build; agent context only",
    }
    for name in ["index.html", "packet.json", "README.md"]:
        manifest["outputs_sha256"][name] = sha(OUT / name)
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("packet_id:", packet_id)
    print("cards:", len(packet_cards))
    print("index bytes:", (OUT / "index.html").stat().st_size)


if __name__ == "__main__":
    main()

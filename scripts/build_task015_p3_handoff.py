"""Build an offline human handoff packet from frozen TASK-014/015 evidence."""
import csv
import io
import json
from collections import Counter
from html import escape
from pathlib import Path

from flavoretro.resources import sha
from flavoretro.review_cards import structure_svg
from scripts.operate import write

TASK = "TASK-015-P3"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/review/task015-p3/handoff-v2"
INPUT = ROOT / "outputs/triage/task014-final/review.jsonl"
AGENT = ROOT / "outputs/review/task015-p1/final-v2/review.jsonl"
CROSS = ROOT / "outputs/review/task015-p2/inbound-v1/card_crosswalk.tsv"


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def h(value):
    return escape(str(value or ""), quote=True)


def put(name, content):
    write(TASK, str((OUT / name).relative_to(ROOT)), content)


def locators(value, limit=4):
    items = [x.strip() for x in (value or "").split("; ") if x.strip()]
    if not items:
        return "无"
    shown = "; ".join(items[:limit])
    return shown + (f"；另有 {len(items) - limit} 行" if len(items) > limit else "")


def main():
    if OUT.exists():
        raise ValueError("immutable handoff exists; choose a new version")
    originals = read_jsonl(INPUT)
    agents = read_jsonl(AGENT)
    with CROSS.open(newline="", encoding="utf-8") as stream:
        cross = list(csv.DictReader(stream, delimiter="\t"))
    assert len(originals) == len(agents) == len(cross) == 60
    assert [x["id"] for x in originals] == [x["id"] for x in agents] == [x["card_id"] for x in cross]
    assert all(x["annotation"] and all(v is None for v in x["annotation"].values()) for x in originals)
    assert all(x["human_review_status"] == "not_performed" for x in agents)
    hashes = {"task014_review": sha(INPUT), "task015_p1_review": sha(AGENT), "task015_p2_crosswalk": sha(CROSS)}
    packet_id = "task015-p3-handoff-v2-" + hashes["task014_review"][:12]
    priorities = Counter()
    sections = []
    gap_stream = io.StringIO()
    gap_cols = ["card_number", "card_id", "priority", "glycoside_focus", "agent_decision", "source_level", "exact_structure_rows", "same_cas_rows", "same_reference_only_rows", "agent_missing_material", "user_review_question", "human_verdict", "structure_checked", "primary_source_checked", "yield_checked", "correction_or_reason", "primary_source_locator", "yield_note"]
    gap_writer = csv.DictWriter(gap_stream, fieldnames=gap_cols, delimiter="\t", lineterminator="\n")
    gap_writer.writeheader()
    identity = []
    for index, (original, agent, link) in enumerate(zip(originals, agents, cross), 1):
        assert agent["card_number"] == index == int(link["card_number"])
        row = original["input_record"]
        fields = row.get("raw", {}).get("fields", {})
        title = " ".join(str(fields.get("RXN:VAR(1):REFERENCE(1):TITLE", "")).split())
        focus = original["stratum"].startswith("glycoside_")
        urgent = agent["decision"] in ("needs_adjudication", "reject_claim") or agent["source_assessment"]["status"] in ("conflict", "unavailable")
        priority = "P0" if urgent else "P1" if focus else "P2"
        priorities[priority] += 1
        missing = agent.get("needs_user_material") or []
        if agent["decision"] == "needs_adjudication":
            question = "裁决结构/方向/步骤冲突；无法确认时选暂存疑。"
        elif agent["decision"] == "reject_claim":
            question = "确认代理否决的是哪项声明，或写明更正。"
        elif focus:
            question = "确认糖苷键在底物/产物中是否存在、本步是否成键或断键及位点。"
        else:
            question = "确认领域相关性和反应总分类；原文/收率只在实际核对后勾选。"
        gap_writer.writerow({
            "card_number": index, "card_id": agent["id"], "priority": priority,
            "glycoside_focus": focus, "agent_decision": agent["decision"],
            "source_level": agent["source_assessment"]["status"],
            "exact_structure_rows": link["exact_structure_rows"], "same_cas_rows": link["same_cas_rows"],
            "same_reference_only_rows": link["reference_only_rows"],
            "agent_missing_material": "；".join(missing), "user_review_question": question,
            "human_verdict": "", "structure_checked": "", "primary_source_checked": "",
            "yield_checked": "", "correction_or_reason": "", "primary_source_locator": "", "yield_note": "",
        })
        mols = []
        for component in row["components"]:
            mols.append('<div class="mol"><b>' + h("反应物" if component["role"] == "reactant" else "产物") + '</b>' + structure_svg(component) + '</div>')
        evidence = []
        for source in agent["source_assessment"].get("sources", []):
            url = str(source.get("url", ""))
            label = h(source.get("title", url))
            if url.startswith(("https://", "http://")):
                label = '<a href="' + h(url) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>'
            evidence.append('<li>' + label + '<small>' + h(source.get("evidence_locator", "")) + '</small></li>')
        new_evidence = (
            '<p><b>本批 RDF 严格结构：</b>' + h(link["exact_structure_rows"]) + ' 行 · '
            '<b>同 CAS 反应号：</b>' + h(link["same_cas_rows"]) + ' 行 · '
            '<b>仅文献线索：</b>' + h(link["reference_only_rows"]) + ' 行</p>'
            '<p class="small">严格结构：' + h(locators(link["exact_structure_locators"])) + '</p>'
            '<p class="small">同反应号：' + h(locators(link["same_cas_locators"])) + '</p>'
            '<p class="small">仅文献线索：' + h(locators(link["reference_only_locators"])) + '</p>'
            '<p class="caution">同题名不等于此卡具体实验；导出中的结构/反应号也不是独立原文确认。</p>'
        )
        missing_html = ''.join('<li>' + h(x) + '</li>' for x in missing) or '<li>代理审核未列额外材料；仍按各标签轴确认。</li>'
        sections.append(
            '<article class="card" id="card-' + str(index) + '" data-id="' + h(agent["id"]) +
            '" data-priority="' + priority + '" data-focus="' + ('yes' if focus else 'no') +
            '" data-search="' + h((str(index) + ' ' + title + ' ' + agent["transformation_description_zh"]).lower()) + '">'
            '<h2>卡 ' + str(index) + ' <span class="pill">' + priority + '</span> ' + ('<span class="pill">糖苷重点</span>' if focus else '') + '</h2>'
            '<p class="small">' + h(agent["id"]) + '</p><p><b>来源题名：</b>' + h(title) + '</p>'
            '<div class="mols">' + ''.join(mols) + '</div>'
            '<div class="grid"><section><h3>代理审核建议</h3><p><b>处置：</b>' + h(agent["decision"]) +
            '；<b>总分类：</b>' + h(", ".join(agent["transformation_labels"])) +
            '；<b>领域：</b>' + h(agent["domain_relevance"]) + '</p><p>' + h(agent["transformation_description_zh"]) + '</p>'
            '<p><b>糖苷变化：</b>' + h(agent["glycoside_assessment"]["bond_change"]) +
            '；<b>糖身份/位点：</b>' + h(agent["glycoside_assessment"].get("site_or_sugar", "")) + '</p>'
            '<p><b>收率说明：</b>' + h(agent["conditions_yield_assessment"].get("reason", "")) + '</p>'
            '<p><b>理由：</b>' + h(agent["decision_reason_zh"]) + '</p>'
            '<p><b>来源等级：</b>' + h(agent["source_assessment"]["status"]) + '</p>'
            '<p>' + h(agent["source_assessment"].get("reason", "")) + '</p><ul>' + ''.join(evidence) + '</ul>'
            '<p><a href="../../task015-p1/final-v2/index.html#card-' + str(index) + '" target="_blank" rel="noopener">打开完整代理审核卡</a></p></section>'
            '<section><h3>本批新增材料</h3>' + new_evidence + '<h3>你需要判断</h3><p>' + h(question) + '</p><ul>' + missing_html + '</ul></section></div>'
            '<form class="review-form"><h3>你的审核记录</h3>'
            '<label>结论<select name="verdict" required><option value="">请选择</option><option value="agree">同意代理判断</option><option value="revise">更正代理判断</option><option value="unresolved">暂存疑，待补证</option><option value="exclude">排除该声明/实例</option></select></label>'
            '<label class="check"><input type="checkbox" name="structure_checked">我核对了结构、方向及相应分类/糖苷连接；这些轴可供后续逐项判定</label>'
            '<label class="check"><input type="checkbox" name="source_checked">我对照了一手原文中的这个具体实例（需填写下方定位）</label>'
            '<label class="check"><input type="checkbox" name="yield_checked">我核对了该实例的条件/收率归属（需填写说明）</label>'
            '<label>更正或暂存疑/排除理由<textarea name="correction" placeholder="若与代理不同，写明正确类别、糖苷键变化和依据；无法判定写具体缺口"></textarea></label>'
            '<label>一手原文具体定位<input name="source_locator" placeholder="DOI/专利 + 页码、scheme/example、化合物号；仅勾选核对原文时填写"></label>'
            '<label>条件/收率核对说明<input name="yield_note" placeholder="数值、单位、产物归属与原文位置；未核对可留空"></label>'
            '<button type="submit" class="primary">保存此卡审核</button> <span class="save-status" aria-live="polite"></span></form></article>'
        )
        identity.append({"id": agent["id"], "card_number": index, "source_sha256": row["source_sha256"]})
    payload = {"schema_version": 1, "packet_id": packet_id, "source_hashes": hashes, "cards": identity, "role": "human_review_handoff_pending", "split": "development_exposed"}
    payload_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TASK-015 人工复核包</title><style>
:root{--ink:#16353b;--muted:#586e72;--line:#cbd9d9;--bg:#f3f6f5;--accent:#14645e}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}header{background:#123f45;color:white;padding:22px max(18px,calc((100vw - 1240px)/2))}h1{font-size:26px;margin:0 0 5px}header p{margin:6px 0}main{max-width:1280px;margin:18px auto;padding:0 16px;display:grid;grid-template-columns:260px minmax(0,1fr);gap:18px}.panel,.card{background:white;border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:16px}aside{position:sticky;top:12px;align-self:start}h2{font-size:21px;margin:0 0 10px}h3{font-size:17px;margin:12px 0 7px}p{margin:8px 0;overflow-wrap:anywhere}.small,small{font-size:13px;color:var(--muted);display:block;overflow-wrap:anywhere}.pill{font-size:12px;border-radius:16px;background:#dceae7;padding:3px 8px}.caution{background:#fff3d7;border-left:4px solid #b27b18;padding:9px}.mols,.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.mol{border:1px solid var(--line);padding:7px;min-width:0;border-radius:7px}.mol svg{width:100%;height:auto;max-height:230px}label{display:block;margin:10px 0;font-size:14px}input:not([type=checkbox]),select,textarea,button{font:inherit;border:1px solid #9db3b4;border-radius:6px;padding:9px;min-height:42px;max-width:100%;color:var(--ink)}input:not([type=checkbox]),select,textarea{width:100%;background:white}textarea{min-height:80px}.check{display:flex;gap:9px;align-items:start}.check input{margin-top:5px;min-width:18px;min-height:18px}button{cursor:pointer;background:white}button.primary{background:var(--accent);color:white}button:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,a:focus-visible{outline:3px solid #d08515;outline-offset:2px}.actions{display:flex;gap:8px;flex-wrap:wrap}.actions button{flex:1}a{color:#12645f}.card[hidden]{display:none}ul{padding-left:20px}.save-status{color:var(--accent);font-weight:600}#message{min-height:30px;color:#a22d25}footer{max-width:1280px;margin:auto;padding:20px;font-size:13px;color:var(--muted)}@media(max-width:900px){main{display:block}aside{position:static}.mols,.grid{grid-template-columns:1fr}}@media(max-width:500px){header{padding:18px}.panel,.card{padding:14px}}
</style></head><body><header><h1>TASK-015 · 60 卡人工复核</h1><p>先看 P0 争议，再看 P1 糖苷重点，最后处理 P2 对照。代理建议可见；请以你实际检查的结构和来源作决定。</p><p>本页离线运行。保存的是浏览器草稿；请经常导出 JSON。提交后仍由 Cano 校验与补证，不能仅凭导出或总体确认自动生成 gold。</p></header><main><aside><div class="panel"><h2>审核进度</h2><p id="progress">0 / 60 已保存</p><label>审核者姓名或代号<input id="reviewer" placeholder="实际审核者，不可代填"></label><label>查看范围<select id="filter"><option value="P0">P0：争议与否决</option><option value="P1">P1：其余糖苷重点</option><option value="P2">P2：其他对照</option><option value="all">全部 60 条</option><option value="pending">尚未保存</option></select></label><label>搜索卡号/题名<input id="find" placeholder="如 vitexin 或 39"></label><div class="actions"><button id="prev">上一条</button><button id="next">下一条</button></div><p id="position"></p></div><div class="panel"><h2>备份与交回</h2><button id="export" class="primary">导出审核 JSON</button><label>导入上次导出的 JSON<input id="import" type="file" accept=".json,application/json"></label><p id="message" role="status" aria-live="polite"></p><p class="small">交回导出的 JSON 文件即可。源哈希或卡号不符会被拒绝；无需修改原 RDF 或旧卡片。</p></div></aside><div><div class="panel"><h2>填写原则</h2><p>每卡先选结论。三个复选框分别表示你亲自核对过结构/类别、一手原文具体实例、条件/收率；未核对的轴请留空。若更正、暂存疑或排除，请写理由。确认所有 60 卡都已作处置之后导出 JSON。</p><p class="caution">“同意代理判断”不等于“原文已核对”。只有填写的一手原文定位和实际审核范围通过后续校验，相关轴才可能进入开发 gold。不可把这 60 张已暴露卡称为未见盲测。</p></div><div id="cards">__CARDS__</div></div></main><footer>受限数据库衍生内容仅供项目本地审核，不公开分发。原始导出、TASK-014 样本、TASK-015-P1 代理审核保持只读。</footer><script id="packet" type="application/json">__PAYLOAD__</script><script>
const packet=JSON.parse(document.querySelector('#packet').textContent),cards=[...document.querySelectorAll('.card')],byId=new Map(cards.map(c=>[c.dataset.id,c])),key='flavoretro:'+packet.packet_id;let saved={},history=[],position=0;const $=q=>document.querySelector(q);function message(s){$('#message').textContent=s}function valid(r){if(!r||!['agree','revise','unresolved','exclude'].includes(r.verdict))throw Error('请选择结论');if(['revise','unresolved','exclude'].includes(r.verdict)&&!r.correction.trim())throw Error('更正、暂存疑或排除须写理由');if(r.source_checked&&!r.source_locator.trim())throw Error('勾选原文核对须填具体定位');if(r.yield_checked&&(!r.source_checked||!r.yield_note.trim()))throw Error('收率核对须先核原文并填归属说明');if(!r.reviewer_id.trim())throw Error('请填写审核者姓名或代号');return r}function visible(){const f=$('#filter').value,q=$('#find').value.trim().toLowerCase();return cards.filter(c=>(f==='all'||f==='pending'&&!saved[c.dataset.id]||c.dataset.priority===f)&&(q===''||c.dataset.search.includes(q)))}function apply(c){const r=saved[c.dataset.id]||{},form=c.querySelector('form');for(const n of ['verdict','correction','source_locator','yield_note'])form.elements.namedItem(n).value=r[n]||'';for(const n of ['structure_checked','source_checked','yield_checked'])form.elements.namedItem(n).checked=!!r[n];c.querySelector('.save-status').textContent=r.verdict?'已保存 · '+r.reviewed_at:'尚未保存'}function render(scroll=true){const list=visible();position=Math.max(0,Math.min(position,list.length-1));for(const c of cards)c.hidden=true;if(list.length){list[position].hidden=false;apply(list[position]);if(scroll)list[position].scrollIntoView({block:'start'});}$('#position').textContent=list.length?'当前 '+(position+1)+' / '+list.length+' · 卡 '+list[position].id.replace('card-',''):'此筛选下无卡片';$('#progress').textContent=Object.keys(saved).length+' / 60 已保存；结构核对 '+Object.values(saved).filter(x=>x.structure_checked).length+'；原文核对 '+Object.values(saved).filter(x=>x.source_checked).length}function persist(){try{localStorage.setItem(key,JSON.stringify({saved,history,reviewer:$('#reviewer').value}));return true}catch(e){return false}}for(const c of cards)c.querySelector('form').addEventListener('submit',e=>{e.preventDefault();try{const f=e.currentTarget,r={verdict:f.elements.namedItem('verdict').value,structure_checked:f.elements.namedItem('structure_checked').checked,source_checked:f.elements.namedItem('source_checked').checked,yield_checked:f.elements.namedItem('yield_checked').checked,correction:f.elements.namedItem('correction').value.trim(),source_locator:f.elements.namedItem('source_locator').value.trim(),yield_note:f.elements.namedItem('yield_note').value.trim(),reviewer_id:$('#reviewer').value.trim(),reviewed_at:new Date().toISOString()};valid(r);history.push({id:c.dataset.id,before:saved[c.dataset.id]||null,after:r,changed_at:r.reviewed_at});saved[c.dataset.id]=r;const persisted=persist();message(persisted?'已保存本地草稿；请定期导出 JSON。':'浏览器无法保存本地草稿；当前内容仍在内存，请立即导出 JSON。');render()}catch(err){message(err.message)}});for(const id of ['filter','find'])$('#'+id).addEventListener(id==='find'?'input':'change',()=>{position=0;render()});$('#prev').onclick=()=>{position--;render()};$('#next').onclick=()=>{position++;render()};$('#reviewer').addEventListener('change',persist);function envelope(){return {schema_version:1,packet_id:packet.packet_id,source_hashes:packet.source_hashes,split:'development_exposed',status:'human_submission_pending_validation',reviewer_id:$('#reviewer').value.trim(),records:packet.cards.map(x=>({...x,review:saved[x.id]||null})),history}}$('#export').onclick=()=>{const blob=new Blob([JSON.stringify(envelope(),null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='flavoretro-task015-human-review-'+packet.packet_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);message('已导出 '+Object.keys(saved).length+' / 60 卡；请把 JSON 文件交给 Cano 校验。')};$('#import').onchange=async e=>{try{const file=e.target.files[0];if(!file)return;if(file.size>8*1024*1024)throw Error('文件超过 8 MB');const x=JSON.parse(await file.text());if(x.schema_version!==1||x.packet_id!==packet.packet_id||JSON.stringify(x.source_hashes)!==JSON.stringify(packet.source_hashes)||!Array.isArray(x.records)||x.records.length!==60)throw Error('审核包版本或源哈希不符');const ids=new Set(),next={};for(let i=0;i<60;i++){const r=x.records[i],expected=packet.cards[i];if(!r||r.id!==expected.id||r.card_number!==expected.card_number||r.source_sha256!==expected.source_sha256||ids.has(r.id))throw Error('卡号、来源或顺序不符');ids.add(r.id);if(r.review)next[r.id]=valid(r.review)}saved=next;history=Array.isArray(x.history)?x.history:[];$('#reviewer').value=x.reviewer_id||'';persist();position=0;render();message('已导入 '+Object.keys(saved).length+' / 60 卡。')}catch(err){message('导入失败：'+err.message)}finally{e.target.value=''}};try{const old=JSON.parse(localStorage.getItem(key)||'null');if(old&&old.saved){saved=old.saved;history=old.history||[];$('#reviewer').value=old.reviewer||''}}catch(e){}render(false);
</script></body></html>""".replace("__CARDS__", "".join(sections)).replace("__PAYLOAD__", payload_json)
    OUT.mkdir(parents=True)
    put("index.html", html)
    put("gap_register.tsv", gap_stream.getvalue())
    put("packet.json", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    guide = """# TASK-015 人工复核包使用说明

1. 双击 `index.html`。先填左侧的实际审核者姓名/代号，按 P0 → P1 → P2 查看 60 卡。每卡有原结构、代理判断、来源等级、新 RDF 的严格连接与仅文献线索，并有完整代理卡链接。
2. 每卡选择「同意代理判断 / 更正 / 暂存疑 / 排除」。只勾选亲自核对过的轴；勾选具体原文必须填 DOI/专利号和页码/实例/化合物号，勾选收率还须填归属说明。更正/暂存疑/排除须写理由。点击「保存此卡审核」。
3. 浏览器草稿可能随文件地址或浏览器改变而失效；定期点「导出审核 JSON」。完成 60/60 后把导出的 JSON 放在 `/home/ljx/FlavoRetro/data/inbox/scifinder/task015-user/` 并告诉 Cano 路径。可随时用「导入」恢复同版本备份。**不要改动原 RDF、旧卡片或手工修改 JSON 身份字段。**
4. `gap_register.tsv` 便于按优先级和卡号查漏，也有空白人工列；主要交接载荷是页面导出的 JSON。若无法核实，请明确选暂存疑并说明原因，不必为了凑 gold 补猜。

此包只有代理建议和空白人审栏。审核者提交之后由 Cano 校验、补证、处理争议；最后再由所有者确认全部处理。`development_exposed` 保持不变，任何文件生成或勾选都不自动成为 gold/production/盲测。
"""
    put("README.md", guide)
    manifest = {"task": TASK, "packet_id": packet_id, "cards": 60, "glycoside_focus": 30, "priorities": dict(priorities), "source_hashes": hashes, "outputs": {p.name: sha(p) for p in OUT.iterdir() if p.is_file()}, "human_review_status": "not_performed", "restriction": "local restricted database-derived handoff; no Git or public distribution"}
    put("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"packet_id": packet_id, "priorities": priorities, "outputs": list(manifest["outputs"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

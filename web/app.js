/* FlavoRetro 浏览器工作台：路线探索 / 资源与证据 / 文献教学 / 项目状态。
 * 纯原生 JS，无构建步骤。措辞纪律：候选不代表可执行，未知保持未知。
 */
"use strict";

// ---------- 基础工具 ----------
const $ = id => document.getElementById(id);
let lastResult = null, offset = 0;
let teachingCache = null;    // /api/teaching 惰性缓存（Promise），失败时 resolves 为 null
let literatureCache = null;  // /api/literature-teaching 惰性缓存（Promise）

async function api(path, options) {
    const response = await fetch(path, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || data.error?.message || data.error || '请求失败');
    return data;
}
function text(tag, value, cls) {
    const el = document.createElement(tag);
    el.textContent = value;
    if (cls) el.className = cls;
    return el;
}
function div(cls) { const el = document.createElement('div'); if (cls) el.className = cls; return el; }
function chip(value, cls) { return text('span', value, 'chip' + (cls ? ' ' + cls : '')); }
function fixed(value, digits = 3) { const n = Number(value); return Number.isFinite(n) ? n.toFixed(digits) : '—'; }
function kv(label, value) {
    const p = div('kv');
    p.append(text('b', label + '：'), document.createTextNode(String(value)));
    return p;
}

// ---------- 中文标签映射（移植自旧项目，按新后端枚举收敛） ----------
const CLOSURE_ROUTE_ZH = { surrogate: '候选闭合 · 无独立证据', partial: '部分路线 · 未闭合' };
const CLOSURE_LEAF_ZH = { surrogate: '候选闭合 · 无独立证据', partial: '未闭合' };
const EVIDENCE_BASIS_ZH = { unreviewed_candidate_stock: '未审候选库存', unresolved: '未解决' };
const STRUCTURE_STATUS_ZH = { parsed: '结构解析通过', parse_failure: '结构解析失败', missing: '结构缺失' };
const HAZARD_UNKNOWN = 'unknown_not_certified_safe';
const LIMITATIONS_ZH = {
    'No independently reviewed production templates or stock': '没有经独立审定的生产模板或库存。',
    'No experimental feasibility certification': '无实验可行性认证。',
    'No independent forward model; filter rejects only explicit disproved replay': '无独立正向模型；过滤器仅排除明确被证伪的回放。',
    'Unknown hazards and conditions remain unknown': '未知的危险与条件保持未知。',
    'Native baseline does not share optimized node ceiling': '原生基线不共享优化版节点上限。'
};
const TARGET_NAMES_ZH = {
    hesperidin: '橙皮苷', naringin: '柚皮苷', neohesperidin: '新橙皮苷', narirutin: '柚皮芸香苷',
    rutin: '芦丁', quercitrin: '槲皮苷', hesperetin: '橙皮素', naringenin: '柚皮素',
    quercetin: '槲皮素', kaempferol: '山奈酚', luteolin: '木犀草素', chalcone: '查尔酮'
};
const MODE_ZH = { quick: '快速探索', balanced: '平衡 · 两阶段', strict: '深入探索' };
// 文献教学页字段标签（值原样呈现，仅字段名中文化）
const SCOPE_ZH = {
    publisher_full_text: '出版方全文', pubmed_abstract: 'PubMed 摘要', full_text: '全文',
    publisher_abstract: '出版方摘要', publisher_abstract_and_review_route: '出版方摘要与综述路线',
    publisher_record: '出版方记录', open_full_text: '开放全文', primary_full_text: '一手全文',
    open_full_text_historical_summary_not_template_activated: '开放全文（历史综述，未激活模板）'
};
const CLAIM_STATUS_ZH = {
    legacy_registry_summary_pending_primary_source_revalidation: '历史登记摘要 · 待一手来源复核',
    machine_extracted_pending_human_review: '机器抽取 · 待人工复核'
};
const HAZARD_FLAG_ZH = {
    heavy_metal_salt: '重金属盐', strong_lewis_acid: '强路易斯酸', oxidant: '氧化剂',
    hydrogenation: '氢化', chlorinated_solvent: '氯代溶剂', reproductive_hazard_solvent: '生殖毒性溶剂',
    biocatalytic_low_intrinsic_hazard: '生物催化 · 固有危险低', copper_salt: '铜盐',
    corrosive_base: '腐蚀性碱', nanomaterial_handling: '纳米材料操作',
    activated_glycosyl_halide: '活化糖基卤化物', whole_cell_engineering: '全细胞工程',
    conditions_not_reported_in_abstract: '摘要未报告条件',
    conditions_require_full_text_review: '条件需全文复核',
    conditions_require_original_1943_source: '条件需查 1943 年原始来源'
};
const CLAIM_POLICY_ZH = {
    teaching_not_sop: '教学用途 · 非操作规程',
    machine_extraction_not_primary_evidence: '机器抽取 · 非一手证据',
    production_lesson_gate: '生产课程准入门槛'
};

// ---------- tab 切换 ----------
document.querySelectorAll('[data-tab]').forEach(button => button.onclick = () => {
    document.querySelectorAll('.page').forEach(p => p.hidden = p.id !== button.dataset.tab);
    document.querySelectorAll('[data-tab]').forEach(b => b.classList.toggle('active', b === button));
    if (button.dataset.tab === 'resources') loadRecords();
    if (button.dataset.tab === 'literature') loadLiterature();
    if (button.dataset.tab === 'governance') loadStatus();
});

// ---------- 搜索表单 ----------
$('preview').onclick = () => { $('molecule').src = '/api/molecule?smiles=' + encodeURIComponent($('smiles').value); };
$('preset').onchange = () => { if ($('preset').value) { $('smiles').value = $('preset').value; $('preview').click(); } };

// 教学解释模式开关：默认开，状态存 localStorage
const TEACHING_KEY = 'flavoretro.teaching';
$('teaching').checked = localStorage.getItem(TEACHING_KEY) !== '0';
$('teaching').onchange = () => {
    localStorage.setItem(TEACHING_KEY, $('teaching').checked ? '1' : '0');
    if (lastResult) render(lastResult); // 重渲染当前结果以切换教学块显隐
};

function fetchTeaching() {
    if (!teachingCache) teachingCache = api('/api/teaching').catch(() => null);
    return teachingCache;
}

// ---------- 路线解读 ----------
function treeView(node) {
    const el = div(node.type === 'reaction' ? 'tree reaction' : 'tree');
    if (node.type === 'mol') {
        const img = document.createElement('img');
        img.src = '/api/molecule?smiles=' + encodeURIComponent(node.smiles);
        img.alt = '路线中的分子结构';
        img.loading = 'lazy';
        img.onerror = () => { img.replaceWith(text('p', '结构图不可用')); };
        el.append(img, text('code', node.smiles));
        if (node.closure) el.append(text('span', CLOSURE_LEAF_ZH[node.closure] || node.closure, 'tag'));
    } else el.append(text('span', '↓ 预测反应 · 条件与可行性未确认'));
    for (const child of node.children || []) el.append(treeView(child));
    return el;
}

// 遍历树收集末端 mol 叶节点
function collectLeaves(node, found = []) {
    const children = node.children || [];
    if (node.type === 'mol' && !children.length) found.push(node);
    for (const child of children) collectLeaves(child, found);
    return found;
}

// 自根广度优先收集反应节点（第 1 步最接近目标分子）
function collectReactions(tree) {
    const found = [], queue = [{ node: tree, depth: 0 }];
    while (queue.length) {
        const { node, depth } = queue.shift();
        if (node.type === 'reaction') found.push({ node, depth });
        for (const child of node.children || []) queue.push({ node: child, depth: depth + 1 });
    }
    return found;
}

function hazardLabel(hazard) {
    if (!hazard || hazard === HAZARD_UNKNOWN) return { label: '未知，未经安全认证', cls: 'neutral' };
    return { label: '危险标记：' + hazard, cls: 'hazard' };
}

function leafCard(leaf) {
    const card = div('leaf-card');
    const img = document.createElement('img');
    img.src = '/api/molecule?smiles=' + encodeURIComponent(leaf.smiles);
    img.alt = '末端原料结构';
    img.loading = 'lazy';
    img.onerror = () => { img.replaceWith(text('p', '结构图不可用（SMILES 未通过解析）')); };
    card.append(img, text('code', leaf.smiles));
    const row = div('chips');
    row.append(text('span', CLOSURE_LEAF_ZH[leaf.closure] || leaf.closure || '未标注', 'tag' + (leaf.closure === 'partial' ? ' partial' : '')));
    row.append(text('span', EVIDENCE_BASIS_ZH[leaf.evidence_basis] || leaf.evidence_basis || '未标注', 'tag partial'));
    const hz = hazardLabel(leaf.hazard);
    row.append(text('span', hz.label, 'tag ' + hz.cls));
    card.append(row);
    const check = leaf.structure_check || {};
    let checkText = STRUCTURE_STATUS_ZH[check.status] || check.status || '未检查';
    if (check.unspecified_stereo) checkText += ` · 未指定立体中心 ${check.unspecified_stereo} 个`;
    card.append(kv('结构检查', checkText));
    return card;
}

// 按 classification 在教学数据中查条目；查不到回退 default 并注明
function teachingEntry(classification, teaching) {
    if (teaching && classification && teaching.classifications && teaching.classifications[classification])
        return { entry: teaching.classifications[classification], fallback: false };
    return { entry: teaching ? teaching.default : null, fallback: true };
}

function teachingBlock(meta, teaching) {
    const { entry, fallback } = teachingEntry(meta && meta.classification, teaching);
    const block = div('teaching-block');
    if (!entry) {
        block.append(text('p', '教学数据暂不可用（/api/teaching 未就绪），仅显示模板元数据。'));
        return block;
    }
    block.append(text('h4', '教学说明 · ' + (entry.label_zh || '通用说明') + (fallback ? '（未匹配到专属条目，以下为通用说明）' : '')));
    const dl = document.createElement('dl');
    const add = (label, values) => {
        if (values == null || (Array.isArray(values) && !values.length)) return;
        dl.append(text('dt', label));
        const dd = document.createElement('dd');
        if (Array.isArray(values)) {
            const ul = document.createElement('ul');
            for (const item of values) ul.append(text('li', item));
            dd.append(ul);
        } else dd.textContent = values;
        dl.append(dd);
    };
    add('反应原理', entry.principle_zh);
    add('常见条件', entry.typical_conditions_zh);
    add('风险提示', entry.risk_notes_zh);
    add('证据边界', entry.evidence_boundary_zh);
    const sources = (entry.source_ids || []).map(id => [id, teaching.sources && teaching.sources[id]]).filter(([, s]) => s);
    if (sources.length) {
        dl.append(text('dt', '教学依据'));
        const dd = document.createElement('dd');
        dd.className = 'sources';
        for (const [id, s] of sources) {
            const a = document.createElement('a');
            a.href = s.url || (s.doi ? 'https://doi.org/' + s.doi : '#');
            a.target = '_blank';
            a.rel = 'noopener';
            a.textContent = `${id} · ${s.title}`;
            dd.append(a);
        }
        dl.append(dd);
    }
    block.append(dl);
    return block;
}

function stepCard(item, stepNo, teaching) {
    const meta = item.node.metadata || {};
    const card = div('step-card');
    card.append(text('h3', `第 ${stepNo} 步 · 预测反应（条件与可行性未确认）`));
    const template = meta.template || (meta.template_hash ? meta.template_hash.slice(0, 16) + '…' : (meta.template_code || '—'));
    card.append(kv('模板号', template));
    const { entry } = teachingEntry(meta.classification, teaching);
    const family = entry && meta.classification ? `${entry.label_zh}（${meta.classification}）` : (meta.classification || '未分类');
    card.append(kv('反应家族', family));
    if (meta.policy_name) card.append(kv('策略', `${meta.policy_name} · 概率 ${fixed(meta.policy_probability)}` + (meta.policy_probability_rank != null ? ` · 候选排名第 ${meta.policy_probability_rank}` : '')));
    if (meta.library_occurence != null) card.append(kv('语料出现次数', meta.library_occurence));
    if (meta.mapped_reaction_smiles) card.append(text('code', meta.mapped_reaction_smiles, 'mapped'));
    if (teaching) card.append(teachingBlock(meta, teaching));
    return card;
}

function renderRunMeta(result) {
    const meta = div();
    const card = div('meta-card');
    card.append(text('div', `实时运行 ${result.run_id} · ${result.created_at || ''} · 状态 ${result.status}`));
    card.append(text('div', `候选路线 ${result.candidate_count} · 展示 ${result.routes.length} · release_ready: ${result.release_ready}（非实验验证 · 候选仅供探索）`));
    for (const phase of result.phases || []) {
        const b = phase.budget || {};
        const budget = `预算（深度 ${b.depth} · 分支 ${b.branching} · 节点 ${b.nodes} · 迭代 ${b.iterations} · ${b.seconds} 秒）`;
        const stop = phase.profiling && phase.profiling.stop_reason ? ` · 停止原因 ${phase.profiling.stop_reason}` : '';
        card.append(text('div', `阶段 ${phase.index + 1} · seed ${phase.seed} · ${budget} · ${phase.node_count} 节点 · ${Number(phase.search_seconds).toFixed(2)} s（墙钟 ${Number(phase.wall_seconds).toFixed(2)} s）· ${phase.engine_class}${stop}`));
    }
    if (result.limitations && result.limitations.length) {
        card.append(text('div', '已知局限：'));
        const ul = document.createElement('ul');
        ul.className = 'limitations';
        for (const item of result.limitations) {
            const li = document.createElement('li');
            li.append(document.createTextNode(LIMITATIONS_ZH[item] || item));
            if (LIMITATIONS_ZH[item]) li.append(text('small', ' （原始记录：' + item + '）'));
            ul.append(li);
        }
        card.append(ul);
    }
    meta.append(card);
    $('run-meta').replaceChildren(meta);
}

async function render(result) {
    lastResult = result;
    $('download').hidden = false;
    renderRunMeta(result);
    let teaching = null;
    if ($('teaching').checked) teaching = await fetchTeaching();
    if (lastResult !== result) return; // 期间又发起了新搜索，放弃本次渲染
    $('routes').replaceChildren();
    if (!result.routes.length) {
        $('routes').append(text('p', '本预算没有提取出路线。可调整预算后重新搜索。', 'empty'));
        return;
    }
    for (const [index, route] of result.routes.entries()) $('routes').append(routeCard(route, index, teaching));
}

function routeCard(route, index, teaching) {
    const card = document.createElement('article');
    card.className = 'card route';
    const heading = div('route-head');
    heading.append(text('h2', `路线 ${index + 1}`));
    heading.append(text('span', CLOSURE_ROUTE_ZH[route.closure] || route.closure, 'tag' + (route.closure === 'partial' ? ' partial' : '')));
    heading.append(text('small', route.route_id.slice(0, 12)));
    heading.append(text('span', `${route.steps} 步 · 暂定分数 ${route.score}`, 'tag neutral'));
    card.append(heading);

    // 评分构成：分项与公式，注明 score_status 含义
    const c = route.cost || {};
    const cost = div('cost');
    cost.append(text('b', '评分构成 '));
    cost.append(document.createTextNode(`步骤 ${c.steps} · 未解决原料 ${c.unresolved_materials} · 已知危险 ${c.known_hazards} · 未指定立体 ${c.unspecified_leaf_stereo}`));
    cost.append(text('span', `score = ${c.steps} + 2×${c.unresolved_materials} + 5×${c.known_hazards} + ${c.unspecified_leaf_stereo} = ${route.score}`, 'formula'));
    cost.append(text('span', `score_status: ${route.score_status} —— 暂定成本，越低越好；仅用于候选排序，不构成证据或可行性评价。`, 'formula'));
    card.append(cost);
    card.append(text('p', `evidence_closed: ${route.evidence_closed} · actionable: ${route.actionable} · release_ready: false —— 非实验验证，候选仅供探索。`, 'fact-line'));

    // 末端原料证据
    card.append(text('h3', '末端原料证据'));
    const leaves = collectLeaves(route.tree);
    if (!leaves.length) card.append(text('p', '本路线无末端原料节点。', 'note'));
    const grid = div('leaf-grid');
    for (const leaf of leaves) grid.append(leafCard(leaf));
    card.append(grid);

    // 逐步反应卡片（教学块随开关显隐）
    card.append(text('h3', '逐步反应'));
    if (teaching) {
        const scope = teaching.scope_note_zh || teaching.scope_note;
        if (scope) card.append(text('p', '教学模式：' + scope, 'teaching-note'));
    }
    const reactions = collectReactions(route.tree);
    if (!reactions.length) card.append(text('p', '本路线不含反应步骤。', 'note'));
    reactions.forEach((item, i) => card.append(stepCard(item, i + 1, teaching)));

    const details = document.createElement('details');
    details.append(text('summary', '查看路线结构'), treeView(route.tree));
    card.append(details);
    return card;
}

$('search-form').onsubmit = async event => {
    event.preventDefault();
    $('preview').click();
    $('submit').disabled = true;
    $('message').textContent = '正在执行新的 MCTS 搜索，请保持页面打开…';
    const req = { smiles: $('smiles').value, mode: $('mode').value, seed: Number($('seed').value), candidate_stock: $('candidate').checked };
    for (const name of ['seconds', 'iterations']) if ($(name).value !== '') req[name] = Number($(name).value);
    try {
        const result = await api('/api/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) });
        await render(result);
        $('message').textContent = '本次实时搜索完成。结果仅支持计算探索。';
    } catch (error) {
        $('message').textContent = '搜索失败：' + error.message;
    } finally {
        $('submit').disabled = false;
    }
};
$('download').onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(lastResult, null, 2)], { type: 'application/json' }));
    a.download = lastResult.run_id + '.json';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};

// ---------- 文献教学页 ----------
function policyBanner(policy) {
    const banner = div('banner');
    banner.append(text('p', '', ''));
    banner.firstChild.textContent = '边界声明（来自 claim_policy，原样呈现）：';
    let known = 0;
    for (const [key, value] of Object.entries(policy || {})) {
        if (key === 'production_lesson_gate') {
            banner.append(text('p', `${CLAIM_POLICY_ZH[key]}：${value}（未通过该门槛的课程不进入生产）`));
        } else if (CLAIM_POLICY_ZH[key]) {
            banner.append(text('p', `${CLAIM_POLICY_ZH[key]}：${value}`));
        } else {
            banner.append(text('p', `${key}: ${JSON.stringify(value)}`));
            continue;
        }
        known++;
    }
    if (!known) banner.append(text('p', '（未提供 claim_policy 字段）'));
    return banner;
}

function kvTable(rows) {
    const table = document.createElement('table');
    table.className = 'kv-table';
    for (const [label, value] of rows) {
        if (value == null || (Array.isArray(value) && !value.length) || value === '') continue;
        const tr = document.createElement('tr');
        tr.append(text('th', label));
        const td = document.createElement('td');
        if (Array.isArray(value)) {
            const box = div('chips');
            for (const item of value) box.append(chip(item));
            td.append(box);
        } else if (value instanceof Node) td.append(value);
        else td.textContent = value;
        tr.append(td);
        table.append(tr);
    }
    return table;
}

// 递归渲染嵌套条件对象（机器抽取原文，键值原样呈现）
function nestedTable(obj) {
    const table = document.createElement('table');
    table.className = 'kv-table';
    for (const [key, value] of Object.entries(obj || {})) {
        const tr = document.createElement('tr');
        tr.append(text('th', key));
        const td = document.createElement('td');
        if (value && typeof value === 'object') td.append(nestedTable(value));
        else td.textContent = String(value);
        tr.append(td);
        table.append(tr);
    }
    return table;
}

function paperCard(paper) {
    const card = div('paper-card');
    const title = paper.source_url ? document.createElement('a') : document.createElement('span');
    title.textContent = paper.title || paper.paper_id;
    if (paper.source_url) { title.href = paper.source_url; title.target = '_blank'; title.rel = 'noopener'; }
    const h3 = document.createElement('h3');
    h3.append(title);
    card.append(h3);
    card.append(text('p', [paper.paper_id, paper.year, paper.journal].filter(x => x != null && x !== '').join(' · '), 'meta'));
    const rows = [
        ['DOI', paper.doi],
        ['证据范围', paper.evidence_scope ? (SCOPE_ZH[paper.evidence_scope] ? `${SCOPE_ZH[paper.evidence_scope]}（${paper.evidence_scope}）` : paper.evidence_scope) : null],
        ['claim_status', paper.claim_status ? (CLAIM_STATUS_ZH[paper.claim_status] ? `${CLAIM_STATUS_ZH[paper.claim_status]}（${paper.claim_status}）` : paper.claim_status) : null],
        ['路线目标', paper.route_targets],
        ['关键步骤', paper.key_step],
        ['报告条件', paper.reported_conditions]
    ];
    card.append(kvTable(rows));
    if (paper.hazard_flags && paper.hazard_flags.length) {
        const tr_box = div('chips');
        for (const flag of paper.hazard_flags) tr_box.append(chip(HAZARD_FLAG_ZH[flag] ? `${HAZARD_FLAG_ZH[flag]}（${flag}）` : flag, 'warn'));
        card.append(kvTable([['危险标记', tr_box]]));
    }
    return card;
}

function lessonCard(lesson) {
    const card = div('lesson-card');
    card.append(text('h3', `${lesson.title_zh || lesson.title_en || lesson.reaction_id}（${lesson.reaction_id}）`));
    card.append(text('p', [lesson.paper_id, lesson.doi, lesson.record_status].filter(Boolean).join(' · '), 'meta'));
    const rows = [
        ['反应原理', lesson.principle_zh],
        ['证据边界', lesson.evidence_boundary_zh],
        ['来源定位', lesson.source_locators],
        ['structure_status / production_ready', `structure_status: ${lesson.structure_status} · production_ready: ${lesson.production_ready}（未通过人工结构复核，不进入生产）`]
    ];
    card.append(kvTable(rows));
    if (lesson.conditions) {
        card.append(text('p', '抽取条件（机器抽取，非一手证据）：', 'meta'));
        card.append(nestedTable(lesson.conditions));
    }
    return card;
}

async function loadLiterature() {
    if (!literatureCache) literatureCache = api('/api/literature-teaching').catch(error => ({ error: error.message }));
    const data = await literatureCache;
    const banner = $('literature-banner'), list = $('literature-list'), lessons = $('lesson-list'), summary = $('literature-summary');
    if (data.error) {
        banner.replaceChildren(text('p', '文献教学数据暂不可用：' + data.error));
        list.replaceChildren(); lessons.replaceChildren(); summary.replaceChildren();
        return;
    }
    banner.replaceChildren(policyBanner(data.claim_policy));
    summary.replaceChildren();
    for (const [key, value] of Object.entries(data.summary || {})) summary.append(chip(`${key}: ${value}`));
    list.replaceChildren();
    for (const paper of data.paper_cards || []) list.append(paperCard(paper));
    if (!list.children.length) list.append(text('p', '暂无文献卡片。', 'note'));
    lessons.replaceChildren();
    for (const lesson of data.reaction_lessons || []) lessons.append(lessonCard(lesson));
    if (!lessons.children.length) lessons.append(text('p', '暂无反应课程。', 'note'));
}

// ---------- 资源与证据页 ----------
async function loadRecords() {
    try {
        const data = await api(`/api/records?kind=${encodeURIComponent($('kind').value)}&q=${encodeURIComponent($('query').value)}&offset=${offset}`);
        $('count').textContent = `共 ${data.total} 条 · 当前 ${offset + 1}–${Math.min(offset + 25, data.total)}`;
        $('rows').replaceChildren();
        $('previous').disabled = offset === 0;
        $('next').disabled = offset + 25 >= data.total;
        for (const row of data.records) {
            const tr = document.createElement('tr');
            const raw = row.raw;
            const label = raw.name || raw.query_name || raw.substance_query || raw.title || raw.fields?.['RXN:VAR(1):CAS_Reaction_Number'] || raw.template_id || row.id.slice(0, 12);
            const td = document.createElement('td');
            const button = text('button', '查看', 'secondary');
            button.onclick = () => { $('record-json').textContent = JSON.stringify(row, null, 2); $('record-detail').open = true; };
            td.append(button);
            tr.append(text('td', label), text('td', row.kind), text('td', row.source_status || row.review_status), td);
            $('rows').append(tr);
        }
    } catch (error) { $('count').textContent = error.message; }
}
$('find').onclick = () => { offset = 0; loadRecords(); };
$('kind').onchange = $('find').onclick;
$('previous').onclick = () => { offset = Math.max(0, offset - 25); loadRecords(); };
$('next').onclick = () => { offset += 25; loadRecords(); };

// ---------- 项目状态页 ----------
function profileCard(name, phases) {
    const card = div('profile-card');
    card.append(text('h3', (MODE_ZH[name] || name) + `（${name}）`));
    const ul = document.createElement('ul');
    phases.forEach((b, i) => ul.append(text('li', `阶段 ${i + 1}：深度 ${b.depth} · 分支 ${b.branching} · 节点上限 ${b.nodes} · 迭代 ${b.iterations} · ${b.seconds} 秒`)));
    card.append(ul);
    return card;
}

async function loadStatus() {
    try {
        const data = await api('/api/status');
        $('state').textContent = data.state;
        $('stats').replaceChildren();
        for (const [name, value] of [['反应记录', data.resources.counts.note_reaction + data.resources.counts.scifinder_reaction], ['分子身份', data.resources.counts.molecule], ['库存名称冲突', data.resources.name_conflicts], ['已晋级生产', data.resources.production_records]]) {
            const el = div('stat');
            el.append(text('b', value), text('span', name));
            $('stats').append(el);
        }
        // 搜索预算配置（configs/search.json）可读卡片
        const cfg = data.profiles || {};
        const wrap = $('profiles');
        wrap.replaceChildren();
        const grid = div('profile-grid');
        for (const name of ['quick', 'balanced', 'strict']) if (cfg.profiles && cfg.profiles[name]) grid.append(profileCard(name, cfg.profiles[name]));
        const globals = div('profile-card');
        globals.append(text('h3', '全局参数'));
        const ul = document.createElement('ul');
        if (cfg.envelope) ul.append(text('li', `包络上限：深度 ${cfg.envelope.depth} · 分支 ${cfg.envelope.branching} · 节点 ${cfg.envelope.nodes}`));
        ul.append(text('li', `候选池 ${cfg.candidate_pool} · 展示 ${cfg.display_k}`));
        if (cfg.policy_weights) ul.append(text('li', `策略权重：${Object.entries(cfg.policy_weights).map(([k, v]) => `${k} ${v}`).join(' · ')}`));
        ul.append(text('li', `配置状态：${cfg.status || '未标注'}（${name0(cfg.version)}）`));
        globals.append(ul);
        grid.append(globals);
        wrap.append(grid);
    } catch (error) { $('state').textContent = error.message; }
}
function name0(v) { return v != null ? 'version ' + v : '版本未标注'; }

// ---------- 初始化 ----------
api('/api/targets').then(rows => {
    for (const row of rows) {
        const zh = TARGET_NAMES_ZH[String(row.name).toLowerCase()];
        const option = text('option', zh ? `${zh} · ${row.name}` : row.name);
        option.value = row.smiles;
        $('preset').append(option);
    }
}).catch(error => { $('message').textContent = error.message; });
$('preview').click();

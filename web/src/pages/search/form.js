// ---------- 搜索表单 ----------
$('preview').onclick = () => {
    const smiles = $('smiles').value;
    $('molecule').src = '/api/molecule?smiles=' + encodeURIComponent(smiles);
    renderTopologyPanel(smiles);
    showSourceSuggestion();
};
$('preset').onchange = () => { if ($('preset').value) { $('smiles').value = $('preset').value; $('preview').click(); } };
function showSourceSuggestion(){
    const name=$('preset').selectedOptions[0]?.dataset.name;
    const supported=['rutin','isoquercitrin','astragalin'].includes(name);
    $('source-suggestion').hidden=!supported || !runtimeCapabilities?.literature_expansion;
    $('source-suggestion-text').textContent=name==='rutin'?'芦丁已有来源命名转换可供参考；末步目前仅有作者摘要，糖供体和完整条件仍需核查。':'此目标已有精确来源转换；可加入本次探索，条件与供应仍需核查。';
    $('enable-source-search').disabled=$('literature-expansion').checked;
    $('enable-source-search').textContent=$('literature-expansion').checked?'已加入来源记录':'加入来源记录';
}
$('enable-source-search').onclick=()=>{$('engine').value='optimized';$('literature-expansion').checked=true;syncDomainOptions();showSourceSuggestion();};


// Visible defaults are separate from explicit overrides, preserving each phase's budget.
const budgetFields = ['seconds', 'iterations', 'depth', 'branching', 'nodes'];
let searchBudgetProfiles = JSON.parse($('search-budget-defaults').textContent);
const budgetOverrides = new Set();
function syncBudgetDefaults(reset = false) {
    if (reset) budgetOverrides.clear();
    const phases = searchBudgetProfiles[$('mode').value];
    for (const name of budgetFields) {
        const input = $(name), value = phases[phases.length - 1][name];
        input.dataset.defaultValue = String(value);
        if (!budgetOverrides.has(name)) input.value = value;
        $(name + '-default').textContent = '默认 ' + phases.map(phase => phase[name]).join(' → ');
    }
    $('budget-settings-help').textContent = phases.length > 1
        ? '两阶段默认值按“第一阶段 → 第二阶段”标注，输入框显示第二阶段值；修改某项后，两阶段都使用所填值。'
        : '输入框显示当前搜索预算的默认值，可直接修改；切换搜索预算时，已修改的项目会保留。';
}
for (const name of budgetFields) $(name).addEventListener('input', () => budgetOverrides.add(name));
for (const name of [...budgetFields, 'seed', 'top_k']) $(name).addEventListener('blur', () => {
    if ($(name).value !== '') return;
    budgetOverrides.delete(name);
    $(name).value = $(name).dataset.defaultValue ?? $(name).defaultValue;
});
$('mode').onchange = () => syncBudgetDefaults();
$('reset-budget').onclick = () => syncBudgetDefaults(true);
syncBudgetDefaults();

function fetchTeaching() {
    if (!teachingCache) teachingCache = api('/api/teaching').catch(() => null);
    return teachingCache;
}

function fetchLiterature() {
    if (!literatureCache) literatureCache = api('/api/literature-teaching').catch(error => ({ error: error.message }));
    return literatureCache;
}

function fetchTopology(smiles) {
    if (!topologyCache.has(smiles))
        topologyCache.set(smiles, api('/api/topology?smiles=' + encodeURIComponent(smiles)).catch(() => null));
    return topologyCache.get(smiles);
}

// ---------- 糖苷连接拓扑标注（topology.py 候选呈现，不改搜索语义） ----------
// 每处标注同屏携带边界文案：带标记的图合成子不是试剂，不构成独立标签或反应可行性。
function topologyBlock(data) {
    const block = div('topology-block');
    block.append(text('h4', '糖苷连接'));
    const box = div('chips');
    for (const site of data.sites || []) {
        const zh = TOPOLOGY_FAMILY_ZH[site.family] || site.family;
        box.append(text('span', `${zh.replace('候选','')} · ${site.sugar_ring_size} 元糖环`, 'tag topology'));
    }
    block.append(box);
    const detail=document.createElement('details');detail.append(text('summary','连接标注详情'));
    if ((data.sites || []).some(site => site.family === 'other_O_candidate')) detail.append(text('p','其他 O 连接尚未细分，可能包含糖间侧链连接。'));
    detail.append(text('p','高亮连接用于选择断键位置，尚未验证反应可行性。'));block.append(detail);
    return block;
}

// 按家族关键词在文献教学层做工程关联，返回可跳转的文献 chips
async function literatureChips(families) {
    const data = await fetchLiterature();
    if (!data || data.error) return null;
    const seen = new Set(), hits = [];
    for (const family of families) {
        const re = TOPOLOGY_LITERATURE_HINTS[family];
        if (!re) continue;
        for (const paper of data.paper_cards || []) {
            const hay = [paper.title, paper.key_step].filter(Boolean).join(' ');
            if (re.test(hay) && !seen.has(paper.paper_id)) { seen.add(paper.paper_id); hits.push(paper); }
        }
        for (const lesson of data.reaction_lessons || []) {
            const hay = [lesson.title_zh, lesson.title_en, lesson.principle_zh].filter(Boolean).join(' ');
            if (re.test(hay) && !seen.has(lesson.reaction_id)) { seen.add(lesson.reaction_id); hits.push(lesson); }
        }
    }
    if (!hits.length) return null;
    const box = div('chips topology-literature');
    box.append(text('span', '相关文献：', 'topology-lit-label'));
    for (const hit of hits.slice(0, 4)) {
        const id = hit.reaction_id || hit.paper_id;
        const link = text('button', id, 'chip link');
        link.type = 'button';
        link.onclick = () => openLiteratureAnchor('lit-' + id);
        box.append(link);
    }
    if (hits.length > 4) box.append(text('span', `等 ${hits.length} 条`, 'meta'));
    return box;
}

// 侧栏目标分子拓扑区块；检出位点时把结构图切换为候选键高亮版
async function renderTopologyPanel(smiles) {
    topologyRequested = smiles;
    const panel = $('topology');
    panel.replaceChildren();
    const data = await fetchTopology(smiles);
    if (topologyRequested !== smiles) return; // 输入已变更，丢弃过期渲染
    if (!data) { panel.replaceChildren(text('p', '连接标注暂不可用。', 'note')); return; }
    if (data.status === 'parse_failure') { panel.replaceChildren(text('p', '无法解析该SMILES。', 'note')); return; }
    if (!data.sites || !data.sites.length) { panel.replaceChildren(text('p', '未检出糖苷连接。', 'note')); return; }
    const block = topologyBlock(data);
    panel.replaceChildren(block);
    const lit = await literatureChips([...new Set(data.sites.map(s => s.family))]);
    if (topologyRequested !== smiles) return;
    if (lit) block.append(lit);
    $('molecule').src = '/api/molecule?smiles=' + encodeURIComponent(smiles) + '&topology=1';
}

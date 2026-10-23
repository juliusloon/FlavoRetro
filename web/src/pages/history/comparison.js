function sumKnown(phases, key) {
    const values = phases.map(p => p[key]);
    return values.length && values.every(v => typeof v === 'number' && Number.isFinite(v))
        ? values.reduce((a,b) => a+b, 0) : null;
}
function stockIdentityMethods(result) {
    const phases = result.phases?.length ? result.phases : [result];
    const methods = phases.map(phase => phase.stock_identity_profile?.method);
    return methods.every(Boolean) ? methods : null;
}
function actualSearchCodeBindings(result) {
    if (!result.code) return null;
    const phases = result.phases?.length ? result.phases : [result];
    const modules = phases.map(phase => ({
        'flavoretro.search_repaired.SearchTree': 'flavoretro/search_repaired.py',
        'flavoretro.search.SearchTree': 'flavoretro/search.py'
    })[phase.engine_class]);
    if (modules.some(path => !path || !result.code[path])) return null;
    return Object.fromEntries(modules.map(path => [path, result.code[path]]));
}
function metricRows(envelope){
    if(!envelope)return null;const r=envelope.result;
    return {'运行 ID':r.run_id,'运行状态':r.status==='ok'?'已完成':'未完成','目标 SMILES':r.request?.smiles,'候选库存':r.request?.candidate_stock?'启用':'关闭','库存范围':stockProfileLabel(r),'糖苷反应库':r.request?.glycoside_expansion?r.request.glycoside_library_version||'v1':'关闭','文献反应检索':literatureEnabled(r)?'开启':'关闭','候选路线数':r.candidate_count,'展示路线数':r.routes.length,'展示中候选闭合':r.routes.filter(route=>route.closure==='surrogate').length};
}
function renderComparison() {
    const entries = ['a','b'].map(k => comparisonRuns[k]), metrics = entries.map(metricRows);
    $('comparison-table').replaceChildren();
    $('export-comparison').disabled = !entries.every(Boolean);
    if (!entries.every(Boolean)) {
        $('comparison-message').textContent = '请在菜单中分别选择运行 A 与运行 B，然后开始对照。';
        return;
    }
    $('comparison-message').textContent = '已读取两次已保存运行。检查下方条件与限制，再解释差异。';
    const primary=Object.keys(metrics[0]).filter(key=>key!=='运行 ID');
    const comparisonTable = keys => {
        const wrap = div('table-wrap');
        wrap.tabIndex = 0; wrap.setAttribute('role','region'); wrap.setAttribute('aria-label','运行对照，可横向滚动');
        const table = document.createElement('table'), head = document.createElement('thead'), row = document.createElement('tr');
        for (const [label, index] of [['项目',0],['A',1],['B',2]]) {
            const title = index ? `${label} · ${metrics[index - 1]['运行 ID'].slice(0, 12)}` : label;
            const th = text('th', title);
            th.setAttribute('scope', 'col');
            row.append(th);
        }
        head.append(row); table.append(head);
        const body = document.createElement('tbody');
        for (const key of keys) {
            const th = text('th', key);
            th.setAttribute('scope', 'row');
            const tr = document.createElement('tr'); tr.append(th);
            for (const metric of metrics) {
                const value = metric?.[key];
                let display;
                if (value == null) display = '未记录';
                else if (key === '实际阶段预算' && Array.isArray(value)) display = value.map((b, i) => `阶段 ${i + 1} · seed ${b.seed} · 深度 ${b.depth} · 每模型每分子候选 ${b.branching} · 节点上限 ${b.nodes} · 迭代 ${b.iterations} · ${b.seconds} 秒`).join('；');
                else display=factText(value);
                tr.append(text('td', display));
            }
            body.append(tr);
        }
        table.append(body); wrap.append(table);
        return wrap;
    };
    $('comparison-table').append(comparisonTable(primary));
    if (entries.every(Boolean)) {
        const a = entries[0].result, b = entries[1].result;
        const compareFields={'目标':r=>r.request?.smiles,'搜索模式':r=>r.request?.mode,'候选库存':r=>r.request?.candidate_stock,'库存范围':stockProfile,'糖苷反应库':r=>r.request?.glycoside_expansion?r.request.glycoside_library_version||'v1':'关闭','文献反应检索':literatureEnabled};
        const mismatches = [], unknown = [];
        for (const [label,get] of Object.entries(compareFields)) {
            const av=get(a), bv=get(b);
            if (av == null || bv == null) unknown.push(label);
            else if (JSON.stringify(av) !== JSON.stringify(bv)) mismatches.push(label);
        }
        const warnings = [];
        if (a.run_id === b.run_id) warnings.push('A / B 是同一次运行，不能估计差异。');
        if (mismatches.length) warnings.push('条件不同：' + mismatches.join('、') + '。');
        if (unknown.length) warnings.push('条件未完整记录：' + unknown.join('、') + '。');
        if (a.status !== 'ok' || b.status !== 'ok') warnings.push('至少一次运行失败；失败不计作成功。');
        if ([a,b].some(r => r.request?.engine === 'native') && [a,b].some(r => r.request?.engine === 'optimized')) warnings.push('原生树与优化树的节点限制/分支语义不同；相同数字不证明计算预算等价。');
        if (Boolean(a.request?.glycoside_expansion) !== Boolean(b.request?.glycoside_expansion) || a.request?.glycoside_library_version !== b.request?.glycoside_library_version || a.domain_binding?.manifest_sha256 !== b.domain_binding?.manifest_sha256 || literatureEnabled(a) !== literatureEnabled(b) || a.literature_binding?.manifest_sha256 !== b.literature_binding?.manifest_sha256) warnings.push('领域动作库不同；差异可能来自新增来源知识，不能单独归因于搜索算法。');
        if (Boolean(a.request?.flavanone_opening || a.flavanone_binding || a.algorithm_variant==='DFF') !== Boolean(b.request?.flavanone_opening || b.flavanone_binding || b.algorithm_variant==='DFF')) warnings.push('领域图规则不同；新增先验与搜索机制的贡献需分别判断。');
        if (!mismatches.length && !unknown.length) warnings.push('已记录的目标、资源与预算字段一致；这仅是两次计算的描述性对照。');
        warnings.push('闭合只指候选库存终止。展示路线数量不是正确反应率。');
        const box = document.createElement('details');box.className='comparison-warning';box.append(text('summary','比较设置与说明'));for (const warning of warnings) box.append(text('p',warning));$('comparison-table').append(box);
    }
}
let comparisonGeneration=0;
async function compareSelectedRuns(fromRoute=false) {
    const aId = $('compare-run-a').value, bId = $('compare-run-b').value;
    const generation=++comparisonGeneration,routeGeneration=navigationGeneration;
    const current=()=>generation===comparisonGeneration&&routeGeneration===navigationGeneration&&currentPage==='history'&&$('compare-run-a').value===aId&&$('compare-run-b').value===bId;
    if(!fromRoute)recordNavigation();
    if (!aId || !bId) { $('comparison-message').textContent = '请选择运行 A 与运行 B。'; return; }
    if (aId === bId) { $('comparison-message').textContent = 'A 与 B 是同一运行，无法对照。'; return; }
    $('run-comparison').disabled = true;
    $('comparison-message').textContent = '正在读取两次运行并核对完整性…';
    try {
        const [a, b] = await Promise.all([api('/api/runs/' + encodeURIComponent(aId)), api('/api/runs/' + encodeURIComponent(bId))]);
        if(!current())return;
        comparisonRuns.a = a; comparisonRuns.b = b;
        renderComparison();
    } catch (error) {
        if(!current())return;
        $('comparison-table').replaceChildren();
        $('export-comparison').disabled = true;
        $('comparison-message').textContent = '对照读取失败：' + error.message;
    } finally {
        if(generation===comparisonGeneration)$('run-comparison').disabled = false;
    }
}
$('run-comparison').onclick = () => compareSelectedRuns();
for (const id of ['compare-run-a', 'compare-run-b']) $(id).onchange = () => {
    comparisonGeneration++;$('run-comparison').disabled=false;
    recordNavigation(true);
    $('comparison-message').textContent = '运行选择已更改；点击“开始对照”重新读取。';
    $('comparison-table').replaceChildren();
    $('export-comparison').disabled = true;
};
$('export-comparison').onclick = () => {
    if (!comparisonRuns.a || !comparisonRuns.b) return;
    downloadObject('flavoretro-run-comparison.json', {
        schema_version:1, scope:'descriptive_two_run_comparison', independent_chemical_validation:false,
        exported_at:new Date().toISOString(), runs:comparisonRuns
    });
};

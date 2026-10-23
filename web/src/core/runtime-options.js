// ---------- TASK-022：领域选项、真实运行对照与循序练习 ----------
function syncDomainOptions() {
    const native = ['native','native_stop'].includes($('engine').value);
    const stop = $('engine').value === 'native_stop';
    $('engine').querySelector('option[value="native_stop"]').disabled = !runtimeCapabilities?.search_methods?.includes('native_proxy_stop_v1');
    $('engine').querySelector('option[value="native_stop"]').hidden = !runtimeCapabilities?.search_methods?.includes('native_proxy_stop_v1');
    $('search-method-help').textContent = stop ? '已选择原生树＋保守提前停止。需显式开启候选库存；每个阶段独立判断当前保留树的暂定评分界，不能认证化学可行性、供应或参考反应召回。' : '选择通用优化搜索或原生搜索；两者均逐次探索新路线。';
    if (native) { $('glycoside-version').value = ''; $('literature-expansion').checked = false; }
    const ffReady = runtimeCapabilities?.flavanone_opening === true && $('engine').value === 'native';
    $('flavanone-opening').disabled = !ffReady;
    if (!ffReady) $('flavanone-opening').checked = false;
    $('flavanone-help').textContent = !runtimeCapabilities?.flavanone_opening ? '后端暂未开放黄烷酮开环候选。' : $('engine').value !== 'native' ? '选择 native 后可显式启用。候选来自领域图规则，默认关闭。' : '可加入保留全部取代基的黄烷酮开环候选。规则不补回保护基，不预测C2选择性、条件或化学可行性；与通用模型共用原生MCTS。';
    $('glycoside-version').disabled = native;
    $('literature-expansion').disabled = native || !runtimeCapabilities?.literature_expansion;
    $('glycoside-version').querySelector('option[value="v8"]').disabled = !runtimeCapabilities?.v8;
    $('literature-help').textContent = !runtimeCapabilities?.literature_expansion ? '后端升级待验证：新文献精确检索暂不可用。' : native ? '原生基线关闭新文献精确检索。选择 optimized 后可显式启用。' : '默认关闭。仅在产物图精确匹配时提供原文反应前体；来源重现不等于新反应预测或独立迁移。';
    $('domain-help').textContent = native
        ? '当前使用原生树；糖苷扩展关闭，黄烷酮图规则见单独开关。原生树不执行 optimized 的节点上限。'
        : ($('glycoside-version').value
            ? `已选择 ${$('glycoside-version').value} 来源限定扩展；已报道实例与范围迁移候选分别标记，独立化学验证未完成。`
            : '默认关闭。启用后加入来源限定动作；独立化学验证与实验条件仍未完成。');
    if (!runtimeCapabilities?.v8) $('domain-help').textContent += ' v8 后端升级待验证。';
    showSourceSuggestion();
}
$('engine').onchange = syncDomainOptions;
$('glycoside-version').onchange = syncDomainOptions;
syncDomainOptions();
function syncStockOptions() {
    const enabled = $('candidate').checked;
    const zincReady=runtimeCapabilities?.stock_profiles?.includes('zinc')===true;
    $('stock-profile').disabled = !enabled || !zincReady;
    $('stock-profile').querySelector('option[value="zinc"]').disabled = !zincReady;
    if (!enabled) $('stock-profile').value = 'reviewed';
    $('stock-help').textContent = !enabled
        ? '候选库存未启用。'
        : $('stock-profile').value === 'zinc'
            ? '使用 ZINC 库存，排除目标自身。'
            : '使用项目审核候选库存。';
    if (!zincReady) $('stock-help').textContent += ' ZINC 后端升级待验证。';
}
$('candidate').onchange = syncStockOptions;
$('stock-profile').onchange = syncStockOptions;
syncStockOptions();
async function loadRuntimeCapabilities() {
    try { const status=await api('/api/status');runtimeCapabilities=status.runtime_capabilities || null;
        if (status.profiles?.profiles) { searchBudgetProfiles=status.profiles.profiles;syncBudgetDefaults(); }
    }
    catch(error) { runtimeCapabilities=null; }
    syncDomainOptions();syncStockOptions();
}
const capabilitiesReady=loadRuntimeCapabilities();
function stockProfile(result) {
    return result.request?.stock_profile || (result.stock_binding ? 'zinc' : 'reviewed');
}
function stockProfileLabel(result) {
    return stockProfile(result) === 'zinc' ? 'ZINC 历史候选库存' : '项目审核候选库存';
}
function flavanoneEnabled(result) {
    return Boolean(result?.request?.flavanone_opening || result?.flavanone_binding || result?.algorithm_variant==='DFF');
}
function literatureEnabled(result) {
    return Boolean(result.request?.literature_expansion || result.literature_binding);
}

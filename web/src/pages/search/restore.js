function phaseBudgets(result) {
    if (Array.isArray(result.phases) && result.phases.length) return result.phases.map(p=>({seed:p.seed,...p.budget}));
    if (result.effective_config && result.request) return [{seed:result.request.seed,seconds:result.request.seconds,
        iterations:result.request.iterations,depth:result.request.depth,branching:result.request.branching,nodes:result.request.nodes}];
    return null;
}
function savedMethodNote(result) {
    if(!result)return '';
    const variant=result.algorithm_variant;
    if((variant==='NFAST' || result.request?.search_method==='native_proxy_stop_v1') && runtimeCapabilities?.search_methods?.includes('native_proxy_stop_v1'))return ' 已恢复原生树＋保守提前停止配置；新搜索使用当前运行时代码，历史代码与结果身份仍保留。';
    if(variant==='DFF' || result.request?.flavanone_opening) return runtimeCapabilities?.flavanone_opening ? ' 已恢复黄烷酮开环候选开关；新搜索使用当前代码，历史方法与结果保留原身份。' : ' 黄烷酮图规则尚未接入当前后端；再次搜索使用普通原生引擎，原记录仍保留。';
    if(variant==='repaired_O') return stockIdentityMethods(result)?.every(method=>method==='canonical_smiles_full_inchikey_v1')===true ? ' 已恢复通用优化修复和精确库存身份；新搜索使用当前代码，原方法与结果保留原身份。' : ' 此旧修复记录使用历史库存身份；再次搜索使用当前修复版和精确库存身份，不重放旧库存语义。';
    if(variant && !['N','O','D','D8'].includes(variant))return ` 此实验变体 ${variant} 尚未接入当前实时入口；再次搜索将使用 ${result.request?.engine || '所选'} 普通引擎。原记录仍为原方法结果。`;
    return '';
}

function restoreSearchRequest(request,result=null) {
    if(!request)return;
    if(request.smiles){$('smiles').value=request.smiles;$('preset').value='';}
    for(const key of ['mode','engine','seed','top_k'])if(request[key]!=null)$(key).value=request[key];
    const restoredFF=request.flavanone_opening===true || result?.algorithm_variant==='DFF';
    if(restoredFF && runtimeCapabilities?.flavanone_opening) $('engine').value='native';
    const restoredStop=request.search_method==='native_proxy_stop_v1' || result?.algorithm_variant==='NFAST';
    if(restoredStop && runtimeCapabilities?.search_methods?.includes('native_proxy_stop_v1')) $('engine').value='native_stop';
    budgetOverrides.clear();
    for (const key of budgetFields) if (request[key] != null) { $(key).value=request[key];budgetOverrides.add(key); }
    syncBudgetDefaults();
    $('candidate').checked=request.candidate_stock===true;
    $('stock-profile').value=result ? stockProfile(result) : request.stock_profile || 'reviewed';
    $('literature-expansion').checked=result ? literatureEnabled(result) : request.literature_expansion===true;
    syncStockOptions();
    const version=request.glycoside_expansion?(request.glycoside_library_version || 'v1'):'';
    $('glycoside-version').value=[...$('glycoside-version').options].some(o=>o.value===version)?version:'';
    syncDomainOptions();
    if(version && $('glycoside-version').value!==version)$('domain-help').textContent=`该已存运行使用 ${version}；此版本不在当前可选菜单中。再次搜索前需明确选择，原运行元数据保持不变。`;
    $('flavanone-opening').checked=restoredFF && runtimeCapabilities?.flavanone_opening===true && $('engine').value==='native';
    const methodNote=savedMethodNote(result);
    if(methodNote)$('search-method-help').textContent+=methodNote;
    $('preview').click();
}

// ---------- 路线解读 ----------
const REVIEW_ZH = {
    development_gold: '结构/分类开发审核认可', excluded: '该记录排除',
    primary_instance_verified: '原文实例已核对', export_procedure_supported: '数据库实验段支持',
    bibliography_or_abstract_only: '仅书目或摘要', conflict: '来源冲突', unavailable: '来源不可得',
    quarantine_name_structure_mismatch: '名称与结构错配 · 隔离',
    retain_encoded_candidate: '保留编码候选', retain_candidate_not_primary_certified: '模板候选 · 未获原文认证',
    note_token_and_components_consistent: '笔记定位与组分一致', note_canonical_match_confirmed: '笔记再定位一致',
    exclude_exact_reaction_parse_failure_retain_note: '解析失败 · 保留笔记', retain_unmatched_not_verified: '笔记反应未验证',
    catalog_claim_not_current_supply_certified: '历史目录线索 · 无当前精确供应认证',
    internal_candidate_no_verified_exact_vendor: '内部候选 · 无精确供应证据',
    reject_listing_for_mismatched_stock_graph: '错配结构的供应声明已否决', reject_parent_sugar_substitution: '母体糖替代声明已否决',
    guide_supported: '笔记线索支持的结构候选', outside_guide_structure: '笔记线索之外的结构候选', low_or_unknown: '低优先级或未知',
    primary_numeric_supported: '原文数值支持', primary_inequality_export_discrepancy: '原文不等式与数据库值有差异',
    final_assigned_export_only: '仅导出实验段支持', final_assigned: '产率已归属（证据等级见来源）',
    final_not_checked: '产率未核查', final_not_primary_verified: '原文产率未核实', final_database_reported_not_primary_verified: '数据库报告，原文未核实',
    final_absent: '明确未报告', final_absent_composition_not_yield: '组成比例，不是产率',
    final_absent_multiple_primary_recoveries: '多次回收，未报告单一产率', final_absent_with_conversion_note: '未报告产率，另有转化说明',
    final_ambiguous: '产率归属不明', final_ambiguous_multi_product: '多产物产率归属不明', excluded_record: '记录已排除',
    same_structure_alias_use_narirutin_keep_both_ids: '同结构别名 · 保留原ID',
    quarantine_both_udp_arabinose_name_assignments: 'UDP糖身份声明隔离',
    blocked_source_blacklist: '来源黑名单', incomplete_record: '不完整记录', pathway_suspect: '路径压缩嫌疑',
};
function reviewBlock(review, sourceAlreadyShown=false) {
    const block=document.createElement('details');block.className='review-block';block.append(text('summary','来源与检查'));
    if (!review) { block.append(text('p', '历史运行未记录审核视图')); return block; }
    if (review.status === 'legacy_validation') { block.append(text('p', '旧视图开发验证 · 未应用审核准入')); return block; }
    if (review.source_instance_supported) block.append(text('p', '该结构变换有指定原文实例支持；本次预测条件与可行性未确认。'));
    if (review.status === 'unmatched') block.append(text('p', '未与审核实例严格匹配；保留预测候选。'));
    const entries = review.evidence || (review.stock_records || []).map(x => ({...x.review, display_name: x.name})) || [];
    const records = entries.length ? entries : (review.axes ? [review] : []);
    for (const r of records) {
        const details = document.createElement('details');
        details.append(text('summary', (r.canonical_display_name || r.display_name || ('记录 ' + (r.record_id || '').slice(0, 12))) + (r.card_number ? ` · 审核卡 ${r.card_number}` : '')));
        for (const [axis, value] of Object.entries(r.axes || {})) details.append(kv(({structure_classification:'结构/分类', primary_source:'来源', yield_status:'参考实例产率状态', note_locator:'笔记定位', identity:'身份', current_vendor:'供应', record_disposition:'记录处置'})[axis] || axis, REVIEW_ZH[value] || value));
        if (r.source_instance_yield) {
            const y = r.source_instance_yield;
            const primary = y.primary_value ?? y.primary_reported_value;
            const reported = y.reported_value ?? y.raw_reported?.value ?? y.reported_raw ?? y.raw_value;
            if (primary != null) details.append(kv('参考原文产率（非预测值）', `${primary}${y.primary_reported_uncertainty != null ? ' ± ' + y.primary_reported_uncertainty : ''}%`));
            if (reported != null) details.append(kv('原数据库报告值', String(reported)));
            if (y.measurement_method) details.append(kv('参考测量方法', y.measurement_method));
            if (y.reason) details.append(text('p', y.reason));
        }
        if (r.identity_reason) details.append(text('p', r.identity_reason));
        if(r.effective_runtime_candidate_allowed===false)details.append(text('p','此条目未获准作为搜索终止原料。'));
        if (r.source_instance_evidence) {
            const evidence = r.source_instance_evidence;
            if (evidence.reason) details.append(text('p', evidence.reason));
            for (const source of evidence.sources || []) {
                details.append(kv('参考出处', source.title || source.doi || '来源已登记'));
                if (source.evidence_locator) details.append(kv('实例位置', source.evidence_locator));
                if (/^https?:\/\//.test(source.url || '')) {
                    const a = text('a', '查看来源'); a.href = source.url; a.target = '_blank'; a.rel = 'noopener'; details.append(a);
                }
            }
        }
        block.append(details);
    }
    if (review.task022 && !sourceAlreadyShown) block.append(literatureEvidence(review.task022));
    if (review.stock_records) block.append(text('p', '库存候选命中不等于可采购；无当前精确供应认证。'));
    if (review.status === 'no_specific_review') block.append(text('p', '无专项审核结论；保留原事实与约束。'));
    return block;
}

function leafBadges(leaf) {
    const row = div('mol-badges');
    row.append(text('span', CLOSURE_LEAF_ZH[leaf.closure] || leaf.closure || '未标注', 'tag' + (leaf.closure === 'partial' ? ' partial' : '')));
    if (leaf.stock_binding && leaf.closure === 'surrogate') row.append(text('span', '库存结构命中', 'tag partial'));
    else if (leaf.evidence_basis) row.append(text('span', EVIDENCE_BASIS_ZH[leaf.evidence_basis] || leaf.evidence_basis, 'tag partial'));
    if (leaf.hazard && leaf.hazard !== HAZARD_UNKNOWN) row.append(text('span', '危险标记：' + leaf.hazard, 'tag hazard'));
    else row.append(text('span', '危险未认证', 'tag neutral'));
    return row;
}

function leafEvidence(leaf) {
    const check = leaf.structure_check || {};
    if (!leaf.review && !check.status && !leaf.stock_profile && !leaf.stock_binding) return null;
    const details = document.createElement('details');
    details.className = 'mol-evidence';
    details.append(text('summary', '原料检查'));
    let checkText = STRUCTURE_STATUS_ZH[check.status] || check.status || '未检查';
    if(check.unspecified_carbon_stereo!=null)checkText+=` · 未指定碳立体中心 ${check.unspecified_carbon_stereo} 个`;
    else if(check.unspecified_stereo)checkText+=` · 历史未指定立体标记 ${check.unspecified_stereo} 个`;
    if(check.unassigned_hetero_stereo_flags)checkText+=` · 另有杂原子立体标记 ${check.unassigned_hetero_stereo_flags} 个待核查`;
    details.append(kv('结构检查', checkText));
    if (leaf.stock_profile || leaf.stock_binding) {
        const zinc = leaf.stock_profile === 'zinc' || Boolean(leaf.stock_binding);
        details.append(kv('库存范围', zinc ? 'ZINC 历史候选库存' : '项目审核候选库存'));
    }
    if(leaf.subgoal)details.append(kv('下一步研究',leaf.subgoal.next_step));
    if (leaf.review) details.append(reviewBlock(leaf.review));
    return details;
}

// 按 classification 在教学数据中查条目；查不到回退 default 并注明
function teachingEntry(classification, teaching) {
    if (teaching && classification && teaching.classifications && teaching.classifications[classification])
        return { entry: teaching.classifications[classification], fallback: false };
    return { entry: teaching ? teaching.default : null, fallback: true };
}

function teachingBlock(meta, teaching) {
    const { entry, fallback } = teachingEntry(meta && meta.classification, teaching);
    const block = document.createElement('details');block.className='teaching-block';block.append(text('summary',entry?.label_zh || '通用反应原理'));
    if (!entry) {
        block.append(text('p', '反应原理暂不可用。'));
        return block;
    }
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

function flavanoneEvidence(evidence) {
    const block=div('domain-evidence');block.append(text('h4','领域图规则 · 计算候选'));
    block.append(text('p','支持该反应类别的文献不等于当前底物已有报道。候选保留原子及取代基，不能补回保护基；C2选择性、收率、条件和可行性仍未预测。'));
    const line=div('source-doi');line.append(text('b','类别来源：'));
    for(const doi of evidence.class_support_dois || []) {
        const link=text('a',doi);link.href='https://doi.org/'+encodeURIComponent(doi);link.target='_blank';link.rel='noopener';line.append(link,document.createTextNode(' '));
    }
    block.append(line,text('p','尚无当前底物的精确来源实例或独立化学验证。','note'));return block;
}

function stepCard(item, stepNo, teaching, includeHeading = true) {
    const meta = item.node.metadata || {};
    const card = div('step-card');
    if (includeHeading) card.append(text('h3', `第 ${stepNo} 步 · ${meta.task022_evidence || item.node.review?.task022 ? '文献已报道反应（精确来源重现）' : meta.task022_scope_hypothesis ? '黄烷酮开环候选（领域图规则）' : '预测反应（条件与可行性未确认）'}`));
    const template = meta.template || (meta.template_hash ? meta.template_hash.slice(0, 16) + '…' : (meta.template_code || '—'));
    const { entry } = teachingEntry(meta.classification, teaching);
    const family=entry?.label_zh || '未分类';
    card.append(kv('反应家族', family));
    if (meta.task022_scope_hypothesis) card.append(flavanoneEvidence(meta.task022_scope_hypothesis));
    if (meta.task016_evidence) card.append(domainEvidence(meta.task016_evidence));
    if (meta.task022_evidence) card.append(literatureEvidence(meta.task022_evidence,(item.node.children || []).filter(n=>n.type==='mol').map(n=>n.smiles)));
    card.append(reviewBlock(item.node.review || meta.review,Boolean(meta.task022_evidence)));
    if (teaching) card.append(teachingBlock(meta, teaching));
    return card;
}

function localTime(value) {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' });
}

function phaseTotal(result, key) {
    const values = (result.phases || []).map(phase => Number(phase[key]));
    return values.length && values.every(Number.isFinite) ? values.reduce((sum, value) => sum + value, 0) : null;
}

function engineLabel(result) {
    const stop = result.request?.search_method === 'native_proxy_stop_v1' || result.algorithm_variant === 'NFAST';
    return `${result.request?.engine || '未记录'}${stop ? '＋提前停止' : ''}`;
}

function renderRunMeta(result){
    const card=div('meta-card run-summary'),head=div('run-summary-head');head.append(text('strong',savedRun?'已保存的探索结果':'本次探索结果'));if(result.created_at)head.append(text('span',localTime(result.created_at),'note'));card.append(head);
    const stats=div('run-summary-stats');for(const [value,label]of [[result.candidate_count??result.routes.length,'候选路线'],[result.routes.length,'展示路线'],[result.routes.filter(r=>r.closure==='surrogate').length,'展示中候选闭合']]){const cell=div();cell.append(text('b',value),text('span',label));stats.append(cell);}
    card.append(stats,text('p','路线按研究优先级从高到低排列。候选库存命中不等于当前可采购；预测步骤仍需核查条件与选择性。','note'));$('run-meta').replaceChildren(card);
}

async function render(result,projection=null){
    if(projection||result!==lastResult){const projected=new Map((projection||[]).map(route=>[route.route_id,route]));displayedRoutes=result.routes.map(route=>({...route,...(projected.get(route.route_id)||{})}));for(const route of displayedRoutes)if(route.score_status!=='research_priority_higher_is_better'){route.score=100/(1+Math.max(0,route.score??0));route.legacyPresentation=true;}displayedRoutes.sort((a,b)=>b.score-a.score||a.route_id.localeCompare(b.route_id));}
    lastResult = result;
    if (result.run_id !== renderedRunId) selectedRouteIndex = 0;
    renderedRunId = result.run_id;
    $('search-results').classList.remove('is-empty');$('search-intro').hidden=true;
    $('route-workbench').hidden = false;
    $('download').hidden = false;
    renderRunMeta(result);
    renderLabDevelopment(result);
    $('learning-use-run').disabled = false;
    const teaching = await fetchTeaching();
    if (lastResult !== result) return; // 期间又发起了新搜索，放弃本次渲染
    lastTeaching = teaching;
    $('routes').removeAttribute('aria-busy');
    renderRoutes(result, teaching);
}

function renderRoutes(result, teaching) {
    const catalog = $('route-catalog');
    catalog.replaceChildren();
    $('route-catalog-card').hidden = !displayedRoutes.length;
    if (!displayedRoutes.length) {
        $('routes').replaceChildren(text('p', '本预算没有提取出路线。可调整预算后重新搜索。', 'empty'));
        return;
    }
    if (selectedRouteIndex >= displayedRoutes.length) selectedRouteIndex = 0;
    $('route-catalog-summary').textContent = `共 ${displayedRoutes.length} 条展示路线 · 分数降序`;
    displayedRoutes.forEach((route, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'route-entry';
        button.id = 'route-tab-' + index;
        button.setAttribute('role', 'tab');
        button.setAttribute('aria-controls', 'route-detail-panel');
        button.setAttribute('aria-selected', String(index === selectedRouteIndex));
        button.tabIndex = index === selectedRouteIndex ? 0 : -1;
        button.append(text('span', `路线 ${index + 1}`, 'route-entry-title'));
        const meta = div('route-entry-meta');
        meta.append(text('span', `${route.steps} 步`, 'tag neutral'), text('span', `优先级 ${fixed(route.score,4)}`, 'tag neutral'));
        if (route.closure) meta.append(text('span', CLOSURE_ROUTE_ZH[route.closure] || route.closure, 'tag' + (route.closure === 'partial' ? ' partial' : '')));
        button.append(meta);
        button.onclick = () => selectRoute(index, result, teaching);
        catalog.append(button);
    });
    renderRouteDetail(displayedRoutes[selectedRouteIndex], selectedRouteIndex, teaching);
}

function selectRoute(index, result, teaching,fromRoute=false) {
    selectedRouteIndex = index;
    [...$('route-catalog').children].forEach((button, i) => {
        const active = i === index;
        button.setAttribute('aria-selected', String(active));
        button.tabIndex = active ? 0 : -1;
    });
    renderRouteDetail(displayedRoutes[index], index, teaching);
    if(!fromRoute)recordNavigation();
}

$('route-catalog').addEventListener('keydown', event => {
    const buttons = [...$('route-catalog').children], index = buttons.indexOf(document.activeElement);
    if (index < 0 || !lastResult || !displayedRoutes.length) return;
    let next = null;
    if (event.key === 'ArrowRight') next = buttons[(index + 1) % buttons.length];
    else if (event.key === 'ArrowLeft') next = buttons[(index - 1 + buttons.length) % buttons.length];
    else if (event.key === 'Home') next = buttons[0];
    else if (event.key === 'End') next = buttons[buttons.length - 1];
    if (!next) return;
    event.preventDefault();
    selectRoute(buttons.indexOf(next), lastResult, lastTeaching);
    next.focus();
});

function reactionKind(meta) {
    if(meta.task022_evidence?.source?.evidence_scope==='primary_abstract')return '作者摘要所述转换';
    if (meta.task022_evidence) return '文献已报道反应';
    if (meta.task022_scope_hypothesis) return '黄烷酮开环候选';
    return '预测反应 · 条件未确认';
}

function schemeMol(node, context) {
    const wrap = div('scheme-node');
    const reactions = (node.children || []).filter(child => child.type === 'reaction');
    const leaf = !reactions.length;
    const figure = div('scheme-mol' + (context.target ? ' is-target' : '') + (leaf ? ' is-leaf' : ''));
    const img = document.createElement('img');
    img.src = '/api/molecule?smiles=' + encodeURIComponent(node.smiles);
    img.alt = context.target ? '目标分子结构' : leaf ? '末端原料结构' : '中间体结构';
    img.loading = 'lazy';
    img.onerror = () => { img.replaceWith(text('p', '结构图不可用。', 'note')); };
    figure.append(img);
    const caption = div('scheme-caption');
    if (context.target) caption.append(text('span', '目标分子', 'tag'));
    else if (leaf) caption.append(text('span', '末端原料', 'tag'));
    if (leaf) caption.append(leafBadges(node));
    if (caption.children.length) figure.append(caption);
    if (leaf) {
        const evidence = leafEvidence(node);
        if (evidence) figure.append(evidence);
    }
    wrap.append(figure);
    if (leaf) return wrap;

    for (const reaction of reactions) {
        context.counter.value += 1;
        const stepNo = context.counter.value, meta = reaction.metadata || {};
        const branch=div('scheme-branch');
        const arrow = div('scheme-arrow');
        arrow.append(text('span', '⟹', 'scheme-arrow-mark'));
        const label = div('scheme-arrow-label');
        label.append(text('strong', `第 ${stepNo} 步`), text('span', reactionKind(meta), 'tag neutral'));
        arrow.append(label);
        branch.append(arrow);

        const reactants = div('scheme-reactants');
        const precursors = (reaction.children || []).filter(child => child.type === 'mol');
        precursors.forEach((child, i) => {
            if (i) reactants.append(text('span', '+', 'scheme-plus'));
            reactants.append(schemeMol(child, { ...context, target: false }));
        });
        if (!precursors.length) reactants.append(text('p', '未记录前体结构。', 'note'));
        branch.append(reactants);

        const evidence = document.createElement('details');
        evidence.className = 'scheme-evidence';
        evidence.append(text('summary', `第 ${stepNo} 步依据`));
        evidence.append(stepCard({ node: reaction, depth: stepNo - 1 }, stepNo, context.teaching, false));
        arrow.append(evidence);
        wrap.append(branch);
    }
    return wrap;
}

function renderRouteDetail(route, index, teaching) {
    const card = div('card route route-detail-panel');
    card.id = 'route-detail-panel';
    card.setAttribute('role', 'tabpanel');
    card.setAttribute('aria-labelledby', 'route-tab-' + index);
    const heading = div('route-head');
    heading.append(text('h2', `路线 ${index + 1}`));
    heading.append(text('span', CLOSURE_ROUTE_ZH[route.closure] || route.closure, 'tag' + (route.closure === 'partial' ? ' partial' : '')));
    heading.append(text('span', `${route.steps} 步`, 'tag neutral'), text('span', `优先级 ${fixed(route.score,4)}`, 'tag neutral'));
    card.append(heading);

    if(route.route_quality)card.append(text('p',`来源支持 ${route.route_quality.source_supported_steps}/${route.steps} 步 · O-乙酰保护调整 ${route.route_quality.protection_only_steps} 步`,'note'));
    if (route.cost) {
        const cost = div('cost');
        const c = route.cost;
        cost.append(text('span', `评分构成：步骤 ${c.steps} · 未解决原料 ${c.unresolved_materials} · 已知危险 ${c.known_hazards} · 未指定碳立体 ${c.unspecified_leaf_carbon_stereo ?? c.unspecified_leaf_stereo} · 其他立体标记 ${c.unassigned_hetero_stereo_flags ?? 0}`));
        card.append(cost);
    }
    card.append(text('p', '从左到右：目标分子 → 中间体 → 末端原料。左右滑动查看完整路线。', 'note'));

    const scheme = div('scheme-scroll');
    scheme.tabIndex=0;scheme.setAttribute('role','region');scheme.setAttribute('aria-label','横向逆合成路线，可左右滚动');
    scheme.append(schemeMol(route.tree, {counter:{value:0},teaching,target:true}));
    card.append(scheme);
    appendSourceVariants(card,route);

    const details = document.createElement('details');
    details.append(text('summary', '评分口径与路线状态'));
    details.append(text('p',route.legacyPresentation?'旧版成本转换为高分优先，仅用于本次历史路线排序。':'库存覆盖28%、前体简化20%、模型支持20%、路线简洁12%、来源支持20%；覆盖与负担按唯一末端结构计算；O-乙酰保护调整另扣分；另扣已知危险与未指定碳立体；杂原子立体标记另列核查，不补构型。候选闭合为60–100分，未闭合低于60分。分数不是成功概率，未知危险不视为安全。'));
    if(route.score_components)for(const [key,label]of Object.entries({stock_coverage:'库存覆盖',precursor_simplicity:'前体简化',model_support:'模型支持',route_economy:'路线简洁',source_support:'来源支持'}))details.append(kv(label,fixed(route.score_components[key],4)));
    if(route.ranking_metrics?.model_probability_coverage<1)details.append(text('p','部分步骤缺少模型先验，缺失部分不计入模型支持。'));
    if(route.ranking_method&&savedRun&&lastResult.ranking_method!==route.ranking_method)details.append(text('p','历史展示路线按当前口径重排；原始记录与导出保留当时结果。'));
    card.append(details);
    $('routes').replaceChildren(card);
}

// 搜索进行中的骨架屏（aria-hidden 装饰，文本状态仍由 #message 直播）
function skeletonRoutes() {
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 3; i++) {
        const card = div('card route skeleton-card');
        card.setAttribute('aria-hidden', 'true');
        card.append(div('sk-line w40'), div('sk-line w70'), div('sk-block'));
        fragment.append(card);
    }
    return fragment;
}

$('search-form').onsubmit = async event => {
    $('search-results').classList.remove('is-empty');$('search-intro').hidden=true;
    event.preventDefault();
    if (($('glycoside-version').value==='v8' && !runtimeCapabilities?.v8) || ($('literature-expansion').checked && !runtimeCapabilities?.literature_expansion) || ($('stock-profile').value==='zinc' && !runtimeCapabilities?.stock_profiles?.includes('zinc'))) {
        $('message').setAttribute('role','alert');$('message').textContent='后端升级待验证：当前已选功能尚未获后端支持，请刷新或调整选项。';return;
    }
    if ($('engine').value === 'native_stop' && (!runtimeCapabilities?.search_methods?.includes('native_proxy_stop_v1') || !$('candidate').checked)) {
        $('message').setAttribute('role','alert');$('message').textContent='提前停止需后端支持并显式开启候选库存。';return;
    }
    if ($('flavanone-opening').checked && (!runtimeCapabilities?.flavanone_opening || $('engine').value !== 'native')) {
        $('message').setAttribute('role','alert');$('message').textContent='黄烷酮开环候选需后端支持及 native 引擎。';return;
    }
    $('preview').click();
    $('submit').disabled = true;
    $('message').setAttribute('role', 'status');
    $('message').textContent = '正在执行新的 MCTS 搜索，请保持页面打开…';
    $('run-meta').replaceChildren();
    $('route-workbench').hidden = false;
    $('route-catalog-card').hidden = true;
    $('route-catalog').replaceChildren();
    $('route-catalog-summary').textContent = '';
    $('download').hidden = true;
    $('routes').setAttribute('aria-busy', 'true');
    $('routes').replaceChildren(skeletonRoutes());
    const req = { smiles: $('smiles').value, mode: $('mode').value, seed: Number($('seed').value), candidate_stock: $('candidate').checked };
    req.engine = $('engine').value === 'native_stop' ? 'native' : $('engine').value; req.top_k = Number($('top_k').value);
    if ($('engine').value === 'native_stop') req.search_method = 'native_proxy_stop_v1';
    if ($('glycoside-version').value) { req.glycoside_expansion = true; req.glycoside_library_version = $('glycoside-version').value; }
    if ($('literature-expansion').checked) req.literature_expansion = true;
    if ($('flavanone-opening').checked) req.flavanone_opening = true;
    if ($('candidate').checked && $('stock-profile').value === 'zinc') req.stock_profile = 'zinc';
    for (const name of budgetFields) if (budgetOverrides.has(name) && $(name).value !== '') req[name] = Number($(name).value);
    try {
        const result = await api('/api/search', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(req) });
        savedRun = false; currentReadSource = null; currentManifest = null;
        const saved = await api('/api/runs/' + result.run_id); currentManifest = saved.manifest;
        await render(result);
        if(currentPage==='search')recordNavigation();else{rememberPage('search',captureRoute('search'));updatePageLocation();}
        $('message').textContent = '本次实时搜索完成。结果仅支持计算探索。';
    } catch (error) {
        $('message').setAttribute('role', 'alert');
        $('message').textContent = '搜索失败：' + error.message;
    } finally {
        $('routes').removeAttribute('aria-busy');
        $('submit').disabled = false;
    }
};
$('download').onclick = () => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify({execution_source: savedRun ? (currentReadSource || 'explicit_saved_run') : lastResult.execution_source, manifest:currentManifest, result:lastResult}, null, 2)], { type: 'application/json' }));
    a.download = lastResult.run_id + '.json';
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};

// ---------- 中文标签映射（移植自旧项目，按新后端枚举收敛） ----------
const CLOSURE_ROUTE_ZH = { surrogate: '候选闭合', partial: '未闭合' };
const CLOSURE_LEAF_ZH = { surrogate: '候选闭合', partial: '未闭合' };
const EVIDENCE_BASIS_ZH = { unreviewed_candidate_stock: '未审候选库存', unresolved: '未解决' };
const YIELD_STATUS_ZH = { lower_bound:'下界，不能按精确值解释', reported_lower_bound:'原文报告下界', numeric:'原文数值', reported_numeric:'原文报告数值', zero:'原文报告为零', reported_zero:'原文报告为零', not_reported:'未报告', not_isolated_yield:'仅有文献过程报告，未按分离收率登记', missing:'缺失', qualitative:'定性报告', trace:'痕量' };
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
// 拓扑位点家族标签（值原样保留 family 串，仅附中文释义；topology.py 候选，非反应可行性）
const TOPOLOGY_FAMILY_ZH = {
    aryl_O_candidate: '芳基 O-糖苷键候选',
    sugar_sugar_O_candidate: '糖-糖 O 连接候选',
    aryl_C_candidate: '芳基 C-糖苷键候选',
    other_O_candidate: '其他 O 连接候选',
    N_candidate: 'N 连接候选',
    phosphate_donor_control: '磷酸供体对照'
};
// 家族 → 文献卡片关键词（工程关联匹配，非化学验证；命中 title/key_step 等文本）
const TOPOLOGY_LITERATURE_HINTS = {
    aryl_C_candidate: /C-glycosyl/i,
    aryl_O_candidate: /O[- ]glycosyl|glucoside|glycosylation|rhamnosid/i,
    sugar_sugar_O_candidate: /branched|rhamnosyl|1,6|sugar.?chain/i,
    other_O_candidate: /glycosyl/i,
    N_candidate: /glycosyl/i,
    phosphate_donor_control: /glycosyl/i
};

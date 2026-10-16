"""Progress v11: current bounded SS qualification and sixth C raw freeze."""
import json
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
R=ROOT/'docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md'
S=ROOT/'STATE.md';O=BASE/'report_snapshots/progress-v11-inputs'
def main():
    assert not O.exists()
    prior=json.loads((BASE/'report_snapshots/progress-v10.json').read_text())
    assert sha_file(R)==prior['report_pointer']['sha256'] and sha_file(S)==prior['state_pointer']['sha256']
    names=[
      'C/E02/fresh/C-E02-R7/common_raw_only_source_input_v1.json',
      'C/E02/fresh/C-E02-R7/role_A2_raw_only_manifest_v1.json',
      'C/E02/fresh/C-E02-R7/raw_acquisition_terminal_manifest.v2.json',
      'C/E02/stages/batches/C-E02-R7/G5_FRESH_HOLDOUT_ACQUIRE.json',
      'C/E02/stages/batches/C-E02-R7/fresh_source_input_manifest.json',
      'epochs/C-E02/epoch_state.v6.json',
      'SS/E02_design/new_source_A4_v1/role_A4_fixed_manifest.json',
      'SS/E02_design/new_source_A4_acceptor_supplement_v1/role_A4_acceptor_supplement_manifest.json',
      'SS/E02_design/new_source_A5_v1/role_A5_manifest.json',
      'SS/E02_design/new_source_A3_metadata_corroboration_v2/role_A3_manifest.json',
      'SS/E02_design/new_source_actual_exposure_custodian_v3/permanent_exposure_manifest.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/independent_table_value_reconciliation.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/independent_graph_reconciliation.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/bounded_reconciliation_checks.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/qualified_design_source_support.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/A6_summary.json',
      'SS/E02_design/new_source_A6_reconciliation_v3/role_A6_manifest.json',
      'SS/E02_design/new_source_A6_reconciliation_failure_v1/failure.json',
      'SS/E02_design/new_source_A6_reconciliation_failure_v2/failure.json',
      'SS/E02_design/new_source_locations_v1/common_raw_only_locator_input_v1.json',
      'SS/E02_design/new_source_locations_v1/role_A2_fixed_raw_only_locator_manifest.json',
      'report_audit/progress-v10-A12-v1/A12_bounded_documentary_validation_v1.json',
      'report_audit/progress-v10-A12-v1/role_A12_manifest.json',
      'report_snapshots/progress-v11-budget-prefix.json']
    for n in names:assert (BASE/n).is_file(),n
    bdoc=json.loads((BASE/names[-1]).read_text());b=bdoc['totals'];f=bdoc['families']
    assert b['HTTP']==779 and b['bytes']==1152366332
    archives={};inputs={}
    for label,p in [('prior_report_archive',R),('prior_state_archive',S)]:
        q=O/('progress-v10-'+p.name);write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p);archives[label]=pointer(q)
    for n in names:
        p=BASE/n;q=O/'evidence'/n;write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p)
        inputs[str(p.relative_to(ROOT))]=dict(sha256=sha_file(p),physical_archive=pointer(q))
    text=R.read_text()
    def sub(a,z):
        nonlocal text
        assert text.count(a)==1,(a,text.count(a));text=text.replace(a,z)
    sub('report_snapshots/progress-v10.json','report_snapshots/progress-v11.json')
    sub('现已实际冻结R1–R5五个G5分支','现已实际冻结R1–R5及R7六个G5分支')
    sub('SS仅SS-E01曾冻结并已incomplete，SS-E02仍source-first设计；2来源支持同1受体，尚无G2/G3/G4。','SS仅SS-E01曾冻结并已incomplete，SS-E02仍source-first设计；旧UDP-apiose/7-O-Glc层2来源支持同1受体，新flavonol3-O-Gal/O2/UDP-glucose层新增1个Kgal→K2设计支持、同层仍仅1受体；两层不合并，尚无G2/G3/G4。')
    sub('最新C epoch_state.v5绑定R5 A6和第四G6','最新C epoch_state.v6绑定第六G5及R5 A6和第四G6')
    sub('C-E02的R1–R5均已在各自首次化学抽取前实际G5冻结','C-E02的R1–R5及R7均在各自首次化学抽取前实际G5冻结；R7当前仅原件冻结、独立化学提取待开始')
    sub('future-fresh已按R1–R5采集原件或记录访问延后','future-fresh已按R1–R5及R7采集原件或记录访问延后')
    sub('SS第二受体补核现在完成：17 raw共同输入','SS第二受体旧17raw补核完成：17 raw共同输入')
    sub('3个focus均defer、新支持0，现支持仍同1受体；','该旧17raw的3个focus均defer、新支持0，旧UDP-apiose层支持仍同1受体；')
    old=next(x for x in text.splitlines() if x.startswith('18. **预算。**'))
    sub(old,'18. **预算。** 搜索仍107/600=91真MCTS+16fixture，107terminal/0pending，工程32/60。追加物理前缀截至2026-10-10T02:24:24.074504+00:00：779 HTTP、1,152,366,332 bytes；C441/111,234,738B，SS334/1,041,097,672B，root4/33,922B；附件146请求，失败或redirect174。article-version旧口径86、含original_pdf扩展口径93，均为请求类别而非有效论文数；SS expanded33请求不能称33篇有效原件。快照保存真实采集窗口及prefix SHA，旧702/586/533/497等快照不改写。总8000HTTP/8GiB、家族2500HTTP/2GiB等硬预算不变；无本轮科学MCTS，外部工具不可观测HTTP单列。全局来源disposition/闭包/最终分母仍pending，不宣称饱和。')
    sub('SS现有2支持仍同1受体；第二受体原图双独立转写和来源特定供体补充已完成。','SS旧UDP-apiose/7-O-Glc层2支持仍同1受体；其旧第二受体原图双独立转写和来源特定供体补充已完成。')
    sub('更广SS公开一手来源发现继续，先固定raw，再做新双抽取。','另一路新SS来源双抽取/A6现已固定，新Kgal→K2支持单列于flavonol3-O-Gal/O2/UDP-glucose层；不能把两个不同底物/糖/位点上下文合并为一个范围的两受体。')
    start=text.index('SS新raw-only包73计划/73HTTP/73terminal')
    end=text.index('\n\n独立A12 progress-v9',start)
    text=text[:start]+'''SS新raw-only包73计划/73HTTP/73terminal、36,813,720B；173 metadata occurrences、12 source-associated条目中，取得3个完整来源的6个XML/PDF版本和31原始附件，另外9条缺完整一手正文。共同81 raw SHA为73响应（含失败）加8既有官方donor数据库原响应，后8仅身份参考。A3原件3/3身份通过；后追加Fg1/Fg4/Catharanthus三条MED/Crossref元数据身份，不能升级为全文反应资格。A3初版editor/ISSN与字段计数失败按历史保留。A4固定77文件、A4 Kgal补充9文件、A5固定86文件；173元数据occurrences由A5复算为148唯一DOI/数据库ID，口径分别保留。A0 v3实际绑定12来源科学design暴露，其中7仅摘要、3全文+2SI，未知首读时间保持null，全部future-fresh排除；原v2没有把未读全文一概曝光，后续摘要实际读取有独立证据，不能倒填旧计划。\n\n新SS A6 v3完成13项bounded检查：K2与Kgal完整canonical/Standard及FixedH InChI、糖碳立体和MolBlock往返双轨一致；官方UDP-glucose CID8629全图匹配来源Fig2E/body16实际donor名，9碳立体中心完整，两个potential-P未指定只作为工具诊断；实际盐/反离子/水合/质子化unknown，未自动中性化。Standard InChI尿嘧啶keto/lactim往返改变精确共价图的真实差异保留，FixedH保持原图。46实际assay测量格、43peak×3=129字段、52ordinal格字面一致；66组织丰度格中62初始一致、4处A4转录差异，root查看SI原图物理p3逐格裁定A5吻合，原A4四值和失败v2不改。52格的B+superscript四残基标签显式映射为A4后缀，未把不同酶合并。9ND/2SD零的丰度与4ND的ordinal均不改写为缺失/0；数值格、表达量和峰字段均不当反应数。初始v1脚本SyntaxError与v2真实检查失败及全部部分输出物理保留，v3仅新增结果。\n\n番茄来源正文16与Fig2E明确recombinant79-B用Kgal+UDP-glucose产生K2、79-A阴性；正文10的分离植物峰MS+Petunia提取物RT/UV比对、SI S1B完整图和同标签enzyme产品形成实际来源身份链。A6授予1条设计source-support，Kgal C21H20O11→K2 C27H30O16、beta-D-Glc-(1→2)-beta-D-Gal、GalO2位点，非独立化学验证或human_reviewed。两个原始parent611.1594/611.1597及作者neutral610.1521保留，按既有0.01Da转写门通过不叫质谱QC；449.1073/465.1009碎片冲突、Fig2F把Kgal写glucoside、S1A质子化片段均独立保留。Qgal→Q2作者说法与whole-pollen Fig6D阳性保留，但未完成单独79B assay及实际donor/步数的完整图链，不计第二受体。新层支持仍1受体，旧api7Glc/UDP-apiose层另1受体；无SS G2/G3/G4、无fresh。其余来源科学字段与完整screening宇宙尚pending，不把本bounded核对当完整化学round或饱和。\n\nC-R7原件包52HTTP/25,193,994B全部terminal，228元数据dispositions守恒；9 source闭包中3来源取得27可用原件，分别6/13/8。v1容器magic未识别DOCTYPE开头的3XML，v2实际结构解析修正，原件字节不变。第六G5绑定原G4 SHA、全19名字hypotheses、旧曝光与新SS custodian v3；新契约以真实时间补足晚暴露绑定，旧queryplan/pending说明不覆写。G5之后已启动独立A4，A5等待可用agent槽位后以同一raw启动，A3只核出版身份；当前尚无本轮A6/G6资格、0fresh。SS另9来源locator补核25HTTP/1,790,037B全部terminal：17metadata+8原件请求，新增完整正文/SI均0；2个200仅coredata、authorize/429/403/TLS失败保留，未绕过登录或把访问失败当化学不存在。\n\n独立A12 progress-v10为26pass/0current fail/8inherited pending、0未处理请求文档项，803输入SHA/15输出、24物理归档、19prefix/702HTTP原响应字节逐项核对。审计以v10原asof为准，不用之后SS A5/A6或R7状态反向判当时pending为错误。v9真实误写v12输入4655仍保留；v10正确4849，v11旧审计4655。独立A11新SS bounded核对已分派，目前pending，不提前声称通过。
'''+text[end:]
    text+='\n- progress-v11：新SS双轨/A6固定、13bounded checks，Kgal→K2新增1设计支持且同层仍仅1受体；4丰度转录差异及Standard InChI互变异构差异已按实际原图/FixedH裁定并保留失败。C-R7第六G5/52HTTP/3来源27原件，独立A3/A4/A5待核；SS locator25HTTP/0新全文。A12v10 26pass/8pending与779HTTP真实asof绑定，fresh0、科学0/null、P2仍开。\n'
    state=S.read_text();oldp=next(x for x in state.splitlines() if x.startswith('TASK-016-P7（'))
    newp='TASK-016-P7（2026-10-10 CST）：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)及[执行中报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md) **In Progress**，agent_delegated。C/SS E01 incomplete保留；C-E02 C6/2受体/10负控/C3-H G4 SHA不变。R1–R5及R7六G5，R1/R3/R4/R5四G6，fresh0；R7 52HTTP/3来源27原件已冻结，同raw独立A3/A4/A5待核。R5双轨81测量+18表达/五产物立体中心A4未完成与原RT/mass冲突保留，旧目标图命中已拒绝；R6访问补核0原件。SS新A4/A5/A6已固定，13bounded checks，新Kgal+UDP-glucose→K2设计支持1条；新flavonol3Gal-O2层1受体，旧api7Glc-UDPapiose层2支持仍1受体，两个strata不合并，无SS G2+。4组织丰度转录分歧原图裁定/旧值及两失败保留，UDPglucose Standard互变异构与FixedH原图分开，实际盐未知不自动中性化。SS locator另25HTTP/0新全文；12来源实际科学design暴露含7摘要，首读unknown不倒填。两轴G7/G8、新bank G9未成，科学A/B/E0cell、metricsnull。旧221全量、187+34无资产限历史144文件，新增8intake+4alias单测单列；107terminal=91real16fixture/工程32。物理预算02:24:24UTC 779HTTP/1,152,366,332B，扩展article93/附件146均请求数。A12v10 26pass/0fail/8pending/803inputs15outputs，v9真实失败保留；新SS A11待核。最新progress-v11，P2/formal/release未关闭，未commit/push/tag/release。'
    assert state.count(oldp)==1;state=state.replace(oldp,newp)
    oldnext=next(x for x in state.splitlines() if x.startswith('下一步：继续已批准TASK-016-P7。'))
    newnext='下一步：继续已批准TASK-016-P7。C-R7必须在第六G5后同raw独立A3/A4/A5并A6核对原件/完整图/旧曝光及all19名字闭包，设计图不当fresh。SS沿各精确stratum补第二不同合格受体，Kgal新层不得跟旧api7Glc层合并；保持实际source-product链门、不加通用NMR/标准品/纯化酶门。独立A11核新SS当前包，后续来源分母/真实预算继续守恒，不把metadata或访问失败当完整化学round/饱和。每scope两受体、完整重放/负控/生产guard后才建bank及freeze；各≥6完整可执行fresh/≥2组、100%适用零泄漏后才真实A/B/E与净增益/零loss/三seed节点迁移。新科学资产变化后完整工程/历史回归，冲突/失败/零保留。'
    assert state.count(oldnext)==1;state=state.replace(oldnext,newnext)
    write(TASK,str(R.relative_to(ROOT)),text);write(TASK,str(S.relative_to(ROOT)),state)
    snap=dict(task=TASK,approval_type='agent_delegated',revision='progress-v11',created_at=now(),parent_snapshot=pointer(BASE/'report_snapshots/progress-v10.json'),report_pointer=pointer(R),state_pointer=pointer(S),**archives,inputs=inputs,G5_batches=6,G6_batches=4,C_R7_A3_A4_A5_pending=True,SS_new_qualified_design_supports=1,SS_new_distinct_acceptors_in_flavonol3Gal_O2_stratum=1,SS_old_distinct_acceptors_in_api7Glc_UDPapiose_stratum=1,scope_strata_merged=False,SS_G2_created=False,SS_A6_checks_passed=13,SS_abundance_source_adjudicated_differences=4,A12_v10=dict(passed=26,failed=0,pending=8),A11_new_SS_pending=True,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,goal_completed=False,human_reviewed=False,source_chemical_saturation=False,budget_pointer=pointer(BASE/'report_snapshots/progress-v11-budget-prefix.json'))
    p=BASE/'report_snapshots/progress-v11.json';immutable_json(p,snap)
    print(json.dumps(dict(snapshot=pointer(p),report=pointer(R),state=pointer(S),physical_evidence_archives=len(inputs),goal_completed=False)))
if __name__=='__main__':main()

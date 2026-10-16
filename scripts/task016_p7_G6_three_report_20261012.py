"""Finalize official P7 three-targeted G6 rulings; no simulated fresh promotion."""
from pathlib import Path
import json,hashlib,datetime,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from operate import write,event
T='TASK-016-P7';B=Path('outputs/task016-p7/v1');O=B/'G6_three_decisions_20261012_v1'
SNAP=B/'report_snapshots/progress-G6-three-rulings-v1.json'
REPORT=Path('docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md')
STATE=Path('STATE.md')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def rd(p):return json.loads((ROOT/p).read_text())
def ptr(p):return {'path':str(p),'sha256':sha(p)}
def main():
 if (ROOT/SNAP).exists():raise RuntimeError('final snapshot already exists')
 paths={
  'A6_name':O/'A6_isoorientin_name_only_formal_ruling.json',
  'C_A4_graph':O/'C_PMC13564134_A4_PubChem_property_full_graph.json',
  'C_A5_graph':O/'C_PMC13564134_A5_PubChem_atom_record_full_graph.json',
  'C_A6_final':O/'C_PMC13564134_A6_dual_structure_and_exact_build_closure_ruling.json',
  'C_G6_corrected':O/'C-PMC13564134-G6-corrected/stages/G6_IDENTITY_STRUCTURE_ADMIT.json',
  'Iris_SI':O/'source10_Iris_SI_to_main_original_linkage_ruling.json',
  'Pea_O2':O/'source14_Pisum_inner_sugar_O2_original_ruling.json',
  'A11':O/'A11_three_workstreams_independent_raw_verification.json',
  'raw_HTTP':O/'C_PubChem_raw_HTTP_receipts.json',
  'exposure':O/'C_PMC13564134_permanent_graph_exposure.jsonl',
  'epoch_ledger':B/'epoch_ledger.jsonl',
  'budget':B/'report_snapshots/progress-G6-three-rulings-physical-budget.json'}
 a=rd(paths['A11']);c=rd(paths['C_A6_final']);budget=rd(paths['budget'])
 assert a['passed']==305 and a['failed']==0
 assert c['dual_molecular_structure_complete'] and c['static_only_scope_applicability_complete_reference']
 assert c['EXACT_FROZEN_BUILD_REACTION_LEAKAGE'] and not c['fresh_eligible']
 assert rd(paths['Iris_SI'])['official_citation_DOI_confirmed']
 assert rd(paths['Pea_O2'])['site_inner_sugar_O2_source_confirmed'] is False
 assert budget['totals']['HTTP']==1265 and budget['totals']['bytes']==1244352674
 logrel=None
 for line in reversed((ROOT/'operations/events.jsonl').read_text().splitlines()):
  try:e=json.loads(line)
  except Exception:continue
  if e.get('action')=='command_end' and e.get('task')==T and 'unittest' in ' '.join(e.get('argv',[])):
   if e.get('returncode')!=0:raise RuntimeError('latest tests failed')
   logrel=Path(e['log']);break
 assert logrel is not None
 log=(ROOT/logrel).read_text()
 assert 'Ran 286 tests' in log and '\nOK' in log
 old=rd(B/'report_snapshots/progress-reaction-ledger-v1.json')
 assert old['fresh_C']==old['fresh_SS']==0
 snapshot={'task':T,'as_of':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'phase':'G6_three_targeted_evidence_dispositions_complete_G6_global_still_in_progress',
  'G4_C_SHA':sha(B/'C/E02/stages/G4_SCOPE_FREEZE.json'),
  'G4_SS_SHA':sha(B/'SS/E02/stages/G4_SCOPE_FREEZE.json'),
  'three_workstreams_decision_finished':True,'human_reviewed':False,
  'isoorientin_name_exposure':{'physical_instances':36,'distinct_records_by_exposure_id':12,'name_only_automatically_reject_fresh':False,
    'no_structure_site_in_old_name_rows':True},
  'C_PMC13564134':{'original_article_A3_verified':True,
    'PubChem_CIDs':{'luteolin':5280445,'isoorientin':114776,'UDP-glucose':8629},
    'PubChem_new_HTTP200':6,'independent_A4_A5_full_graphs_reconciled':True,
    'product_sugar_absolute_stereo_confirmed':True,'reference_precursors_complete':True,
    'static_frozen_scope_reconstructs_reference':True,'exact_build_match':'C-CHRYSIN-LU6',
    'fresh_eligible':False,'decision':'REJECTED_FROM_FRESH_AS_EXACT_BUILD_REPLAY'},
  'Iris_source10':{'official_PMCID':'PMC13422134','DOI':'10.1002/cbic.70486',
    'official_article_SI_link_proven':True,'provided_PDF_bit_identical_to_original':False,
    'binary_claim_status':'not verified, not disproven','chemical_C6_fresh':False},
  'Pisum_source14':{'original_DOI':'10.1515/znc-1979-9-1014',
    'O2_atom_level_linkage_in_original_confirmed':False,'decision':'DEFERRED_NOT_ESTABLISHED',
    'source_historical_not_fresh':True},
  'G6_new_full_dual_graph_verified_count':1,'G6_full_accepted_fresh_reaction_count':0,
  'G6_global_completed':False,'fresh_C':0,'fresh_SS':0,
  'G7_panel_real':False,'G8_real':False,'new_G9':False,
  'scientific_ABE_cells':0,'metrics':None,
  'A11_independent_checks':305,'A11_failed':0,
  'new_HTTP':6,'new_download_bytes':59099,'physical_HTTP':1265,'physical_bytes':1244352674,
  'regression_tests':286,'regression_failures':0,'regression_errors':0,
  'regression_log':str(logrel),'regression_log_SHA':sha(logrel),
  'G7_writer_all_new_exposure_supplements_bound':False,
  'roadmap_P2_completed':False,'git_committed_or_pushed':False,
  'evidence':{k:ptr(v) for k,v in paths.items()}}
 assert snapshot['G4_C_SHA']=='09bee632a3ced321885ddda6460f13a15f5658d513c807cbea3f9fec2718ed46'
 assert snapshot['G4_SS_SHA']=='a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f'
 write(T,str(SNAP),json.dumps(snapshot,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
 header='## 2026-10-12：G6 三项专项裁定正式收口（three-rulings-v1）'
 report=f"""
{header}

本轮执行所有者明确要求的三项科学资格工作，使用预注册 SHA 输入、源 HTML/PDF、官方 PubChem 原始结构 JSON 和 A11 独立重算。两轴 G4 冻结原SHA、MCTS 和模型配置不变；正式 G7 writer 对补充的所有人工和本次新化学曝光尚需硬绑定。

一、isoorientin 名称级曝光 A6 正式裁定：在三本已有 SS-E01 曝光账中独立核对36行实例，按 exposure_id 去重12条不同 biological_endpoint；这些条目仅记录 Buckwheat2018 Table3 的总 C-glucosylflavones analyte 与可能化合物名称，不含目标/受体/供体分子图、成键位点或反应签名。裁定 NAME_ONLY_IS_NOT_STRUCTURE_SITE_REACTION_LEAKAGE，即这些名字本身不能自动排除或自动放行 fresh；保留旧记录不篡改。但完整 C 反应是否无泄漏仍须检查。

二、PMC13564134 完整 C6 原子图与独立 A4/A5 成功、A6 检出独立于名字的确定性泄漏。为原文所指 GyCGT1 luteolin + UDP-glucose -> isoorientin one-step C6 葡糖基化，预注册 PubChem 三个源名字六个 REST 原件（6/6 HTTP200；59,099 bytes）：luteolin CID5280445、isoorientin CID114776、UDP-glucose CID8629。A4 独立读取 PubChem property 立体 SMILES，A5 独立解析另一份 PC_Compound 原子/键表与 Absolute SMILES，项目原有结构 harness.reconcile 返回 structure_complete=true、reference_precursor_complete=true。产物结构 C21H20O11、C6-C1 键和(2S,3R,4R,5S,6R) 糖立体核对；源原子 AIDs 产品芳香 C6=17、糖基 C1=14、供体 UDP-Glc 异头 C1=30、O-P连接O=7。已冻结 C-E02 范围静态还原到完整 luteolin+UDP-glucose 参考前体（2个有效结果）。然而重新从 C/E02/build_supports.json 原始冻结 build 同时比对三张立体分子图，准确命中早已用于 scope 设计的 C-CHRYSIN-LU6；原有 assert_zero_leakage 实际抛出 build/holdout closure leakage。因此 2026 原文虽然身份新颖、全结构及静态适用性通过，反应本身不是独立 fresh，正式 REJECTED_FROM_FRESH_AS_EXACT_BUILD_REPLAY。保留先前 G6 原文仅文本的阶段冻结，另在 G6_three_decisions_20261012_v1/C-PMC13564134-G6-corrected 写入新的完整结构但无fresh的SHA链；epoch_ledger仅追加、不重写旧版本。新结构阅读记为永久曝光，今后不得洗为新 holdout。

三、10号 Iris SI 来源正式裁定：原有官方缓存 PMC13422134 HTML citation title/DOI 10.1002/cbic.70486 和明确的 SI 地址 CBIC-27-e70486-s001.pdf；早先下载的广告资产计划也指向该官方附件；所有者 12页 SI 内标题 UGT707B2/Iris tectorum，Fig S1–S6、Table S3 能闭合文章家庭关联。故 SI -> 主文章归属已高置信度证实；但官方 SI URL 以前实际返回 recaptcha HTML 而非同一二进制 PDF，不能伪称用户提供的 PDF 与官网逐字节一致，也不能据此通过 C6化学资格。

四、14号豌豆糖链位置证据裁定：从既有已保管原版4页直接复核可证明 UDP-glucose/粗酶使 kaempferol、quercetin 出现3-O单/双/三葡糖苷，不能直接定位新增糖基连接在内层糖 O2、确认(1->2)或核准完整糖立体。正式 disposition=DEFERRED_NOT_ESTABLISHED_IN_ORIGINAL_1979_PDF，禁止从三葡糖苷名称猜 O2 或错误地否定全文所有反应。该历史源亦不得当 fresh。

独立 A11 实际重算原始曝光行、PDF、官方 SI 页、6份原始结构、A4/A5和 frozen build：305/305 pass、0 fail；全量规范虚拟环境测试286/286 OK（{logrel}）、git diff --check 通过。新增 6 HTTP / 59,099 B；最新物理账共1,265 HTTP / 1,244,352,674 B。当前可确认完整 A4/A5 结构图1条，但就是旧 exact build，合格 fresh C/SS 仍0/0，科学全反应 G6准入0，真实G7面板无、科学A/B/E0、metrics=null、TASK-016-P7 和 Roadmap P2仍In Progress；没有Git提交/推送。机器真相快照：outputs/task016-p7/v1/report_snapshots/progress-G6-three-rulings-v1.json。
"""
 if header in (ROOT/REPORT).read_text():raise RuntimeError('report repeated')
 write(T,str(REPORT),(ROOT/REPORT).read_text().rstrip()+'\n\n'+report.strip()+'\n')
 state=f"""
2026-10-12 TASK-016-P7 G6 三专项裁定已执行（progress-G6-three-rulings-v1）：① A6 复核 isoorientin 名字曝光36物理行/12 distinct，缺反应图及位点，名称自身不自动阻断或准入；② PMC13564134官方 PubChem CIDs 5280445/114776/8629 共6 HTTP 取得完整接受体/产物/供体和立体，A4/A5独立完整结构比较、C6-C1键、reference precursor及冻结C6 scope静态适用均pass；A6与冻结 build support C-CHRYSIN-LU6受体、供体、产物图 EXACT匹配，属于真实结构级泄漏，明确不得fresh；③ 10号 Iris PMC13422134 正文确有官方SI链接，与owner SI标题及S1-S6吻合但官方二进制尚未同SHA；14号1979豌豆原文不支持推定内糖O2位点，证据deferred。A11 305/305, 规范全量单测286/286（{logrel}），物理预算1265 HTTP/1,244,352,674 B。G4原SHA不变，永久图曝光登记、有效G6新修正分支和epoch追加；G6 full fresh reaction准入0，fresh C=0/SS=0，G7尚无真实面板，A/B/E=0, metrics null，P7/P2 In Progress，未Git提交推送。
"""
 write(T,str(STATE),(ROOT/STATE).read_text().rstrip()+'\n\n'+state.strip()+'\n')
 event(T,'P7_G6_three_workstreams_science_report_sync',snapshot_sha=sha(SNAP),A11=305,tests=286,
  fresh_C=0,fresh_SS=0)
 print(json.dumps({'snapshot':str(SNAP),'report_and_STATE_updated':True,'A11':305,'tests':286,
  'budget_HTTP':1265,'fresh_C':0,'fresh_SS':0},ensure_ascii=False))
if __name__=='__main__':main()

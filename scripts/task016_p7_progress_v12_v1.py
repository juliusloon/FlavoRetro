"""Progress v12: close new raw evidence, preserve actual verification failures and interruption."""
import json
from scripts.operate import write
from scripts.task016_p7_orchestrate import ROOT,TASK,now,sha_file
from scripts.task016_p7_c_e02_http import BASE,immutable_json
from scripts.task016_p7_c_e02_fresh import pointer
R=ROOT/'docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md';S=ROOT/'STATE.md';O=BASE/'report_snapshots/progress-v12-inputs'
def main():
 assert not O.exists()
 prev=BASE/'report_snapshots/progress-v11.json';prior=json.loads(prev.read_text())
 assert sha_file(R)==prior['report_pointer']['sha256'] and sha_file(S)==prior['state_pointer']['sha256']
 names=[
 'report_snapshots/root-post-progress-v11-quota-interruption.json',
 'report_snapshots/progress-v11-R7-stale-description-correction.json',
 'C/E02/fresh/C-E02-R7/root_A3_publication_identity_v2/A3_summary.json',
 'C/E02/fresh/C-E02-R7/root_A3_publication_identity_v2/role_A3_manifest.json',
 'C/E02/fresh/C-E02-R7/root_A3_publication_identity_failure_v1/failure.json',
 'C/E02/fresh/C-E02-R7/source_exposure_custodian_v1/permanent_exposure_manifest.json',
 'C/E02/fresh/C-E02-R7-A3/v1/root_verified_query_conservation.json',
 'verification-v14-newSS-bounded/independent_verification.json',
 'verification-v14-newSS-bounded/role_A11_independent_manifest.json',
 'verification-v14-newSS-bounded-root-followup/failed_check_counterevidence.json',
 'SS/E02_design/reference_discovery_r2/preregistered_locator_plan.json',
 'SS/E02_design/reference_discovery_r2/metadata_query_conservation.json',
 'SS/E02_design/reference_discovery_r2/complete_metadata_occurrence_dispositions.json',
 'SS/E02_design/reference_discovery_r2/prechemical_read_allocation.json',
 'SS/E02_design/reference_discovery_r2/originals/official_byte_execution.v2.json',
 'SS/E02_design/reference_discovery_r2/A3_publication_identity_v1/A3_summary.json',
 'SS/E02_design/reference_discovery_r2/A3_publication_identity_v1/role_A3_manifest.json',
 'SS/E02_design/reference_discovery_r2/raw_closeout_v1/raw_only_source_intake_manifest.json',
 'SS/E02_design/reference_discovery_r2/raw_closeout_v1/Petunia_only_design_common_raw_input.json',
 'SS/E02_design/reference_discovery_r2/raw_closeout_v1/role_A2_raw_only_intake_manifest.json',
 'report_snapshots/progress-v12-data-Git-exclusion.json',
 'report_snapshots/progress-v12-budget-prefix.json']
 for n in names:assert (BASE/n).is_file(),n
 bdoc=json.loads((BASE/names[-1]).read_text());b=bdoc['totals'];assert b['HTTP']==876 and b['bytes']==1193598167
 archive={};inputs={}
 for label,p in [('prior_report_archive',R),('prior_state_archive',S)]:
  q=O/('progress-v11-'+p.name);write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p);archive[label]=pointer(q)
 for n in names:
  p=BASE/n;q=O/'evidence'/n;write(TASK,str(q.relative_to(ROOT)),p.read_text());assert sha_file(q)==sha_file(p)
  inputs[str(p.relative_to(ROOT))]=dict(sha256=sha_file(p),physical_archive=pointer(q))
 text=R.read_text()
 def sub(a,z):
  nonlocal text
  assert text.count(a)==1,(a,text.count(a));text=text.replace(a,z)
 sub('report_snapshots/progress-v11.json','report_snapshots/progress-v12.json')
 sub('R7当前仅原件冻结、独立化学提取待开始','R7的A4已于G5后实际读取3来源，角色抽取未固定；A5启动/结果待核')
 sub('G5之后已启动独立A4，A5等待可用agent槽位后以同一raw启动，A3只核出版身份；当前尚无本轮A6/G6资格、0fresh。','G5后A4实际于02:28UTC读取3来源，后额度中止、尚无固定角色结果；A5先前槽位限制未启动，现已重发启动请求，实际开读/结果待核。root独立A3仅解析3份原JATS front与官方MED，3/3出版身份通过、6其余来源原件身份pending；未读C化学正文。并行A3另7个官方Crossref查询在02:28UTC实际完成、125,745B，7计划/7HTTP/7terminal，原件计数不增加、独立A3 final role未固定。当前无本轮A6/G6资格、0fresh。')
 sub('独立A11新SS bounded核对已分派，目前pending，不提前声称通过。','独立A11新SS bounded v14已留下固定结果：4pass/1fail/5pending，不能称整体通过。失败为其断言旧A6 v2汇总字段raw_literal_differences必须有4条，而当时该字段为空；4条真实分歧实际完整保存在records的same=false行。root追加反证指针与哈希、保留原A11失败，待原角色独立复核，未由root改写独立审计结果。该4pass涵盖固定SHA/293字段、全图表示诊断与来源链/精确stratum；既不等于独立化学验证，也不关闭其他pending。')
 old=next(x for x in text.splitlines() if x.startswith('18. **预算。**'))
 sub(old,'18. **预算。** 搜索仍107/600=91真MCTS+16fixture，107terminal/0pending，工程32/60。最新物理前缀截至2026-10-10T06:12:28.828513+00:00：876 HTTP、1,193,598,167 bytes；C448/111,360,483B，SS424/1,082,203,762B，root4/33,922B；附件204请求，失败或redirect180。article-version旧口径98、含original_pdf扩展口径105，均是请求类别；SS expanded45不能称45篇有效原件。新增由C A3实际7metadata与SS参考链90HTTP构成，真实时间与旧779/702等快照分别保留，不追填当时预算。总8000HTTP/8GiB、家族2500HTTP/2GiB/200附件等硬预算不变，SS附件实际149尚未触上限；外部工具不可观测HTTP单列。完整来源分母/科学循环仍pending，不宣称饱和。')
 marker='\n## 执行中修订记录'
 assert text.count(marker)==1
 extra='''

SS参考链新一轮raw包已关闭：3类路线8 metadata请求/180occurrences（分页截断与未选择记录逐项保留），6个新PMCID对应6 XML正文、6主PDF版本、58附件，共70可用原件对象；随后12原件/元数据请求、6官方PMC OA object-index查询和64实际广告bytes请求，总90HTTP/41,106,090B全部terminal。所有原始响应SHA、实际计划/执行ID和字节均守恒。6个旧NCBI www OA元数据URL返回404仍保留；官方公开S3 index实际给出资源Key和ETag后才下载，未猜SI地址、未绕访问限制。Petunia EPS为DOS binary EPS头，v1 ASCII detector误标other；v2按真实header offset/length及%!PS section、原size/MD5/SHA核对修正，原错误结果不改、0额外HTTP。6份JATS front与官方MED逐项出版身份6/6通过，作者顺序与缺字段/不同日期语义保留，PDF未另核。

化学读取前已冻结allocation：仅PMC5856881（Petunia UGT79B31）分配设计双抽取；其10原件与既有官方UDP-glucose参考构成独立共同raw输入。其他PMC4494776/PMC4762388/PMC9786081/PMC12313340/PMC10940802五份保持科学正文/图未读，只有metadata/front及容器/字节检查；不保证future-fresh资格，也不提前排除后续严格零泄漏核对。两轨不得读取另外五份科学内容，须scope冻结后的适当输入锁或明确重新分配design后才能读；不得因已下载或标题含酶名就计支持。新SS设计来源资格仍只有上一轮Kgal→K2那1条同层受体，Petunia目前0科学资格，SS G2+未成。

本轮root实际恢复时钟05:53UTC，先前三个agent以quota错误终态退出，具体quota起点/持续时间未知，无过程在运行、未宣称该间隔完成工作。C A4只有部分真实读出，A5未有固定结果，原A11失败保留；root继续完成A3、原件采集和归档，未把root自检冒充独立角色。progress-v11条目4“R7独立抽取待开始”是过时文字，与其后A4已启动段矛盾；此版依据真实02:28首次读出更正，旧REPORT/STATE及66项有限自检保留，后者未覆盖此文字一致性。科学矩阵仍0/null，目标未完成。
'''
 text=text.replace(marker,extra+marker)
 text+='\n- progress-v12：C-R7 root A3原件front身份3/3、并行7元数据HTTP守恒，A4部分读出/角色未固定、A5启动结果待核；保留quota中断及v11过时文字更正。A11v14 4pass/1fail/5pending，失败反证另存、不改独立结果。SS参考链90HTTP关闭、6来源12正文版本58附件，6front身份通过；仅Petunia分配design双抽取、其他5正文图保持未读，无新增科学支持。876HTTP真实asof，fresh0/科学0/null/P2仍开。\n'
 state=S.read_text();oldp=next(x for x in state.splitlines() if x.startswith('TASK-016-P7（'))
 newp='TASK-016-P7（2026-10-10 CST）：[合同](docs/tasks/TASK-016-P7-domain-aligned-transfer-closure.md)及[执行中报告](docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md) **In Progress**，agent_delegated。C/SS E01 incomplete保留；C-E02 C6/2受体/10负控/C3-H G4 SHA不变，六G5/四G6/fresh0。R7 52HTTP/3来源27原件G5冻结；A4实际读3来源后quota中止、尚未fixed，A5启动结果待核；root A3原件JATS front身份3/3、其余6原件身份pending，并行A3另7metadata HTTP已守恒但角色未固定。R5双轨/A6固定且0fresh、原立体转录缺口与RT/mass冲突保留，R6无原件。SS新A6 1条Kgal→K2设计支持，flavonol3Gal-O2-UDPGlc同层仅1受体；旧api7Glc-UDPapiose层2支持仍1受体，不合并，无SS G2+。独立A11v14 4pass/1fail/5pending：v2汇总字段断言失败，实际四分歧记录反证已另存待独立复核，原失败不改。参考链新90HTTP/6来源12正文版本58附件全部terminal，6JATS出版身份通过；仅Petunia10原件分配设计双抽取、其余5科学正文图未读，不预授fresh资格。4丰度转录差异/Standard互变异构/原碎片冲突/盐未知与失败全保留。G7/G8/新bankG9未成，科学A/B/E0cell、metricsnull。旧221全量及187+34无资产限历史144文件，新增8intake+4alias单测单列；107terminal=91real16fixture/工程32。预算06:12:28UTC 876HTTP/1,193,598,167B，扩展article105/附件204为请求数，SS附件149未触200上限。A12v10 26pass/0fail/8pending仍仅原asof；最新progress-v12，quota真实时间不倒填，P2/formal/release未关闭，未commit/push/tag/release。'
 assert state.count(oldp)==1;state=state.replace(oldp,newp)
 oldnext=next(x for x in state.splitlines() if x.startswith('下一步：继续已批准TASK-016-P7。'))
 newnext='下一步：继续已批准TASK-016-P7。C-R7从实际quota中断处恢复独立A4/A5，以既有G5和同raw完成A6；不得重复HTTP或读取对方输出，root A3只有出版身份。独立A11原角色复核v14失败反证并新增版本，原失败保留。SS仅Petunia common raw白名单设计双抽取以补精确stratum第二受体，另5未读原件维持隔离、不能当已资格或同域反应；metadata-only hint可保留但后续fresh仍须scope先冻、零build/source闭包、完整图及运行时适用。达到每scope两受体/100%重放/负控/生产guard后才建bank/freeze；两轴≥6完整可执行fresh/≥2组后真实A/B/E、净增益/零loss/三seed迁移与完整工程历史验证。未满足合同停止条件，不以访问失败/metadata未选或quota中断声称来源饱和。'
 assert state.count(oldnext)==1;state=state.replace(oldnext,newnext)
 write(TASK,str(R.relative_to(ROOT)),text);write(TASK,str(S.relative_to(ROOT)),state)
 snap=dict(task=TASK,revision='progress-v12',created_at=now(),approval_type='agent_delegated',human_reviewed=False,parent_snapshot=pointer(prev),report_pointer=pointer(R),state_pointer=pointer(S),**archive,inputs=inputs,G5_batches=6,G6_batches=4,C_R7_original_front_identity_passed=3,C_R7_A4_partial_not_fixed=True,C_R7_A5_start_or_result_pending=True,C_R7_parallel_A3_HTTP=7,SS_reference_round_HTTP=90,SS_reference_round_original_sources=6,SS_reference_round_XML_versions=6,SS_reference_round_PDF_versions=6,SS_reference_round_attachments=58,SS_reference_round_publication_front_passed=6,SS_reference_design_whitelist=['PMC5856881'],SS_reference_other5_scientifically_unread=True,SS_new_qualified_design_supports=1,SS_strata_not_merged=True,SS_G2_created=False,A11_v14=dict(passed=4,failed=1,pending=5),A11_failed_check_counterevidence_pending_independent_review=True,stale_v11_R7_text_corrected_history_preserved=True,fresh_C=0,fresh_SS=0,scientific_ABE_cells=0,metrics=None,goal_completed=False,source_chemical_saturation=False,budget_pointer=pointer(BASE/'report_snapshots/progress-v12-budget-prefix.json'))
 p=BASE/'report_snapshots/progress-v12.json';immutable_json(p,snap)
 print(json.dumps(dict(snapshot=pointer(p),report=pointer(R),state=pointer(S),physical_evidence_archives=len(inputs),goal_completed=False)))
if __name__=='__main__':main()

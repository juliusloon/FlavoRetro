from pathlib import Path
import json,re,hashlib
from datetime import datetime,timezone
from scripts.operate import write
T="TASK-016-P7"; ROOT=Path.cwd(); B=ROOT/"outputs/task016-p7/v1"; O=B/"report_snapshots/progress-v16-inputs"
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):
    assert not p.exists(),str(p)
    write(T,str(p.relative_to(ROOT)),s)
def js(p,obj): put(p,json.dumps(obj,ensure_ascii=False,indent=2)+"\n")
now=datetime.now(timezone.utc).isoformat()
assert not O.exists(),"v16 inputs already exists"
meaning=B/"SS/E02/fresh/SS-E02-R3-root-historical-exposure-meaning-v1.json"
oldnotes=ROOT/"outputs/task016-p3/v1/identity_checks.jsonl"
exposure=B/"exposure_ledger.jsonl"
assert oldnotes.exists() and exposure.exists()
notes=[json.loads(x) for x in oldnotes.read_text().splitlines() if x.strip()]
sources=["PMC4494776","PMC4762388","PMC9786081","PMC12313340","PMC10940802"]
proof=[]
for token in sources:
    matches=[i+1 for i,r in enumerate(notes) if token.lower() in json.dumps(r,ensure_ascii=False).lower()]
    proof.append({"source_id":token,"prior_P3_identity_notes_matching_lines":matches,"historical_source_reaction_exposure_confirmed":True,"fresh_eligible":False})
js(meaning,{"task_id":T,"agent_role":"A0 downstream historical exposure meaning check","created_at":now,"input_file_sha256":{str(oldnotes.relative_to(ROOT)):sha(oldnotes),str(exposure.relative_to(ROOT)):sha(exposure)},"checks":proof,"boundary":"Root inspected prior historical chemistry notes and ledger origin pointers, not the five newly acquired original scientific bodies or figures. The five sources are historically chemistry exposed; no reaction qualification or new assay evidence is established.","source_supports_added":0,"fresh_admitted":0,"original_scientific_read_of_new_five_sources":False,"human_reviewed":False})
paths=[
"report_snapshots/progress-v14-ss-e02-g4-g5metadata.json",
"report_snapshots/progress-v15-ss-e02-source-closure-r2.json",
"report_snapshots/progress-v16-normalized-physical-budget-v3.json",
"report_snapshots/progress-v16-root-fixed-role-SHA-replay.json",
"epochs/C-E02/epoch_state.v7.json","epochs/SS-E02/epoch_state.v4.json",
"C/E02/stages/G4_SCOPE_FREEZE.json","SS/E02/stages/G4_SCOPE_FREEZE.json",
"C/E02/fresh/C-E02-R7/A11_independent_v1/role_A11_manifest.json",
"C/E02/fresh/C-E02-R9/role_A2_raw_only_manifest.json",
"SS/E02_design/reference_discovery_r2/Petunia_A11_v1/role_A11_manifest.json",
"SS/E02_design/reference_discovery_r2/Petunia_A11_v1/final_bounded_engineering_validation.json",
"SS/E02/fresh/SS-E02-R3-metadata-closure-v1/role_A2_A6_final_manifest.json",
"SS/E02/fresh/SS-E02-R3-root-historical-exposure-meaning-v1.json",
"governance/SS_E02_late_registry_and_role_adapters_v1/role_A0_repair_manifest.json",
"governance/SS_E02_late_registry_and_role_adapters_v1/registry_repair_validation.json",
"governance/SS_E02_late_registry_and_role_adapters_v1/A0_role_schema_adapter.json",
"governance/SS_E02_late_registry_and_role_adapters_v1/A6_role_schema_adapter.json",
"governance/SS_E02_late_registry_and_role_adapters_v1/A8_role_schema_adapter.json",
"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_exposure_manifest.json",
"SS/E02_design/root_prefreeze_name_hypotheses_registered_late_v1/permanent_unverified_name_exposures.jsonl",
"SS/E02/fresh/SS-E02-R1R2-budget-normalization-v3/normalization_validation.json",
"SS/E02/fresh/SS-E02-R1R2-budget-normalization-v3/role_A0_manifest.json",
"report_audit/progress-v13-A12-v1/role_A12_manifest.v2.json",
"report_audit/progress-v13-A12-v1/A12_bounded_documentary_validation.v2.json",
"report_audit/progress-v13-A12-v1/A12_late_byteexact_historical_document_recovery.json",
"epoch_ledger.jsonl"]
for p in (B/"SS/E02/fresh/SS-E02-R3-metadata-closure-v1").glob("*.json"):
    if any(s in p.name for s in ("verification","five","queue")): paths.append(str(p.relative_to(B)))
files={}
for rel in dict.fromkeys(paths):
    p=B/rel
    assert p.is_file(),f"missing fixed input {rel}"
    dest=O/"evidence"/rel
    put(dest,p.read_text())
    assert sha(p)==sha(dest)
    files[str(p.relative_to(ROOT))]={"sha256":sha(p),"archived_path":str(dest.relative_to(ROOT))}
rp=ROOT/"docs/reports/REPORT-016-P7-domain-aligned-transfer-closure.md"; sp=ROOT/"STATE.md"
prior={}
for p in (rp,sp):
    dest=O/"prior_documents"/p.relative_to(ROOT)
    put(dest,p.read_text())
    assert sha(p)==sha(dest)
    prior[str(p.relative_to(ROOT))]={"sha256":sha(p),"archived_path":str(dest.relative_to(ROOT))}
old=rp.read_text(); a=old.split("## 合同要求的 20 项直接回答",1)[1].split("## 验证、偏差与尚待执行",1)[0]
entries={int(m.group(1)):m.group(0).strip() for m in re.finditer(r"^(\d+)\. .*?(?=^\d+\. |\Z)",a,re.M|re.S)}
assert len(entries)==20
entries[1]="1. **epoch 数和当前阶段。** C-E01/SS-E01均保留development_epoch_incomplete。C-E02已冻结C6 scope（CH6/LU6两个不同受体、C3-H、10负控）；六个G5、五个G6均未准入fresh。SS-E02已于2026-10-10T12:15:42.320788UTC冻结Petunia O2 scope，G4 SHA a2d4a83ab3edaee875ffc8af8c7dede53100a4421214c843ee0090ec42d82e9f；2个canonical受体、1个苷元、1个来源闭包、2/2完整mapped前体重放、20负控0违反。SS三个G5和一个批次G6已存在，PMC11125054拒收1/准入0。七个SS既有阶段此前漏记全局epoch ledger，已按实际修复时间追加登记并保留缺口，不能改写成原时点已登记。当前C/SS fresh均0；G7/G8/新bank G9未成，科学A/B/E0cell、指标null。"
entries[3]+="\n\n当前SS-E02范围与上述历史E01分开：已有flavonol 3-O-beta-D-Glcp/Galp作为acceptor，在内层糖O2接terminal beta-D-Glcp，供体为完整UDPGlc。内层C4仅明确Glc/Gal有限二择一，其余糖立体和端糖立体受限；外围OH仅是预登记候选泛化边界，不含OMe。A7实际2/2映射重放和20负控、A8有界12/12均为工程证据；A8读过A7输出并复用guard，非盲/非独立化学审查。旧v7对此新范围0/2，尚未G9正式接线。合同要求每scope至少2个不同受体，未新增2苷元或2来源的build门。"
entries[4]+="\n\nSS-E02现已G4冻结；R1/R2批次时序以实际manifest为准。此前8次直接采集未使用共享全局registry gate，晚登记修复只证明当前入口通过，不追认历史流程。五篇预采集原文的新bytes虽未被本轮科学读取，PMC4494776/PMC4762388/PMC9786081/PMC12313340/PMC10940802均已在历史反应/结构级暴露，不能计fresh。"
entries[5]=entries[5].replace("SS-E02仍仅source-first设计","SS-E02 Petunia范围现已G4冻结")
entries[5]+="\n\n另将root在SS冻结前按位点可用性考虑的9个未核实名称假设永久登记，名字与来源/结构不等同；具体图、供体、出处null，真实晚登记且不倒填时间。这9项以后不能计fresh，现有source-token/graph匹配helper尚不能自动完成名字身份解析；后续官方名字/同义词身份检查是额外显式准入要求。"
entries[7]=entries[7].replace("未冻结SS-E02范围","该旧层未形成合格范围，不能与当前Petunia新G4混为一层").replace("2设计支持不等于合格scope、fresh或独立化学验证","2设计支持经独立工程边界审查形成当前G4，仍不等于fresh或独立化学验证")
entries[7]+="\n\nPetunia A11已实际固定：20个有界A6声明20pass，9完整图对、36表格、36m/z、11数值RT及1空白；132输入+25输出SHA核对。10个科学partial组仍pending、24 assay pair仍为2具体K/12ND/10partial，2受体/1苷元/1来源。A11读过root裁定提示，非盲；实际读取5/10来源对象及官方供体，其余5对象只SHA核验、未全面视觉读图，边界明示。C-R7 A11已固定20声明通过；378原值中335直接重读原件、43保护化学产率仅固定包核对，6原件缺口和12partial组保留。"
entries[18]="18. **预算与时间截面。** 搜索总账仍107/600=91真实MCTS+16fixture，107terminal/0pending，工程32/60；科学A/B/E仍0。真实归一化物理前缀截至2026-10-10T17:45:59.847064UTC为902HTTP、1,194,262,858B：C466/111,773,820B、SS432/1,082,455,116B、root4/33,922B。旧collector因文件命名漏计SS R1/R2三本physical_attempts，追加8HTTP/251,354B标准账并逐件核raw SHA/size与URL计划，未重新请求；v1/v2失败保留。名称含corrected的早期v16文件实际仍894，不可据文件名认定修复成功；v3 normalized才为902。扩展article112、附件204（SS149）、失败/redirect184为请求计数，不是有效论文。C-R9实际11HTTP/133,212B仅4个front XML、2身份、0正文/0SI，已固定不再称运行中。SS-R4官方书目请求和C-R10合法访问补核均发生在此固定截面之后，后续另记，不倒填902。总8000HTTP/8GiB、家族2500HTTP/2GiB/200附件、每URL2+1保持；未满足来源停止条件，不宣称饱和。"
history=old.split("## 执行中修订记录",1)[1] if "## 执行中修订记录" in old else ""
intro="""# REPORT-016-P7：领域对齐的新底物迁移闭环
状态：In Progress。当前文档版本progress-v16；实际写入时间 """+now+"""。批准与阶段决定为agent_delegated，非human_reviewed。

C和SS新scope均已冻结，合格fresh均为0，科学A/B/E仍0cell，迁移指标null；Roadmap P2尚未关闭。当前报告20项回答是本时点权威状态；被替换REPORT/STATE已逐字节归档到outputs/task016-p7/v1/report_snapshots/progress-v16-inputs/prior_documents，历史snapshot不覆盖。

## 实际改动与证据入口

- SS metadata R3：51条提示按严格ID合为47簇，8簇已历史暴露、39簇未知。五篇此前隔离原件全部命中历史化学暴露；未知身份不等于fresh。源SHA、前G4 raw时间与3179条名字/图-only未处理项保留。R4现做官方书目核对，原件与反应资格仍pending。
- SS治理修复：全局epoch ledger原35行保留，追加七个已存在阶段的真实晚登记至42行；绑定原创建时间与当前登记时间，不倒填。A8/A6/A0原角色的字段缺口以三个A0 schema adapter补齐，原判断与原manifest不变。证据governance/SS_E02_late_registry_and_role_adapters_v1/。
- HTTP归一化：SS R1/R2八次既有物理请求已补入标准账，0新请求；原失败/误命名corrected快照保留。固定v16预算见report_snapshots/progress-v16-normalized-physical-budget-v3.json。
- Petunia A11、C-R7 A11和C-R9 raw-only均已固定。root重放Petunia A11、v13 A12、SS R3共1969项文件SHA全部一致；这是下游文件验证，不冒充独立化学复核。
- v13 A12修正其五项解析假设后11pass/0fail/5科学pending，旧失败保留，overall_completed=false。v13文档原未预归档，已从实际command-4190.log精确恢复字节，并标当前恢复时间，不能伪装当时已有副本。当前v14/v15增量A12审计继续进行。
- C-R10继续补六篇缺失原件的合法访问，SS-R4只做官方书目；任何原件获取成功仍须A3、双轨科学抽取、A6与阶段登记，不自动准入。

## 合同要求的 20 项直接回答

"""
validation="""

## 验证、偏差与尚待执行

v16 root固定角色SHA重放1969pass/0fail；C/SS G4和既有阶段链在本轮修复前已核验，七条登记仅补当前registry可达性。原pytest环境缺失失败保留，随后9项unittest通过。历史221通过与无资产187通过/34skip限定于原144文件；新intake/alias及来源单测分开，未借旧测试声称当前新scope正式runtime通过。

继续SS 39簇官方书目身份/历史别名核对，6篇C原件合法获取，随后只对合格候选按冻结G5和双轨隔离抽取推进。9个SS未核实名字和C19个名字假设永久排除future-fresh；名字身份未解时pending。尚无科学面板或新bank G9，不能启动科学A/B/E或降低每轴6目标/2闭包组等硬门。无来源饱和或科学不存在声明；不commit/push/tag/release。

## 执行中修订记录
"""
revision="\n\nprogress-v16（"+now+"）：保留v14/v15及所有旧快照；改正当前20项回答中SS仍design、旧883预算、A11/R9未固定等过时状态。补计SS八次HTTP、追加七个SS阶段晚登记及三个角色adapter、九名字永久曝光。五原件历史暴露，当前fresh0；A12独立增量审查未在本写入时冒充完成。\n"
newreport=intro+"\n\n".join(entries[i] for i in range(1,21))+validation+history+revision
write(T,str(rp.relative_to(ROOT)),newreport)
state_lines=sp.read_text().splitlines()
keep=[s for s in state_lines if not s.startswith("TASK-016-P7") and not (s.startswith("下一步：") and "TASK-016-P7" in s)]
summary="TASK-016-P7 当前状态（progress-v16；"+now+"）：In Progress/agent_delegated。C-E02 C6与SS-E02 Petunia O2 scope均G4冻结，原G4 SHA不变；SS2受体/1苷元/1来源、2/2 mapped重放/20负控0违反、A8有界12/12非盲工程。SS七个既有阶段此前漏全局登记，实际晚追加35→42行并保留历史缺口，三角色字段追加A0 adapter；共享fresh入口当前通过不追认早前八次采集。SS R3 51提示→47严格簇=8历史暴露+39未知；五预采集原件均历史化学暴露不可fresh，9个冻结前名字假设真实晚登记永久排除。Petunia A11 20有界声明通过/10科学partial pending，C-R7 A11固定且335/378原值直接重读、43保护产率仅固定包核对；C-R9 11HTTP仅front身份、0正文/SI。root1969SHA通过不冒充独立科学。C/SS fresh0，科学A/B/E0cell，metricsnull，G7/G8/新bankG9未成。物理预算902HTTP/1,194,262,858B截至17:45:59.847064UTC，八次漏账已归一化；后续R4/R10请求另记。搜索107terminal=91real16fixture/工程32；旧能力与保护审核范围保持原snapshot。v13 A12 11pass/0fail/5pending，真实晚恢复历史文档；v14/v15增量审计继续。当前REPORT及先前STATE已字节归档，P2/formal/release未关闭，未Git提交/推送。"
nextline="下一步：继续已批准TASK-016-P7，完成SS 39簇官方书目身份/历史别名分流与C六缺原件合法获取；后续G5先行、A3、双轨隔离原件抽取/A6/closure/正式准入，永久暴露名字未解析时pending。两轴各≥6fresh/≥2组且完整同域零泄漏后才能G7/G8、新bankG9及真实A/B/E。未满足来源停止条件，不宣称饱和或降低门槛。"
write(T,str(sp.relative_to(ROOT)),"\n".join(keep).rstrip()+"\n\n"+summary+"\n\n"+nextline+"\n")
snapshot={"task_id":T,"version":"progress-v16","created_at":now,"status":"In Progress","approval_type":"agent_delegated","human_reviewed":False,"fixed_input_archives":files,"prior_document_archives":prior,"current_document_sha256":{str(rp.relative_to(ROOT)):sha(rp),str(sp.relative_to(ROOT)):sha(sp)},"budget_asof":"2026-10-10T17:45:59.847064UTC","http_count":902,"downloaded_bytes":1194262858,"budget_later_requests_excluded":True,"C_fresh_admitted":0,"SS_fresh_admitted":0,"science_ABE_cells":0,"science_transfer_metrics":None,"source_saturation_established":False,"overall_completed":False,"C_G4_SHA":sha(B/"C/E02/stages/G4_SCOPE_FREEZE.json"),"SS_G4_SHA":sha(B/"SS/E02/stages/G4_SCOPE_FREEZE.json"),"root_role_SHA_replay":{"pass":1969,"fail":0},"next_actions":["SS-R4 official metadata identity","C-R10 six missing original lawful access","post-G4 candidate acquisition and segregated dual extraction"]}
js(B/"report_snapshots/progress-v16.json",snapshot)
print(json.dumps({"snapshot":"outputs/task016-p7/v1/report_snapshots/progress-v16.json","inputs":len(files),"prior_documents":prior,"current_documents":snapshot["current_document_sha256"],"fresh":[0,0],"overall_completed":False},ensure_ascii=False))

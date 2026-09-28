# REPORT-015：ORD 实际覆盖与开发审核卡片

## 对应任务

- 任务 ID：TASK-015；[合同](../tasks/TASK-015-ord-coverage-review-cards.md)。
- 状态：Completed（授权的覆盖实测与审核准备完成；实际人工审核、开发 gold 未执行）。
- 所有者批准：2026-09-27 “好，开做”，human_direct 工程执行授权；预算内范围细化记录 agent_delegated，不是 human_reviewed。
- 基线：main / fab9659b10dfd89ca348d48dc855fd9ac1a91092；此前 TASK-013/014 及范围外改动保留。
- 结果提交：未提交、未推送；没有新 PR 或 CI 运行。

## 实际改动

1. 冻结 ORD 官方 Hugging Face 镜像 revision `93475c46949f9218e1dfb6624096025135db2add`，完整下载 53 个当前 Parquet，共 1,256,526,213 字节；每个 LFS SHA-256/大小均匹配。完整扫描 2,428,291 条来源记录，8,509 条命中 9 母核领域查询，2,418,536 条未命中、1,246 条因结构问题无法判断；另有 1 条结构不完整但领域命中的候选保留。来源副本、失败、零、缺失未删除或补猜。
2. 8,508 条完整候选严格归一为 6,013 个精确反应组；78 条领域糖苷候选为 65 组。糖苷来自 USPTO 汇总 69 条、上游训练集 8 条、验证集 1 条，其余当前镜像数据集未命中糖苷候选。上游训练/验证/测试标签原样保存，在项目中均 development_exposed，训练重叠 unknown。原始 sources/procedure/outcomes 与 protobuf 字节定位保留，未加入 active v3 或 MCTS。
3. 同一连通组分内芳基 O 连接在 ORD 75 条记录任一侧出现，芳基 C 仅 1 条底物侧、0 条产物侧；这些是现规则的拓扑命中，不是化学缺失或生成反应结论。本地试点已有 744 条领域糖苷候选，含 227 条芳基 C 候选。严格与本地试点重合 3 组（ORD 4 行），糖苷重合 1 组；未重合的 64 个糖苷组不据此升级为独立实例或训练独立。
4. 现有 60 条样本生成本地离线 SVG 反应/审核卡，保持原样本/标注 null 与来源哈希，支持 30 糖苷重点/抽样层/填写状态/题名 ID 筛选、保存草稿、导入导出、修订历史；浏览器持久存储受限时保留内存草稿并可导出备份。按协议区分结构初筛与具体来源核对，禁止不完整记录选择 primary_checked；全部导出仍 user_submitted_unvalidated / production_eligible=false，需要另行验证，不能直接充当 human_reviewed 或 gold。
5. 47 个文献标题中 32 个匹配 DOI 导航（30 个标题/年份匹配、1 个由 SI 元数据定位正文、1 个标题变体并核对年/卷/首个页码/首作者），11 个原导出专利号仅作导航，4 个身份待核对。Crossref 12 个首轮 429 失败与候选不匹配均保留；一次节流重试后没有未处理查询失败。60 条仅 12 条导出实验步骤，30 糖苷重点中 9 条有步骤；导出步骤均非原文核验。未下载论文正文/SI，未使用机构浏览器或商业数据库账号。nature-academic-search 用于出处核对；nature-downloader 边界用于开放材料获取方案，本次只提供材料入口而未下载正文/SI。
6. 首批 SciFinder 材料清单缩为 4 个已有文献条目，重点核对 C-糖苷、酶促 C 实例、flavonol 3-O 与身份待核对的 hesperidin 衍生物；提供 RDF/原件/PDF/检索记录/审核 JSON 的本地接收目录与责任分工，不要求重新搜全量。公开论文元数据与受限反应内容严格区分，全部本地载荷被 Git 忽略。

完整计数、字段适用范围与官方源见 [ORD 覆盖实测](../protocols/ORD_COVERAGE_V1.md)，具体人工动作与 4 条材料见 [定向检索/导入](../protocols/SCIFINDER_TARGETED_IMPORT_V1.md)。

## 改动文件

| 目录职责 | 文件 | 用途 |
| --- | --- | --- |
| 治理合同 / 历史报告 | TASK-015-ord-coverage-review-cards.md、REPORT-015-ord-coverage-review-cards.md | 人工授权、预算内细化、验收、实际结果与未处理科学缺口 |
| 项目当前登记 | STATE.md、ARCHITECTURE.md、docs/README.md、tasks/README.md、reports/README.md、protocols/README.md、两路线文档 | 更新当前 TASK-015 为覆盖/审核准备；gold 与 P2/正式门槛仍未闭合 |
| 来源与接管规范 | docs/protocols/ORD_COVERAGE_V1.md、SCIFINDER_TARGETED_IMPORT_V1.md | 全镜像范围、候选/去重/失效语义、4 条检索与接收格式 |
| 独立环境元数据 | environment/task015-ord-schema.json | 官方生成 protobuf 冻结 commit/内容哈希与实际版本；非完整 ord-schema 安装 |
| 离线卡片实现 | flavoretro/review_cards.py、scripts/build_review_cards.py | 原始结构 SVG、原始事实/机器建议/人工草稿分开，离线 HTML；不接运行服务 |
| 开放源读取 | scripts/setup_ord_schema.py、fetch_ord.py、scan_ord.py、survey_ord_mirror.py | 隔离冻结 schema；LFS 校验、每源逐行扫描、53 源预算内读取，4 工作进程 |
| 元数据导航与汇总 | scripts/review_references.py、refine_review_references.py、summarize_ord_coverage.py | Crossref 身份候选与限流保全；当前镜像/严格重合/糖苷副本统计 |
| 验收 | scripts/check_review_cards.py、audit_ord_coverage.py、tests/test_ord_coverage.py | 浏览器卡片/导入负例、原始行/哈希/计数/受保护文件、5 条字段保全合同 |
| 本地原件（不上 Git） | data/raw/ord/task015/ | 53 个 Parquet、来源清单、许可、镜像说明；约 1.26 GB |
| 本地扫描（不上 Git） | outputs/coverage/task015-full/、task015-mirror/、task015-summary/ | 原始记录全部保留；候选/unknown/统计/定位/哈希；78 糖苷 TSV/JSONL |
| 本地最终卡片（不上 Git） | outputs/review/task015-v2/、task015-replay-v2/ | index.html、summary、manifest；最终目录另有 scifinder-targets.json；三个核心文件独立重放逐字节一致 |
| 开发版本（保留） | outputs/review/task015/、task015-final/、task015-ready/、task015-v1/、task015-replay/，outputs/coverage/task015-smoke/ | 早期卡片/元数据版本与 2 行组扫描试验；不能与最终完整结果混用 |
| 验收证据（不上 Git） | outputs/validation/task015-audit.json、task015-card-replay-v2.json、task015-cards-v2-pass/、task015-closeout.json | 53 源哈希、25 行原件绑定、197 受保护文件、桌面/移动截图及 fixture 验证；完成摘要 |
| 用户材料接收（不上 Git） | data/inbox/scifinder/task015-user/ | 仅创建说明文件，等待合法原始导出/正文/SI/审核 JSON；本次没有假造用户输入 |
| 操作审计 | operations/events.jsonl、command-*.log、task015-baseline.json | 全命令与写入追踪、失败保全、受保护基线；日志/基线不上 Git |

## 验证

| 检查 | 结果 |
| --- | --- |
| 53 源大小 / SHA-256 与镜像 LFS | 53/53 通过；1,256,526,213 字节 |
| 逐源 Parquet footer / 完整行组 / 逐行 disposition | 53/53 全量；2,428,291 = 8,509 + 2,418,536 + 1,246 |
| candidates / unknown 原始行数与摘要、各 manifest 输出 | 全部吻合；原始 hash 再核一致 |
| 源行/protobuf SHA/id/专利抽样绑定 | 25 项通过，含明确零收率；是工程绑定核查，非化学抽样验证 |
| TASK-014/v3/已有资源/代码/UI 保护哈希 | 197 个文件不变；不是对整个历史目录重做全面审计 |
| `.venv-foundation/bin/python -B -m unittest discover -s tests -v` | 67/67 通过；新 5 项含零/缺失、失败保全、角色/回退、断开组分、映射原值保留 |
| check_review_cards.py 最终 index.html | 60 卡全显示；筛选/保存/导出/合法导入通过，错误源/输入哈希和不完整 primary_checked 拒绝；存储失败仍导出草稿通过 |
| 桌面 1440、手机 390/320 | 横向溢出全 false，JavaScript 错误 0；截图为新浏览器空白标注，不展示 fixture 为人审 |
| 最终卡片独立重放 | index.html、summary.json、manifest.json 3/3 字节一致 |
| preflight | formal_run_ready/release_ready=false，v3 3,059 条、123 源；production template/stock=0/0 |
| Git 忽略与文档收口 | raw / cards / 扫描载荷 / inbox 均被忽略；新增协议链接与职责登记通过 |

命令均通过 `python -B scripts/operate.py TASK-015 ...`。全量覆盖复核入口 scripts/audit_ord_coverage.py；最终浏览器命令 `... scripts/check_review_cards.py --cards outputs/review/task015-v2/index.html --output outputs/validation/task015-cards-v2-pass`；输出不可覆盖。progress.json 是运行期间快照，最终完成状态以 summary/manifest 为准。

## 与合同的偏差

最初优先 USPTO 汇总。冻结镜像清单证明其余 52 个 Parquet 合计仅约 144 MB，故在 2 GB 原始下载上限内完整核验当前 53 源；修订依据与 agent_delegated 批准已追加到 TASK。与“先覆盖，再卡片，再明确 SciFinder 缺口”的用户授权一致，不扩大为科学准入。

GitHub API 查 schema revision 被限流（403），保留错误；改用公开 git ls-remote 冻结 HEAD，并从固定 commit URL 复核两个生成模块 SHA。Python 3.10 不符合当前完整 ord-schema 的安装要求，故只隔离官方生成 protobuf 解码文件，不升级现有依赖或宣称 SDK 完整安装。

未下载正文/SI，不用登录权限限制代替覆盖统计；卡片明确没有原文。正式化学审核与材料获取是接管步骤，不冒充本次完成。

## 已发现但未修改的问题与遗留风险

9 母核规则可能误收/漏检；拓扑同现不证明键变化。部分候选的量为不合理数据库抽取值、记录可能通式/多实例，未科学修正。某些来源只有反应标识符、缺专利定位/条件/收率；明确组分与标识符一致性未全面核对。严格表示未重合不证明化学新颖或训练独立；上游 ML 数据与 USPTO 可能重叠。文献标题/年份/译本存在差异，未把 metadata_match 当作来源审核。

不生成 gold、盲测或 production；不改变 active/release、MCTS、既有 UI 或模型，不执行新检索/账号登录、不提交推送。原 60 条及已有科学门槛保持原状态。

## 建议的下一步

用户先用 30 条重点卡片做结构初筛，按 4 条定向材料清单核对或提供合法正文/SI/原始导出。收到人工记录后另立来源与标签接管合同，确认审核者、具体实例、分歧和开发 gold 版本；正式盲测需另留独立来源。TASK-016 糖苷感知 MCTS 与 TASK-017 正式评测没有自动授权，不能跳过 gold 或 preflight。

存储失败验证首轮在测试注入处提前抛错：Playwright 自动执行了 evaluate 返回的函数。修正测试脚本让注入返回空值，不改卡片源；失败目录 outputs/validation/task015-cards-v2 保留，完整复验使用新目录 task015-cards-v2-pass。

## 后续澄清（2026-09-27，TASK-015-P1）

[REPORT-015-P1](REPORT-015-P1-agent-review-ord-analysis.md)进一步解释ORD的78条是拓扑候选，含已有糖苷后修饰、背景/配方和领域误命中，不能计作78条糖基化。60条委托代理审核已完成，旧报告与空白人工卡保留历史；最新结果见outputs/review/task015-p1/final-v2。

# REPORT-025：工作台布局、分页与教学反应图

日期2026-10-22（Asia/Shanghai）；状态Completed；批准agent_delegated、human_reviewed=false。对应[事前合同](../tasks/TASK-025-workbench-layout.md)。用户明确要求调整三页长宽、独立滚动、紧凑资源/详情、上下分页、教学互斥栏目与类型反应图，并授权精简重复括号说明。

## 页面变化

| 页面 | 实际交付 |
| --- | --- |
| 路线探索 | 移除全宽顶部标题，介绍只在右栏初始居中展示；左栏紧接header。桌面左右占余下视口，各自滚动，父页面不滚动；加载保存结果后介绍隐藏、结果和比较区显示。手机单列。 |
| 资源与证据 | 全宽独立筛选工具栏，结果区域约58:42的记录/JSON详情；当前条目JSON不改写。行只保留名称/类型/短来源/查看当前条目，记录ID与审核版本在详情。上下分页同源同步，含首/前/页码/后/末、每页10/25/50/100与总数。手机切换记录/详情并转移焦点；选中与未选按钮颜色明确区分。 |
| 文献教学 | 四类各有真实来源的逆合成示例图，原理简短展示、来源细节按需展开。案例/原文/六步/新增反应四栏目互斥，当前栏目分页，其他栏目不堆叠；上下完整分页与页大小同步，跨栏目来源链接能落在对应页并聚焦。 |
| 文案 | 精简header、控制项、连接标签和重复限定语；审核版本、来源范围、图表示、评分与比较说明收进详情。保留有用的候选/未解决状态与原始记录，未改零/缺失/冲突含义。 |

默认每页：资源25、案例5、文献10、练习1步、新反应10。全部27类原理的可选目录也分页。调整筛选或每页数回第一页，各栏目独立记住当前页。六步记录与JSON仍为v1，导出全六步，不因只渲染当前步骤而丢记录。

## 化学配图

四SVG为RDKit依据已有精确实例重新绘制，非AI推测分子结构：

- O：芹菜素7-O-葡萄糖苷 → 芹菜素 + UDP-Glc；10.3390/ijms242317118。
- C：根皮素C-葡萄糖苷 → 根皮素 + UDP-Glc；10.1038/s41467-020-18990-9。
- 糖间：芹菜苷apiin → 芹菜素7-O-葡萄糖苷 + UDP-apiose；10.3390/ijms242317118。
- 母核：黄烷酮2b → 已报道E-2′-羟基查尔酮；10.26554/sti.2025.10.4.1169-1178。

图中双线箭头表示逆合成映射，目标连接深绿高亮，完整UDP供体保留；手机局部横向滑动并有文字提示，可开大图。酶/副产物省略、中性表示、编号差异、未指定C2立体及原文MeOH/EtOH冲突保存在详情。来源DOI、定位、结构SMILES、原记录/来源SHA、许可和图SHA保存在teaching-examples.json；见[配图登记](../TEACHING_EXAMPLES.md)。没有新增模板/库存/准入课程，目录仍32篇/18例。来源许可保留CC BY/CC-BY4.0，原始文件不进入Git。

## 验证与证据

环境：已有Linux/Python3.10/Playwright Chromium；Browser plugin not available。UI概念仅作资源页布局参考，按用户具体要求与既有绿tokens实施；图像概念中的数据不是实际展示数据。设计师和教师角色实际试用后复验，主代理额外校验API/结构/历史结果；这不是人类专家审定。

| 验证 | 结果 |
| --- | --- |
| 页面身份、非空、无错误遮罩 | 正确FlavoRetro URL/title，真实资源/案例内容存在 |
| 路线视口 | 1440×1000左右top76/bottom1000；1440×600左右top76/bottom600；右介绍中心误差<1px。左右实际滚轮互不影响，左到底不串动，docY/mainScroll为0，提交按钮可达 |
| 资源紧凑布局 | 行高57px，原212px；1440宽记录802.7/详情573.3px。低高度600时上下pager各61px，表区161.5px、详情285.5px且底边580可用 |
| 资源分页/详情 | 上下next、跳页、10条末页306/9条、25/50/100条、筛选与reset回页1通过；所选JSON与API逐字段一致，列表没有记录ID/审核块 |
| 教学分页 | 32论文、18案例、54新反应与27原理计数/末页/每页数正确；四栏目互斥；末条案例↔原文跨到目标所在页并聚焦；检索清空恢复 |
| 六步记录 | 默认单步、1/2/3/6每页，真实页码操作、错答刷新、笔记/选择/进度保留；导出包含全6步，审核false保持 |
| 图与手机 | 四图GET200、SVG MIME/SHA正确，所有SMILES解析、来源SHA与跨进程复绘一致。390宽页面无横溢；图330px视口局部900px横滑，前体可见；记录/详情切换与键盘定位复验 |
| 历史/导出 | 显式保存run 20261021T184336-6dfad9124c2e460eaa5cdb303998565e读取、结果替代空态、来源折叠、A/B JSON导出通过；未运行新搜索 |
| 控制台与预算 | 各浏览器检查相关warning/error=0、pageerror=0、POST尝试0，本TASK真实MCTS0 |
| 工程 | 22相关现有测试通过、Node语法与web.py AST通过，8个前端源/包内镜像一致；最终镜像3项重验与git diff --check通过；34配色对通过，栏目实际状态对比至少8.718，无颜色插值过渡 |

主要命令均经scripts/operate.py TASK-025：

```text
.venv-foundation/bin/python -m unittest tests.test_web tests.test_web_foundation tests.test_pipeline_presentation tests.test_package
node --check web/app.js
.venv-foundation/bin/python -m outputs.task025.qa_integration_v2
```

本地证据：designer/before.json与9张基线图；after-routes.json、after-content-v2.json、after-supplement.json及最终焦点/截图；teacher/v3/after-qa.json、final-presentation-qa.json与学习导出；chemist/validation.json、cross-process-validation.json、REPORT.md及四图预览；主代理integration-v2/qa_integration.json验证真实JSON与GET资产、冷链接、历史结果与导出。before/manifest.json与revisions/保存本轮初始及收口前像。最终final-current-qa.json逐项核验当前实际服务字节及6个前端源/镜像首尾SHA，移动焦点/返回与提示通过；最后单个尾空格修订有精确前像映射。final-service-check.json记录两个物理网卡与loopback的9项200、34色对与8镜像。

## 修改文件

- web/index.html、app.js、style.css及flavoretro/assets/web镜像：三页结构、通用分页、选择/焦点、折叠说明。
- web/teaching-examples.json、teaching-example-{o,c,chain,scaffold}.svg及包内镜像：四类实际结构示例及出处。
- flavoretro/web.py：仅扩展五个显式静态GET白名单与JSON/SVG MIME；不开放任意文件路径。
- docs/USER_GUIDE.md、TEACHING_EXAMPLES.md、ARCHITECTURE、STATE、PROGRESS与任务/报告导航：当前入口与证据登记。
- TASK/完成记录、REPORT、outputs/task025/：合同/事实/前像/QA/来源与日志；操作账只追加。

资源页完整概念与最终渲染均已用view_image目视；真实数据/按钮与用户指定结构优先，未照搬概念里的示意数据。沿用原生JS与绿色token，没有引入新框架或依赖。当前工作树原有TASK022—024改动完整保留，未stage/commit/push、未访问执行其他旧库。

## 失败保留与范围

首次服务重启将venv解释器符号链接resolve到裸解释器，缺RDKit而启动失败；失败web.log保留，随后直接用.venv-foundation/bin/python恢复0.0.0.0:8767。没有修改环境或调用别的仓库。教师早期脚本额外dispatch change/旧caption断言失败、设计师reset等待提前、主代理假定真实库有零收率记录导致脚本等待失败均保留；改用真实交互与明确API总数另存复验，未修改应用或数据追认这些失败。当前zerofilter总数实际0、missing1075，未把缺失补零。化学预览初始file协议失败保留，改内嵌SVG渲染后四图目视通过。

本轮改搜索界面但没有重新评估搜索算法或启动MCTS。原有科学、供应、教师、生产门不升级。只测试Chromium桌面/手机尺寸，未验证其他浏览器、真实触摸或屏幕阅读器；未来若改分页/布局需沿用对应真实流程验证。后台局域网服务继续保留，信息见outputs/task025/service.json；已有FlavoGlycoLab8766未触碰。

当前服务PID3334502监听0.0.0.0:8767，访问http://10.70.160.64:8767/或http://10.70.194.126:8767/。其主页、health与四图元数据在本机三个地址均200；其他设备端到端未实测。

# REPORT-041 可独立进入的子页面与浏览器导航

2026-10-24。Completed。审批：agent_delegated，human_reviewed=false。[事前TASK](../tasks/TASK-041-addressable-subpages.md)，[长期决定](../adr/ADR-013-addressable-workbench-navigation.md)。

## 交付

原五个栏目只改变DOM可见性，地址与浏览器历史保持不变，返回因此直接离站。现将五个主入口、教学三个分区及四个工具、具体示例/原理、资源记录、保存运行/路线统一为可独立打开的层级hash子页面。点击产生浏览器历史，返回/前进恢复对应内容；刷新、复制地址、原生Ctrl/Cmd新标签可直接进入。上方当前位置提供上级入口，重复点击同一地址不额外压栈。

筛选、页码/每页数、A/B和来源定位随URL恢复；搜索草稿、显式预算覆盖与高级设置展开保存在当前会话，滚动随历史条目恢复。文献查询输入只替换当前条目，不为每次敲字新增历史。旧`?run=`结果链接仍兼容。只读恢复继续核验保存运行；延迟的运行/对照响应不会拉回旧页或覆盖新选择。缺失资源有可返回提示，无效/越界地址会规范化。

修改web/app.js、index.html、style.css及包内三份镜像。文档新增TASK/REPORT/ADR并更新使用说明、架构、索引、进度和STATE。没有后端API/搜索算法、教学科学正文/结构图、数据/库存或原始运行修改。现有服务无需重启；用户刷新一次旧页面加载新脚本。既有未提交改动保留，没有提交/推送或安装依赖。

## 环境与目标流程

Browser plugin not available，使用已有Playwright Chromium；服务http://127.0.0.1:8767/，LAN http://10.70.160.64:8767/api/health已200。视口1440×1000、390×844、320×844。目标流程为主栏目→功能子页→返回/前进→刷新或新标签重新进入同一内容。

重点闭环：历史第2页→真实保存结果→第2条路线→返回第1条→返回历史第2页；资源筛选第2页→条目详情→刷新→返回原列表；教学示例→筛选文献或来源→返回原示例/案例；草稿与显式预算→跨栏目→刷新→恢复；A/B对照→刷新与延迟读取换页。

## 验收

| 检查 | 结果 |
| --- | --- |
| 页面身份、非空与错误遮罩 | 对应URL/标题及实际内容正确，无框架错误遮罩 |
| 返回、前进、刷新、直接进入 | 五个主入口、教学子页、保存运行/路线及资源详情通过；10种独立新上下文直达地址通过 |
| 筛选、分页、草稿、对照与来源 | 状态恢复、越界回收、上级入口、来源定位无遮挡；禁用会话存储后仍可导航 |
| 键盘、原生链接与截图 | 方向键/Home/End/空格与焦点正确，Ctrl新标签通过；三档无整页横溢，截图检查通过 |
| 异步与滚动 | 延迟现有GET原响应后旧对照不覆盖新选择，旧结果不拉回已离开页面；返回恢复滚动 |
| 控制台与搜索 | 页面异常/错误/警告0，浏览器非GET请求0，真实MCTS新增0 |
| 数量与工程 | 浏览器103主流程＋9补充＋5异步＝117项；18项既有工程测试；23项静态/内容/完整镜像/服务字节/health核验通过 |

现有工程测试覆盖tests.test_package、test_web、test_web_foundation、test_lab_handoff。JS通过Node语法，全部8份web资产与包内逐字节一致；既有SCIENTIFIC_LABELS、EXAMPLE_LESSONS、PRINCIPLE_GUIDES、LEARNING_STEPS、LEARNING_TOPICS正文一致。实际服务返回三份前端字节与源码一致。

命令均经`python3 scripts/operate.py TASK-041`记录：`.venv/bin/python -B /tmp/flavoretro-task041/qa.py`、`supplement.py`、`async_qa.py`；`.venv-foundation/bin/python -B -m unittest tests.test_package tests.test_web tests.test_web_foundation tests.test_lab_handoff`；`node --check web/app.js`、`git diff --check`及只读字节/health检查。调试中发现并修正草稿高级设置引用、直接hash进入的历史state初始化与过期对照响应；最终均已补验通过。

## 证据与边界

基线outputs/task041/before/与baseline.json；最终browser-qa.json、browser-supplement.json、browser-async.json和static-verification.json均在outputs/task041。操作通过operations/events.jsonl以TASK-041定位；临时脚本/截图在/tmp/flavoretro-task041，均不入Git。异步验证只延迟真实GET原响应，是导航工程测试，不生成或改写搜索证据。

只验证Chromium及模拟手机视口，未验证Firefox/Safari或真实触摸设备。搜索表单保留和恢复已验，本轮未提交真实新MCTS。关闭标签会话或禁止会话存储后不保证搜索草稿保留。子页面共用静态壳，地址采用`#`；浏览器返回到本站最初入口之后仍按正常历史离站，不拦截离站。独立化学、供应、教师及生产门保持原状态。

## 截图

桌面：新增位置路径、上级入口与原教学布局共存。

![桌面子页面导航](/tmp/flavoretro-task041/1440-navigation.png)

手机：位置路径与分区导航换行可达，内容无整页横溢。

![手机子页面导航](/tmp/flavoretro-task041/390-navigation.png)

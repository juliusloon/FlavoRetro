# REPORT-036 文献教学顶部区域切换

日期：2026-10-23。状态：Completed。批准：agent_delegated；human_reviewed=false。[事前合同](../tasks/TASK-036-literature-section-tabs.md)。

## 实际变更

文献教学页标题下增加“常见反应类型 / 全部反应原理 / 文献核查与练习”三个导航按钮。默认仅显示常见反应类型；切换时只有对应区域参与显示和页面高度，回到内容起点。导航随页内滚动保持可达，按钮支持方向键、Home和End，选中/焦点及tabpanel关系一致。

原理选择与分页、示例选择、文献筛选、工具栏目和练习记录在区域往返中保留。示例筛选和来源/案例跳转自动揭示文献工具区，目标标题保留导航避让空间。重新加载恢复默认首项，同一页面离开教学再返回保留选择。

改动文件：web/index.html、web/app.js、web/style.css及flavoretro/assets/web/三份对应镜像。教学内容、结构资产、后端、库存和来源数据未改；搜索历史TASK035等既有更改完整保留。

## 验证

Browser plugin not available；使用既有Playwright Chromium，URL http://127.0.0.1:8767，视口1440×1000、390×844、320×844。流程：进入教学→默认首项→切换另外两区→原理选择/分页→文献筛选与来源跳转→练习导出→往返与键盘→刷新默认。

| 检查 | 结果 |
| --- | --- |
| 页面身份、非空、框架错误遮罩 | 通过 |
| 三分区互斥、默认首项、隐藏不占高 | 三视口通过 |
| 键盘、选中态、导航可见与对比度 | 三视口通过；按钮文字对比度≥4.5 |
| 交互保留 | 27原理、筛选空态、示例联动、来源跳转、六步练习记录与导出通过 |
| 视觉截图 | 桌面、手机及320窄屏通过，无全页横溢，来源标题不被导航遮挡 |
| 控制台 | 页面异常/错误/警告0；非GET请求0；真实MCTS 0 |
| 工程 | 116项浏览器检查、6项完整镜像/两份Node语法/diff检查通过 |

关键命令：`.venv/bin/python -B /tmp/flavoretro-task036/qa.py`；`node --check web/app.js`及对应包内app.js；`git diff --check`。运行服务未重启，无依赖安装或Git提交/推送。

## 证据与边界

基线在outputs/task036/before/；逐项浏览器明细在outputs/task036/browser-qa.json；静态核验在outputs/task036/static-verification.json。临时脚本和截图在/tmp/flavoretro-task036/，没有加入Git。操作经scripts/operate.py记录。

首次视觉检查发现主导航通用CSS导致新增按钮未选中文字过浅，已限定分区导航选择器并核对三视口对比度。首次QA误用了新增反应卡片选择器，改为实际paper-card后通过；失败记录保存为outputs/task036/qa-harness-selector-correction.json。没有因测试夹具问题改写教学或来源内容。

仅验证Chromium模拟视口，其他浏览器与真实触摸设备未测试。原理及文献内容的既有科学边界保持；本次验收仅针对区域导航和既有交互。

## 截图

![桌面默认常见反应类型](/tmp/flavoretro-task036/1440-examples.png)
![手机默认常见反应类型](/tmp/flavoretro-task036/390-examples.png)
![全部反应原理](/tmp/flavoretro-task036/1440-principles.png)
![文献核查与练习](/tmp/flavoretro-task036/1440-tools.png)

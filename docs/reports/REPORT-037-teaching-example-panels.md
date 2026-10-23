# REPORT-037 常见反应类型双面板排版

日期：2026-10-23。结果：Completed。批准：agent_delegated；human_reviewed=false。[事前合同](../tasks/TASK-037-teaching-example-panels.md)。

## 实际结果

删除“每类看一个具体文献实例……”说明，四个类型按钮移入“常见反应类型”标题同行右侧并靠右排列。四类示例共用双面板：左约1/3显示标题、引言与三个讲解步骤，右约2/3显示文献方程式、原结构图及图注/完整大图入口。低于1100px改为讲解在上、图式在下；手机按钮分两列，结构图可局部横滑。

删除重复的“图中结构身份 / 产物 / 前体”块及其无用样式。原始JSON/SVG、四类科学解释和原理库内容未改；出处、定位、条件/表示边界与显式文献筛选入口保留在双面板下方。

修改web/index.html、web/app.js、web/style.css及flavoretro/assets/web/对应三文件；沿用现有绿色视觉、顶部三分区及全部其它既有修改。无后端、库存、来源或历史运行变更。

## 验证环境与结果

Browser plugin not available，采用已有Playwright Chromium与http://127.0.0.1:8767，视口1440×1000、1200×900、390×844、320×844。验证流程：文献教学→常见类型→四例逐个选择→左右/上下布局与原图/出处→键盘和快速切换→原理库→显式文献筛选跳转。

| 检查 | 结果 |
| --- | --- |
| 页面身份、非空、错误遮罩 | 正确URL/标题，内容正常，无框架遮罩 |
| 按钮与面板布局 | 两档桌面标题右侧同排且组右对齐，面板宽比约1:2；两档手机换行/堆叠，无全页横溢 |
| 四类内容与交互 | 标题、引言、三步解释、方程式、对应原SVG、图注、出处/边界与大图链接均通过；键盘/快速切换正确 |
| 删除内容 | 指定说明、重复身份块均消失 |
| 现有导航 | 默认常见类型、另两区隐藏、27原理可用、筛选自动打开工具区通过 |
| 控制台 | 页面异常、错误、警告0；非GET请求0；真实MCTS 0 |
| 工程核验 | 150项浏览器检查通过；8项完整镜像/两份Node语法/diff/两组内容原字节核验通过 |

命令：`.venv/bin/python -B /tmp/flavoretro-task037/qa.py`；`node --check web/app.js`及包内app.js；`git diff --check`。完整静态核验见outputs/task037/static-verification.json。既有检查通过后未扩大测试范围。

## 证据与边界

基线outputs/task037/before/，逐项浏览器结果outputs/task037/browser-qa.json；命令与写入通过scripts/operate.py记录。临时QA及截图存/tmp/flavoretro-task037/，未加入Git。服务未重启，无安装、Git提交/推送。四类解释与原理库相对于本轮基线逐字节一致，结构资产没有编辑。

仅验证Chromium模拟视口；其他浏览器、真实触摸设备未验证。此次工程验收不改变任何科学/来源/独立验证状态。

## 截图

![O-糖苷桌面双面板](/tmp/flavoretro-task037/1440-o.png)
![C-糖苷桌面双面板](/tmp/flavoretro-task037/1440-c.png)
![糖间连接桌面双面板](/tmp/flavoretro-task037/1440-chain.png)
![母核构建桌面双面板](/tmp/flavoretro-task037/1440-scaffold.png)
![手机讲解优先排列](/tmp/flavoretro-task037/390-o.png)

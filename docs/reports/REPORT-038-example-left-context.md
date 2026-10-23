# REPORT-038 示例出处与核对说明移入左栏

日期：2026-10-23。结果：Completed。批准：agent_delegated；human_reviewed=false。[事前合同](../tasks/TASK-038-example-left-context.md)。

四类示例共用example-left左栏：讲解卡片之后，独立排列出处、读图核对和文献筛选按钮，三者均在讲解卡片外。核对文字直接排版，右侧方程式/结构图顶部对齐且不被左栏内容拉高。删除“仅点击此按钮才应用下方筛选。”提示，保留来源/DOI/定位、条件冲突和表示边界的原文、按钮原有跳转。

改动web/app.js、web/style.css及flavoretro/assets/web/对应镜像。HTML、SVG/JSON、科学内容、后端、库存与运行数据没有改动；原有三分区导航、右对齐四类型按钮、桌面1:2与手机堆叠保留。

## 验证

Browser plugin not available；使用现有Playwright Chromium与http://127.0.0.1:8767，视口1440×1100、390×844、320×844。流程：文献教学→四类示例分别切换→核对左栏卡片外的内容归属/顺序/原文字段→检查右图与窄屏→实际点击文献筛选跳转。

| 检查 | 结果 |
| --- | --- |
| 页面身份/非空/错误遮罩 | 通过 |
| 左栏内容归属/排列 | 四类、三视口均通过，出处/核对/按钮为讲解卡片同级后续元素 |
| 内容保全与删除 | DOI、定位、源范围、条件/表示原文及原结构图通过；指定提示消失 |
| 布局截图 | 桌面右图顶部对齐且不拉高，手机上下堆叠，无全页横溢 |
| 筛选交互 | 三视口实际点击均显示文献工具区与正确类型 |
| 控制台 | 页面异常/错误/警告0，非GET请求0，真实MCTS 0 |
| 工程 | 80项浏览器检查、8项完整镜像/两份Node语法/diff/内容原字节核验通过 |

命令：`.venv/bin/python -B /tmp/flavoretro-task038/qa.py`；`node --check web/app.js`及包内app.js；`git diff --check`。基线outputs/task038/before/，浏览器明细outputs/task038/browser-qa.json，静态检查outputs/task038/static-verification.json；全部写入/命令经operate记录。临时脚本/截图在/tmp/flavoretro-task038/，未加入Git；没有安装、服务重启、提交或推送。

仅验证Chromium模拟视口，其他浏览器及真实触摸设备未测试。本次为局部排版调整，不改变既有科学/来源状态。

## 截图

![桌面左栏独立出处与核对说明](/tmp/flavoretro-task038/1440-scaffold-panels.png)
![手机左栏排列](/tmp/flavoretro-task038/390-scaffold-left.png)

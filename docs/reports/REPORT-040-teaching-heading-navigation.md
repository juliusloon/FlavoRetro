# REPORT-040 教学导航移入标题行右侧

2026-10-23。Completed；批准agent_delegated，human_reviewed=false。[事前合同](../tasks/TASK-040-teaching-heading-navigation.md)。

将原三个教学导航按钮放入文献教学标题行，标题/说明在左、按钮组在右并靠右对齐；窄屏自动换行，按钮组仍靠右。组合标题栏沿用页内固定能力，并按视口为来源锚点保留避让。默认首项与切换逻辑保持。

修改web/index.html、web/style.css及flavoretro/assets/web/对应两文件，未改JS、科学内容、结构资产、后端或数据；并行TASK039与已有变更保留。

## 验证

Browser plugin not available，使用已有Playwright Chromium，http://127.0.0.1:8767；视口1440×1000、1200×900、768×1024、390×844、320×844。流程为进入教学→标题行布局→三项点击/键盘切换→案例来源跳转。

| 检查 | 结果 |
| --- | --- |
| 页面身份、非空与遮罩 | 正确URL/标题，无错误遮罩 |
| 桌面布局 | 1440/1200按钮组位于标题/说明右侧同排并右对齐 |
| 窄屏与截图 | 768/390/320无页面横溢，按钮可达且靠右 |
| 交互 | 默认首项、三分区互斥、键盘与来源跳转通过；目标不被固定标题栏遮挡 |
| 控制台 | 页面异常/错误/警告0，非GET请求0，真实MCTS 0 |
| 工程 | 54项浏览器与3项相关完整镜像/diff检查通过 |

命令：`.venv/bin/python -B /tmp/flavoretro-task040/qa.py`、`git diff --check`。基线outputs/task040/before/，结果outputs/task040/browser-qa.json和static-verification.json；操作经operate记录。临时脚本/截图在/tmp/flavoretro-task040/，不入Git；没有安装、服务重启或Git提交/推送。其他浏览器及真实触摸设备未测试。

## 截图

![桌面标题行与右侧导航](/tmp/flavoretro-task040/1440-heading.png)
![手机标题与右对齐导航](/tmp/flavoretro-task040/390-heading.png)

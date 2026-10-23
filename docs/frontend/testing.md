# 前端检查与交付

先读取[开发入口](../../web/README.md)。所有命令按活动TASK通过operate记录；浏览器环境使用现有.venv，业务/包测试使用.venv-foundation。无需安装新依赖或重启现有服务。

## 固定检查

```bash
python3 scripts/operate.py TASK-NNN python3 -B scripts/frontend.py check
python3 scripts/operate.py TASK-NNN node --check web/app.js
python3 scripts/operate.py TASK-NNN .venv-foundation/bin/python -B -m unittest tests.test_frontend_project tests.test_package tests.test_web tests.test_web_foundation tests.test_lab_handoff
python3 scripts/operate.py TASK-NNN git diff --check
```

check从源重建内存输出，比较服务三个资产及包内镜像，不写文件；失败时执行build。构建合同测试覆盖确定性、include循环、路径边界、重复DOM ID、路由/模板不一致、重复源、产物漂移、页面生成及面包屑禁入。

## 只读浏览器回归

```bash
python3 scripts/operate.py TASK-NNN .venv/bin/python -B scripts/check_frontend.py --base http://127.0.0.1:8767/ --task TASK-NNN --output /tmp/flavoretro-frontend.json --screenshots /tmp/flavoretro-frontend-shots
```

保持被测主机与目标服务一致；用户LAN服务可将base替换为http://10.70.160.64:8767/。检查1440×1000、768×1024、390×844、320×844：五主页/教学子页/组件页身份与内容，返回/刷新，实际保存结果、资源详情、列表选中、来源原地阅读、练习存储与六步导出，公共分页/按钮/表单、空态/错误语义，顶部间距背景及横溢。脚本阻止非GET并核对本地运行目录无新增。

组件示例只操作隔离浏览器状态，示例条目不是科学记录。读取故障/延迟的专项验证应明确标为工程故障注入，预期HTTP错误单列，不当作真实服务故障或化学验证。

## 交付清单

- 源码、frontend/routes清单和生成资产一致；包内镜像一致。
- 科学正文/条件/来源/未知/零与全量导出保留。
- 无面包屑；教学页原顶部间距由背景覆盖，不能通过去掉间距来隐藏泄露。
- 报告说明实际视口/浏览器、通过项、证据及未测范围；截图/临时脚本放/tmp，摘要按项目约定本地存outputs，不入Git。
- 报告与STATE分别保存执行历史和当前事实；未经请求不提交或推送，不用组件工程结果升级科学门。

# FlavoRetro

黄酮与黄酮糖苷的证据感知逆合成研究工作台。运行能力与研究证据分开验收。

- [项目目标](PROJECT.md) · [当前状态](STATE.md) · [架构](ARCHITECTURE.md)
- [文档导航](docs/README.md) · [人接管指南](docs/HUMAN_TAKEOVER.md) · [论文路线](docs/PAPER_ROADMAP.md)
- [使用说明](docs/USER_GUIDE.md) · [测试合同](docs/TEST_CONTRACTS.md)
- [交接与整理报告](docs/reports/REPORT-008-human-github-handover.md)

## 本机启动

```bash
cd /home/ljx/FlavoRetro
.venv/bin/python -B -m flavoretro.web --host 127.0.0.1 --port 8766
```

浏览器访问 http://127.0.0.1:8766 。默认本机访问；Ctrl+C 停止。

```bash
.venv/bin/python -B -m flavoretro.cli --smiles 'COc1ccc(O)cc1' --mode quick
.venv/bin/python -B -m unittest discover -s tests -v
.venv/bin/python -B -m flavoretro.evaluation --development
```

必须从本仓库 checkout 运行。模型、数据在本地 data/；本机 .venv 使用已安装 retro Python 的只读依赖，浏览器依赖独立安装于新 .venv。新机器重建见 [环境说明](environment/README.md)。本次未发布独立 wheel 或 Docker 镜像。

## 当前定位

工程重建已验收（TASK-001—008）；科学验证仍处 `research_candidate` 阶段：无独立审核库存、无独立化学标签、无正式盲测。已收录的化学条目均为候选，默认无已审核库存；勾选候选库存只允许探索性终止，输出不会把它称为 evidence 或 actionable。数据来源许可未全部清除，原始和派生载荷不进入 Git、不公开发布。

## 仓库与发布状态

Git 初始提交已按"治理文档 / 代码与测试 / 操作与元数据"分层。许可证已确定：代码 [Apache-2.0](LICENSE)，项目原创文档 [CC BY 4.0](LICENSES/CC-BY-4.0.md)，数据保留来源许可且不入 Git，边界见 [LICENSES/README.md](LICENSES/README.md)。仓库尚未连接 GitHub 远程；**发布前**请完成 [论文路线中的检查清单](docs/PAPER_ROADMAP.md)（git 身份、资产边界核对）。

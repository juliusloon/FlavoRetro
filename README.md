# FlavoRetro

黄酮与黄酮糖苷的证据感知逆合成研究工作台。每次普通搜索新建 MCTS；候选、工程验收与化学证据分别呈现。

[项目合同](PROJECT.md) · [当前状态](STATE.md) · [架构与文件职责](ARCHITECTURE.md) · [文档导航](docs/README.md) · [使用说明](docs/USER_GUIDE.md)

## 运行

```bash
# 在项目根目录，使用 TASK-012 建立的独立 Python 3.10 环境
.venv-foundation/bin/python -B -m flavoretro.web --workspace /home/ljx/FlavoRetro --host 127.0.0.1 --port 8766
```

浏览器访问 http://127.0.0.1:8766 。工作台包含路线探索、资源与证据、文献教学、项目状态四页；全部搜索参数、版本/清单、历史运行读取、27 个教学条目浏览与固定 12-cell 开发对照均有界面入口。

```bash
.venv-foundation/bin/python -B -m flavoretro.cli --workspace /home/ljx/FlavoRetro --smiles 'COc1ccc(O)cc1' --mode quick
.venv-foundation/bin/python -B -m unittest discover -s tests -v
.venv-foundation/bin/python -B -m flavoretro.evaluation --workspace /home/ljx/FlavoRetro
```

源码 checkout 与已安装包共用 `--workspace` / `FLAVORETRO_WORKSPACE`。wheel/sdist 包含原创前端和默认配置；原始资源、模型、活动版本、运行与状态文档留在工作区，不写入 site-packages。独立安装、依赖锁与资产恢复见 [环境说明](environment/README.md)。原 `.venv` 保留为历史环境，日常使用 `.venv-foundation`。

## 资源与证据

活动指针为 `metadata/active.json`，当前指向不可变 v3；JSON 是资源事实源，SQLite 是可重建只读查询索引。3,059 条记录与 123 条来源保留原值、冲突、失败与明确缺失；v1/replay-v1/v2 保留。来源文件定位或 token 命中不构成一手化学审核。

系统仍为 `research_candidate`：0 production，无独立化学标签、当前供应审核或正式盲测。候选库存终止仅为 surrogate，`evidence_closed` / `actionable` 保持真实值。全部模型模板的当前 classification 为 `0.0 Unrecognized`，界面明确不能据此确定反应家族。

## 仓库与交付边界

已连接 [GitHub 私有仓库](https://github.com/juliusloon/FlavoRetro)。工程 CI 验证无受限资产的合同、构建与仓库外安装；本地真实 MCTS/浏览器证据单独记录，不能由 CI 跳过项代替。[TASK-012](docs/tasks/TASK-012-foundation-readiness.md) 和 [REPORT-012](docs/reports/REPORT-012-foundation-readiness.md) 给出工程地基范围和验收记录。

代码 [Apache-2.0](LICENSE)，原创文档 [CC BY 4.0](LICENSES/CC-BY-4.0.md)，数据保留来源许可。`data/`、`outputs/`、运行 SQLite、模型和真实运行不进 Git/发布包/CI artifact。私有代码同步不表示公开发布、作者身份发表检查或科学晋级完成；论文准入见 [论文路线](docs/PAPER_ROADMAP.md)。

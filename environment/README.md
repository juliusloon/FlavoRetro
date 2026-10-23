# 独立运行环境与资产恢复

活动环境为 `.venv-foundation`：TASK-012 从独立下载的 CPython 3.10.20 建立，`include-system-site-packages=false`，不读取旧 retro Conda 的 site-packages。原 `.venv` 保留，不再作为交付环境。已验证平台是 Linux x86_64 / Python 3.10；不据此宣称其他平台已通过。

## 文件职责

| 文件 | 用途 |
| --- | --- |
| requirements-linux-py310.lock | TASK-012 新独立环境解析得到的 191 个第三方依赖/构建工具固定版本，不含本机 file:// 路径；应用 wheel 单独安装。 |
| pip-freeze.txt | TASK-001 时的历史环境快照，含旧 Conda 构建路径，保留溯源，不作为新环境安装清单。 |
| ../pyproject.toml | 核心依赖与 Python 范围、verification 可选工具、CLI/Web/数据库入口、包内默认资源规则。 |

## 建环境与安装

已具备独立 Python 3.10 时，用该解释器创建普通 venv，不启用 system-site-packages；也可使用 uv 下载托管 Python：

```bash
uv python install 3.10
uv venv --python 3.10 --managed-python .venv-foundation
uv pip install --python .venv-foundation/bin/python -r environment/requirements-linux-py310.lock
.venv-foundation/bin/python -B -m build --installer uv --outdir outputs/validation/new-build
uv pip install --python .venv-foundation/bin/python --no-deps outputs/validation/new-build/*.whl
.venv-foundation/bin/python -B -m pip check
```

`--outdir` 应每次取新目录。wheel 与 sdist 为本地构建物，当前不上传 PyPI；模型/数据不随包分发。仓库外安装已验证可读取默认配置、静态前端、教学与拓扑；没有资产的状态请求返回明确 503，不能静默从旧目录恢复。

## 工作区与配置

CLI、Web、资源构建器、数据库、评估支持 `--workspace <绝对目录>`，或设 `FLAVORETRO_WORKSPACE`；worker 从父服务继承相同路径。源码 checkout 未指定时采用本 checkout；安装包未指定时采用 `~/.local/share/flavoretro`。生产/公开部署不属于本交付。

`configs/` 为工作区配置覆盖；没有覆盖时使用 wheel 中 `flavoretro/assets/configs/` 的默认配置。`web/` 为编辑源，包内 `assets/web/` 为受控交付副本，`test_package` 校验二者一致，前端始终从包内读取。

## 合法恢复本地资产

新机器须从有权访问的本地备份恢复本项目的 `metadata/sources.json`、`note-relocations.json`、`active.json`、`release.json`，以及该清单对应的 `data/raw/legacy/` 和活动版本 `data/derived/v3/`（records、manifest、SQLite 和 index 清单）。可同时恢复原创配置、STATE 与工程验收元数据。恢复的是本项目本地快照，不要求历史仓库可写，也不在旧目录运行任何代码。

逐文件 SHA-256 必须与 `sources.json` 一致；运行入口核查活动指针/manifest/records/source manifest/数据库哈希，worker 额外核模型字节哈希。缺失或错配必须解决后再运行。第三方资源获取与再分发权限逐来源核对；本流程不提供未知许可资产的公开下载/再分发保证。

需要重新构建时：

```bash
.venv-foundation/bin/python -B -m flavoretro.resources <工作区>/data/derived/new-version --workspace <工作区>
# 再在另一个全新目录独立重放，比较 records.json / manifest.json；不覆盖旧版本
# 人工批准版本切换后，active.json 绑定 version 与 manifest_sha256
.venv-foundation/bin/python -B -m flavoretro.database --build --workspace <工作区>
```

SQLite 只索引已验收活动 JSON，不独立编辑。已有/损坏索引保留；另建不可变版本后重新索引，不就地覆写历史。

## 验证

```bash
.venv-foundation/bin/python -B -m unittest discover -s tests -v
.venv-foundation/bin/python -I -B scripts/package_check.py --workspace /home/ljx/FlavoRetro
.venv-foundation/bin/python -B scripts/browser_check.py
```

浏览器需同版本 Playwright Chromium。TASK-012 的浏览器验收复用了用户缓存中的匹配 Chromium 二进制，Python/Playwright 依赖位于新独立环境；新机使用 `python -m playwright install chromium` 获取浏览器。成功/失败输出均留在新的 `outputs/validation/` 子目录。CI 无受限资产，资产相关跳过项不能计为搜索验证。

## 无本地资产的源码与CI检查

云端使用`python -B scripts/test_portable.py`发现全部测试。[tests/local-assets.json](../tests/local-assets.json)逐项登记尚无自带缺包跳过条件的38项历史测试及其本地证据包；路径只允许工作区内data/或outputs/。缺少整个已登记包时，保留原测试ID并明确报告skip及缺失路径；未登记的失败、导入错误、旧登记失效均阻断CI。包目录存在时执行原测试，缺文件、散列漂移与错误断言不会变成skip。原有测试及其自身skip条件保持。

```bash
# 在无data/outputs/模型的源码副本中，通过当前批准TASK执行
python3 scripts/operate.py TASK-NNN .venv-foundation/bin/python -B scripts/test_portable.py
```

解释器路径使用该源码副本可用的工程环境；隔离副本可引用已有环境的绝对解释器路径，无需重新安装。此入口不禁用已有LiveContracts条件：若工作区已有模型，仍可能启动其真实搜索，不能把完整本地发现当成纯工程检查。缺失证据、真实搜索和浏览器验收分别报告，skip不当作通过；私有或受限包不为消除skip上传Git。新增缺包测试应先确认其测试边界并明确登记精确ID，不能捕获FileNotFoundError批量放行。

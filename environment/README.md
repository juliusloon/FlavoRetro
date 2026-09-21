# 运行环境
本次未修改旧仓库或 retro Conda 环境。新 .venv 由 /home/ljx/miniforge3/envs/retro/bin/python 创建，启用 system-site-packages；仅 Playwright/pyee 新装在本项目。它不是独立克隆的 Conda 环境。
核心固定依赖见 pyproject.toml；完整本次解析版本见 pip-freeze.txt。新机器应建立 Python 3.10 环境，按完整 lock 安装并执行 pip check 与全部测试，再按 metadata/sources.json 恢复本地资产。第三方模型/数据不随源代码提供，获取和再分发权限须按来源核对。
本机可直接 .venv/bin/python -B 运行；不要在历史目录运行构建、编译或测试。浏览器验证需 Playwright Chromium；本机复用了已有浏览器二进制。
未在全新机器重装验证；CPU 短程结果不代表跨平台性能。

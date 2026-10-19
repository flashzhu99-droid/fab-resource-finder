# FAB Resource Finder V1.0

半导体厂务公开网盘分享链接搜索引擎。**可运行原型；不包含任何虚构为真实资源的链接。**

- 无安装要求：双击 `FAB_免安装搜索版.html`
- SQLite模式：在Python 3.9+ 环境运行 `python app.py`，打开 `http://127.0.0.1:8765`
- 合规云端采集：配置 `config/sources.json`、`config/manual_links.csv`，通过 GitHub Actions 运行 `cloud/collect.py`
- 中文详细说明：[README_使用说明.md](README_使用说明.md)
- 测试：`python -m unittest discover -s tests -v`

首次真实索引为空。所附演示数据全部虚构，不能作为网盘下载链接。
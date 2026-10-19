# FAB Resource Finder V1.0

**半导体 FAB 厂务专业公开网盘分享链接搜索引擎**。混合架构：云端 GitHub Actions 采集允许公开的资源元数据，本地浏览器检索与导入。当前索引初始为 **0 条真实资源**，不包含未授权的搜索来源。

## 立即使用
1. 下载或打开 [免安装网页搜索端](web/index.html)，可在电脑上独立使用、搜索、收藏和导入索引。
2. 配置 `config/sources.json` 中有明确授权的公开HTML页面或RSS，分别设置 `enabled: true`、`permission_confirmed: true`。默认全部禁用；**不要仅因为网页能访问就认为允许抓取**。
3. 手工整理公开、允许发布的分享链接到 `config/manual_links.csv`，仅把已确认可公开的记录标记 `permission_confirmed=yes`。
4. GitHub 仓库 → **Settings → Pages → Build and deployment → Deploy from a branch → main /docs → Save**。公开索引地址为 https://flashzhu99-droid.github.io/fab-resource-finder/index.json （页面配置生效后才能访问）。
5. GitHub → **Actions → Collect approved public share links → Run workflow**，运行后检查日志和 `docs/index.json`。计划任务每天 UTC 03:17 尝试执行，GitHub 计划任务可能延迟。
6. 在本地搜索页里通过“同步云端”加载上述 JSON。部分浏览器会限制 `file://` 的跨域读取；遇到限制时先下载 index.json，再用“导入文件”加载。
7. 个人收藏、备注保存在本机浏览器存储，建议定期导出备份。

## 当前范围及限制
- 网盘识别：百度、夸克、阿里云盘、115、迅雷、微云。只索引分享链接元数据，不下载网盘文件，不绕过登录、提取码或验证码。
- 当前的云端采集器为保守的公开页面/RSS MVP，不是全网搜索引擎；不支持任意网站批量爬取或登录状态抓取。
- 尚未接入真实的授权公开来源，所以首次运行很可能仍为0条。
- 该 GitHub 仓库当前已部署**云端采集 + 本地 HTML**。包含 SQLite 和 Windows EXE 构建说明的完整本地原型，仍保留在先前提供的 V1.0 ZIP 中，**尚未同步进仓库**。
- 本仓库尚未完成 GitHub Actions 的实际执行验收；文件已提交不等于云端服务已运行。
- 所有对外公开的分享资源，需由操作者确认传播权利及内容合规性。不要公开企业内部文件和私密提取码。

## 目录
- `web/index.html`：本地搜索界面。
- `cloud/collect.py`：合规采集脚本。
- `core.py`：网盘识别和专业分类。
- `config/sources.json`：允许的采集源。
- `config/manual_links.csv`：经人工核准的分享清单。
- `docs/index.json`：供客户端下载的索引。
- `.github/workflows/collect.yml`：GitHub 定时工作流。

## 本地检查
```bash
python -m py_compile core.py cloud/collect.py
python cloud/collect.py
```

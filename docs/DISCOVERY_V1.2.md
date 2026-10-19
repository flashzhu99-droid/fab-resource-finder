# 网盘资源发现 V1.2

## 核心区别
本模块查询公开网盘分享链接的索引，不是去下载政府网站PDF。使用自托管 PanSou 的公开搜索端点获取候选网盘分享元数据。搜云客 soyunke.com 未授权接口不在本项目范围内。

## 文件
- cloud/pansou_bridge.py：PanSou API 适配器。
- config/fab_search_keywords.json：FAB专业关键词。
- .github/workflows/discover.yml：GitHub Actions运行脚本。
- docs/index.json：收集后的搜索索引。

## 操作
打开 Actions 中 Discover netdisk share candidates，运行工作流；建议先输入“超纯水系统”测试。若后端容器启动失败，请先看容器日志；请勿将 GitHub Actions 上传文件成功理解为成功发现资源。

## 责任与限制
此检索仅处理公开索引记录，不绕过登录、验证码或访问权限。未验证链接的有效性、提取码及作品转载授权；自动发现只能产生待核实候选，发布和传播需要核验权利与原始来源。查询强依赖上游可用性、接口格式以及第三方服务条款。上游可能变更导致零结果。

# daily-paper-feed

该项目会抓取 ArXiv 最近论文，并用 DeepSeek（OpenAI SDK 兼容接口）生成中文创新点与摘要翻译，最后发布为可直接用 GitHub Pages 访问的静态站点。

## 本地运行（可选）

- 安装依赖：

```bash
pip install -r requirements.txt
```

- 仅生成 Pages 静态站点（不抓取新数据）：

```bash
python build_pages.py
```

- 抓取 + 生成：

```bash
set DEEPSEEK_API_KEY=你的Key
python daily_fetch.py
python build_pages.py
```

## GitHub Pages 部署

本仓库使用 `docs/` 作为 GitHub Pages 的发布目录：

- 入口页面：`docs/index.html`
- 数据文件：`docs/papers_data.json`

### 1) 启用 Pages

在 GitHub 仓库 Settings → Pages：

- Source: `Deploy from a branch`
- Branch: `main` / Folder: `/docs`

启用后站点地址通常为：`https://bituion.github.io/daily-paper-feed/`

### 2) 配置自动更新

已提供 GitHub Actions 工作流：`.github/workflows/update-pages.yml`

需要在仓库 Settings → Secrets and variables → Actions 新增 Secret：

- `DEEPSEEK_API_KEY`

工作流会每天定时：

- 运行 `daily_fetch.py` 更新 `papers_data.json`
- 运行 `build_pages.py` 生成/更新 `docs/`
- 自动提交并推送到 `main`

你也可以在 Actions 页面手动触发 `Update papers and Pages`。

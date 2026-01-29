import os
import shutil


def _rewrite_index_html(template_html: str) -> str:
    # GitHub Pages 下项目通常部署在 /<repo>/，所以不能用以 / 开头的绝对路径。
    # 这里改为相对路径读取同目录下的 papers_data.json。
    return template_html.replace("fetch(`/api/papers?t=${new Date().getTime()}`)", "fetch(`./papers_data.json?t=${new Date().getTime()}`)")


def main() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))

    template_path = os.path.join(root_dir, "templates", "index.html")
    json_path = os.path.join(root_dir, "papers_data.json")

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    out_index_path = os.path.join(docs_dir, "index.html")
    out_json_path = os.path.join(docs_dir, "papers_data.json")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    # 如果第一次部署时还没有数据文件，也生成空 JSON，保证页面可用。
    if not os.path.exists(json_path):
        with open(json_path, "w", encoding="utf-8") as f:
            f.write("[]\n")

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    out_html = _rewrite_index_html(template_html)

    with open(out_index_path, "w", encoding="utf-8") as f:
        f.write(out_html)

    shutil.copyfile(json_path, out_json_path)

    print(f"Generated: {out_index_path}")
    print(f"Copied:    {out_json_path}")


if __name__ == "__main__":
    main()

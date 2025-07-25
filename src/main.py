import os
import shutil
from textnode import TextNode, TextType
from markdown_utils import markdown_to_html_node, extract_title


def copy_directory(src: str, dst: str) -> None:
    """
    Recursively copy all contents from src to dst.
    Deletes dst first for a clean copy.
    Logs each file copied.
    """
    if os.path.exists(dst):
        shutil.rmtree(dst)
    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dest_root = os.path.join(dst, rel_path) if rel_path != '.' else dst
        os.makedirs(dest_root, exist_ok=True)
        for fname in files:
            src_file = os.path.join(root, fname)
            dst_file = os.path.join(dest_root, fname)
            print(f"Copying {src_file} to {dst_file}")
            shutil.copy(src_file, dst_file)

def generate_page(from_path: str, template_path: str, dest_path: str):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md = open(from_path, encoding="utf-8").read()
    tpl = open(template_path, encoding="utf-8").read()

    # Convert to HTML
    content_html = markdown_to_html_node(md).to_html()
    title = extract_title(md)

    page = tpl.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page)

def generate_pages_recursive(content_dir: str, template_path: str, dest_dir: str) -> None:
    """
    Crawl content_dir and generate HTML pages for each .md file.
    """
#    if os.path.exists(dest_dir):
#        shutil.rmtree(dest_dir)
    # Ensure static files exist
    os.makedirs(dest_dir, exist_ok=True)
    for root, dirs, files in os.walk(content_dir):
        for fname in files:
            if not fname.lower().endswith('.md'):
                continue
            src_path = os.path.join(root, fname)
            rel_dir = os.path.relpath(root, content_dir)
            dest_subdir = os.path.join(dest_dir, rel_dir) if rel_dir != '.' else dest_dir
            os.makedirs(dest_subdir, exist_ok=True)
            dest_file = os.path.join(dest_subdir, os.path.splitext(fname)[0] + '.html')
            generate_page(src_path, template_path, dest_file)

def main():
    # Example TextNode usage
    node = TextNode(
        "This is some anchor text",
        TextType.LINK,
        "https://www.boot.dev"
    )
    print(node)

    # Generate static site: copy from 'static' to 'public'
    src_dir = 'static'
    dst_dir = 'public'
    template_path = 'template.html'

    # Announce the copy
    print(f"\nStarting directory copy: {src_dir} -> {dst_dir}")
    copy_directory(src_dir, dst_dir)
    generate_pages_recursive('content', template_path, dst_dir)

#    generate_page("content/index.md", "template.html", "public/index.html")
#    generate_page("content/blog/glorfindel/index.md", "template.html", "public/blog/glorfindel/index.html")
#    generate_page("content/blog/tom/index.md", "template.html", "public/blog/tom/index.html")
#    generate_page("content/blog/majesty/index.md", "template.html", "public/blog/majesty/index.html")
#    generate_page("content/contact/index.md", "template.html", "public/contact//index.html")
#

if __name__ == "__main__":
    main()

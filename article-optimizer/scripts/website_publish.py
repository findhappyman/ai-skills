#!/usr/bin/env python3
"""Write an Article Optimizer Markdown file into a static website repo."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from datetime import date as Date
from pathlib import Path


DEFAULT_ENV = Path.home() / ".config" / "article-optimizer" / "publisher.env"
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
IMAGE_LINE_BLOCK_RE = re.compile(r"(?m)^[ \t]*!\[([^\]]*)\]\(([^)]+)\)[ \t]*(?:\n|$)")
COVER_HINT_RE = re.compile(r"(封面|cover)", re.IGNORECASE)
BYLINE_RE = re.compile(r"^\*[^*\n]+ · [A-Z][a-z]{2} \d{1,2}, \d{4}\*$")


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def run(cmd: list[str], cwd: Path, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, env=env)
    if check and result.returncode != 0:
        print(f"ERROR: command failed: {' '.join(cmd)}", file=sys.stderr)
        if result.stdout.strip():
            print(result.stdout.strip(), file=sys.stderr)
        if result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def git(site_root: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], site_root, check=check)


def make_slug(title: str, date_str: str) -> str:
    ascii_part = re.sub(r"[^a-z0-9-]+", "-", title.lower()).strip("-")
    digest = hashlib.md5(title.encode("utf-8")).hexdigest()[:8]
    if not ascii_part:
        return f"{date_str}-{digest}"
    prefix = ascii_part[:48].strip("-")
    return f"{date_str}-{prefix}-{digest}"


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{escaped}"'


def strip_frontmatter(markdown: str) -> str:
    if not markdown.startswith("---"):
        return markdown
    match = re.match(r"^---\s*\n.*?\n---\s*\n?", markdown, flags=re.DOTALL)
    return markdown[match.end() :] if match else markdown


def strip_first_h1(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.startswith("# "):
            del lines[index]
            while index < len(lines) and not lines[index].strip():
                del lines[index]
        break
    return "\n".join(lines).strip()


def normalize_image_target(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    return target


def resolve_local_image(target: str, base_dir: Path) -> Path | None:
    target = normalize_image_target(target)
    if not target or target.startswith(("http://", "https://", "data:", "/")):
        return None
    path = Path(target)
    if not path.is_absolute():
        path = base_dir / path
    try:
        return path.resolve()
    except OSError:
        return None


def same_image_content(left: Path | None, right: Path | None) -> bool:
    if not left or not right:
        return False
    try:
        if not left.exists() or not right.exists():
            return False
        return hashlib.md5(left.read_bytes()).hexdigest() == hashlib.md5(right.read_bytes()).hexdigest()
    except OSError:
        return False


def strip_duplicate_cover_image(markdown: str, base_dir: Path, cover_path: Path | None) -> str:
    if not cover_path:
        return markdown.strip()
    cover = cover_path.resolve()
    for match in IMAGE_LINE_BLOCK_RE.finditer(markdown):
        before_image = markdown[: match.start()]
        if re.search(r"(?m)^\s*#{2,}\s", before_image):
            break
        alt = match.group(1)
        target = match.group(2)
        image_path = resolve_local_image(target, base_dir)
        is_same_cover = same_image_content(image_path, cover)
        is_cover_hint = bool(COVER_HINT_RE.search(alt) or COVER_HINT_RE.search(target))
        if is_same_cover or is_cover_hint:
            return (markdown[: match.start()].rstrip() + "\n\n" + markdown[match.end() :].lstrip("\n")).strip()
        break
    return markdown.strip()


def strip_social_noise(markdown: str, strip_trailing_handle: bool) -> str:
    lines = markdown.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^\s*建议(配图|补充图)[:：]", line):
            continue
        if stripped in {"— END —", "END"}:
            continue
        filtered.append(line)
    lines = filtered

    for index, line in enumerate(lines[:10]):
        if BYLINE_RE.match(line.strip()):
            del lines[index]
            break

    while lines and not lines[0].strip():
        del lines[0]
    while lines and lines[0].strip() in {"---", "***", "___"}:
        del lines[0]
        while lines and not lines[0].strip():
            del lines[0]
    while lines and not lines[-1].strip():
        lines.pop()
    if strip_trailing_handle and lines and re.match(r"^@[A-Za-z0-9_.-]+$", lines[-1].strip()):
        lines.pop()
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def copy_asset(source: Path, dest_dir: Path, public_prefix: str, written: list[Path]) -> str:
    data = source.read_bytes()
    suffix = source.suffix.lower() or ".png"
    name = hashlib.md5(data).hexdigest() + suffix
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / name
    if not dest.exists():
        shutil.copy2(source, dest)
    written.append(dest)
    return f"{public_prefix.rstrip('/')}/{name}"


def replace_inline_images(markdown: str, base_dir: Path, images_dir: Path, public_prefix: str, written: list[Path]) -> str:
    def repl(match: re.Match[str]) -> str:
        alt = match.group(1)
        target = match.group(2)
        image_path = resolve_local_image(target, base_dir)
        if not image_path:
            return match.group(0)
        if not image_path.exists():
            print(f"WARNING: inline image not found, keeping original reference: {target}", file=sys.stderr)
            return match.group(0)
        public_ref = copy_asset(image_path, images_dir, public_prefix, written)
        return f"![{alt}]({public_ref})"

    return IMAGE_RE.sub(repl, markdown)


def extract_digest(markdown: str, length: int = 100) -> str:
    text = strip_frontmatter(markdown)
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!", ">")) or line in {"---", "***", "___"}:
            continue
        line = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", line)
        line = re.sub(r"\*+([^*]+)\*+", r"\1", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = line.strip()
        if line:
            return line[:length]
    return ""


def build_frontmatter(args: argparse.Namespace, date_str: str, digest: str, cover_ref: str | None) -> str:
    lines = [
        "---",
        f"title: {yaml_quote(args.title)}",
        f"date: {date_str}",
    ]
    if args.author:
        lines.append(f"author: {yaml_quote(args.author)}")
    if digest:
        lines.append(f"digest: {yaml_quote(digest)}")
    if cover_ref:
        lines.append(f"cover: {yaml_quote(cover_ref)}")
    if args.tags:
        lines.append("tags:")
        for tag in args.tags:
            lines.append(f"  - {yaml_quote(tag)}")
    lines.append(f"draft: {'true' if args.draft else 'false'}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def relative_to_site(site_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(site_root.resolve()))


def publish(args: argparse.Namespace) -> Path:
    site_root = Path(args.site_root).expanduser().resolve()
    if not site_root.exists():
        raise SystemExit(f"ERROR: site root does not exist: {site_root}")

    content_path = Path(args.content).expanduser().resolve()
    if not content_path.exists():
        raise SystemExit(f"ERROR: content Markdown does not exist: {content_path}")

    cover_path = Path(args.cover).expanduser().resolve() if args.cover else None
    if cover_path and not cover_path.exists():
        raise SystemExit(f"ERROR: cover image does not exist: {cover_path}")

    date_str = args.date or str(Date.today())
    slug = args.slug or make_slug(args.title, date_str)
    blog_dir = site_root / args.blog_dir
    covers_dir = site_root / args.covers_dir
    images_dir = site_root / args.images_dir
    out_md = blog_dir / f"{slug}.md"
    written: list[Path] = []

    if args.push and git(site_root, ["status", "--porcelain"]).stdout.strip():
        raise SystemExit("ERROR: website repo must be clean before --push; use an isolated clone")

    if args.push and not args.skip_pull:
        git(site_root, ["pull", "--ff-only", args.remote, args.branch])

    cover_ref = copy_asset(cover_path, covers_dir, args.covers_public_prefix, written) if cover_path else None
    markdown = content_path.read_text(encoding="utf-8").strip()
    markdown = strip_frontmatter(markdown)
    markdown = strip_first_h1(markdown)
    markdown = strip_duplicate_cover_image(markdown, content_path.parent, cover_path)
    markdown = strip_social_noise(markdown, args.strip_trailing_handle)
    markdown = replace_inline_images(markdown, content_path.parent, images_dir, args.images_public_prefix, written)
    digest = args.digest or extract_digest(markdown)
    final = build_frontmatter(args, date_str, digest, cover_ref) + markdown.rstrip() + "\n"

    if out_md.exists() and not args.overwrite:
        current = out_md.read_text(encoding="utf-8")
        if current != final:
            raise SystemExit(f"ERROR: output file exists; rerun with --overwrite: {out_md}")

    blog_dir.mkdir(parents=True, exist_ok=True)
    out_md.write_text(final, encoding="utf-8")
    written.append(out_md)
    print(f"Article written: {out_md}")

    if not args.skip_build:
        build_env = os.environ.copy()
        npm_path = shutil.which(args.npm_bin) or args.npm_bin
        run([npm_path, "run", "build"], site_root, env=build_env)
        print("Build passed: npm run build")

    if not args.push:
        print("No push requested; skipped git commit/push.")
        return out_md

    rel_paths = sorted({relative_to_site(site_root, path) for path in written})
    git(site_root, ["add", *rel_paths])
    diff = git(site_root, ["diff", "--cached", "--quiet"], check=False)
    if diff.returncode == 0:
        print("No staged changes; skipped commit/push.")
        return out_md

    message = args.message or f"feat: publish article {slug}"
    git(site_root, ["commit", "-m", message])
    git(site_root, ["push", args.remote, args.branch])
    print("Pushed website changes.")
    return out_md


def main() -> int:
    env_parser = argparse.ArgumentParser(add_help=False)
    env_parser.add_argument("--env", default=os.environ.get("ARTICLE_PUBLISH_ENV", str(DEFAULT_ENV)))
    env_args, _ = env_parser.parse_known_args()
    load_env(Path(env_args.env).expanduser())
    parser = argparse.ArgumentParser(description="Write an optimized article to a static website repo.")
    parser.add_argument("--env", default=os.environ.get("ARTICLE_PUBLISH_ENV", str(DEFAULT_ENV)))
    parser.add_argument("--title", required=True)
    parser.add_argument("--content", required=True, help="Markdown content path.")
    parser.add_argument("--cover", help="Cover image path.")
    parser.add_argument("--digest")
    parser.add_argument("--date", help="Publish date YYYY-MM-DD; default today.")
    parser.add_argument("--author", default=os.environ.get("ARTICLE_SITE_AUTHOR", ""))
    parser.add_argument("--tag", action="append", dest="tags", default=[])
    parser.add_argument("--slug", help="Optional slug without .md.")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--site-root", default=os.environ.get("ARTICLE_SITE_ROOT"))
    parser.add_argument("--blog-dir", default=os.environ.get("ARTICLE_SITE_BLOG_DIR", "src/content/blog"))
    parser.add_argument("--covers-dir", default=os.environ.get("ARTICLE_SITE_COVERS_DIR", "public/covers"))
    parser.add_argument("--images-dir", default=os.environ.get("ARTICLE_SITE_IMAGES_DIR", "public/article-images"))
    parser.add_argument("--covers-public-prefix", default=os.environ.get("ARTICLE_SITE_COVERS_PUBLIC_PREFIX", "/covers"))
    parser.add_argument("--images-public-prefix", default=os.environ.get("ARTICLE_SITE_IMAGES_PUBLIC_PREFIX", "/article-images"))
    parser.add_argument("--npm-bin", default=os.environ.get("ARTICLE_SITE_NPM", "npm"))
    parser.add_argument("--remote", default=os.environ.get("ARTICLE_SITE_REMOTE", "origin"))
    parser.add_argument("--branch", default=os.environ.get("ARTICLE_SITE_BRANCH", "main"))
    parser.add_argument("--message")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-pull", action="store_true")
    parser.add_argument("--push", action="store_true", help="Commit and push touched files. Default only writes/builds.")
    parser.add_argument("--no-push", action="store_false", dest="push")
    parser.add_argument("--strip-trailing-handle", action="store_true")
    args = parser.parse_args()

    load_env(Path(args.env).expanduser())
    if not args.site_root:
        raise SystemExit("ERROR: --site-root or ARTICLE_SITE_ROOT is required")
    publish(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

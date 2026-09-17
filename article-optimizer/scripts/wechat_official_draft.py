#!/usr/bin/env python3
"""Create a WeChat Official Account draft from local HTML using the official API."""

from __future__ import annotations

import argparse
import html as html_lib
import json
import mimetypes
import os
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_ENV = Path.home() / ".config" / "article-optimizer" / "publisher.env"
TOKEN_CACHE = Path.home() / ".cache" / "article-optimizer" / "wechat_access_token.json"
PROXY_ENV_KEYS = (
    "WECHAT_HTTPS_PROXY",
    "WECHAT_FIXED_PROXY",
    "WECHAT_PROXY",
    "HTTPS_PROXY",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
)


def load_env_file(env_path: str | None) -> None:
    if not env_path:
        return
    path = Path(env_path).expanduser()
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def configured_proxy() -> str | None:
    for key in PROXY_ENV_KEYS:
        value = os.environ.get(key)
        if value:
            return value.strip()
    return None


def install_proxy_opener(proxy_url: str | None) -> None:
    if not proxy_url:
        return
    parsed = urllib.parse.urlparse(proxy_url)
    if parsed.scheme and parsed.scheme.lower().startswith("socks"):
        raise SystemExit(
            "WECHAT proxy uses SOCKS, but this script supports HTTP/HTTPS proxies only. "
            "Use an HTTP CONNECT proxy with a fixed egress IP."
        )
    urllib.request.install_opener(
        urllib.request.build_opener(urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))
    )


def api_json(url: str, payload: dict | None = None) -> dict:
    if payload is None:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read()
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
    result = json.loads(data.decode("utf-8"))
    if "errcode" in result and result.get("errcode") not in (0, None):
        raise RuntimeError(f"WeChat API error {result.get('errcode')}: {result.get('errmsg')}")
    return result


def get_access_token(appid: str, appsecret: str) -> str:
    now = int(time.time())
    if TOKEN_CACHE.exists():
        try:
            cached = json.loads(TOKEN_CACHE.read_text(encoding="utf-8"))
            if cached.get("appid") == appid and cached.get("expires_at", 0) > now + 120:
                return cached["access_token"]
        except (OSError, KeyError, json.JSONDecodeError):
            pass

    qs = urllib.parse.urlencode({"grant_type": "client_credential", "appid": appid, "secret": appsecret})
    result = api_json(f"https://api.weixin.qq.com/cgi-bin/token?{qs}")
    token = result["access_token"]
    TOKEN_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_CACHE.touch(mode=0o600, exist_ok=True)
    TOKEN_CACHE.chmod(0o600)
    TOKEN_CACHE.write_text(
        json.dumps(
            {
                "appid": appid,
                "access_token": token,
                "expires_at": now + int(result.get("expires_in", 7200)),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return token


def multipart_post(url: str, field_name: str, file_path: Path) -> dict:
    boundary = f"----ArticleOptimizerBoundary{int(time.time() * 1000)}"
    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body = bytearray()
    body.extend(f"--{boundary}\r\n".encode())
    body.extend((f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"\r\n').encode())
    body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
    body.extend(file_path.read_bytes())
    body.extend(f"\r\n--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if "errcode" in result and result.get("errcode") not in (0, None):
        raise RuntimeError(f"WeChat API error {result.get('errcode')}: {result.get('errmsg')}")
    return result


def compress_thumb(image_path: Path) -> Path:
    try:
        from PIL import Image
    except ImportError:
        return image_path

    image = Image.open(image_path).convert("RGB")
    image.thumbnail((900, 500))
    out = Path(tempfile.gettempdir()) / f"wechat_thumb_{image_path.stem}.jpg"
    quality = 88
    while quality >= 45:
        image.save(out, format="JPEG", quality=quality, optimize=True)
        if out.stat().st_size <= 64 * 1024:
            return out
        quality -= 8
    image.thumbnail((500, 280))
    image.save(out, format="JPEG", quality=45, optimize=True)
    return out


def extract_title(html: str) -> str:
    for tag in ("title", "h1"):
        match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", html, flags=re.I | re.S)
        if match:
            title = re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()
            if title:
                return title[:64]
    return "未命名文章"


def strip_preview_shell(html: str) -> str:
    html = re.sub(r"<!DOCTYPE[^>]*>", "", html, flags=re.I)
    html = re.sub(r"<head[\s\S]*?</head>", "", html, flags=re.I)
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)
    body = re.search(r"<body[^>]*>([\s\S]*?)</body>", html, flags=re.I)
    return body.group(1).strip() if body else html.strip()


def find_matching_tag_end(text: str, start: int, tag: str) -> int:
    pattern = re.compile(rf"</?{tag}\b[^>]*>", flags=re.I)
    depth = 0
    for match in pattern.finditer(text, start):
        token = match.group(0)
        if token.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not token.endswith("/>"):
            depth += 1
    return -1


def unwrap_outer_tag(content: str, tag: str) -> str:
    opening = re.match(rf"^\s*<{tag}\b[^>]*>", content, flags=re.I)
    if not opening:
        return content.strip()
    end = find_matching_tag_end(content, opening.start(), tag)
    if end == -1:
        return content.strip()
    if content[end:].strip():
        return content.strip()
    return content[opening.end() : end - len(f"</{tag}>")].strip()


def remove_page_shell(content: str) -> str:
    for tag in ("main", "article"):
        content = unwrap_outer_tag(content, tag)
    return content.strip()


def resolve_image(src: str, html_file: Path) -> Path | None:
    if re.match(r"^https?://", src, flags=re.I) or src.startswith("data:"):
        return None
    decoded = urllib.parse.unquote(src)
    path = Path(decoded)
    if not path.is_absolute():
        path = html_file.parent / path
    return path if path.exists() else None


def remove_leading_cover_image(content: str, html_file: Path | None, cover_path: Path | None) -> str:
    if not html_file or not cover_path:
        return content
    cover_key = str(cover_path.expanduser().resolve())
    pattern = re.compile(r'^\s*<section\b[^>]*>\s*<img\b[^>]*\bsrc="([^"]+)"[^>]*>\s*</section>\s*', flags=re.I)
    match = pattern.match(content)
    if not match:
        return content
    image_path = resolve_image(match.group(1), html_file)
    if image_path and str(image_path.resolve()) == cover_key:
        return content[match.end() :].lstrip()
    return content


def remove_content_title_block(content: str) -> str:
    first_section = re.search(r"<section\b[^>]*>", content, flags=re.I)
    if not first_section:
        return content
    start = first_section.start()
    end = find_matching_tag_end(content, start, "section")
    if end == -1:
        return content
    block = content[start:end]
    if "<img" in block.lower():
        return content
    title_like = (
        "letter-spacing" in block.lower()
        or "linear-gradient" in block.lower()
        or re.search(r"font-size:\s*(2[4-9]|[3-9][0-9])px", block, flags=re.I)
    )
    if title_like:
        return content[:start] + content[end:]
    return content


def normalize_section_headings(content: str) -> str:
    pattern = re.compile(
        r'<section style="margin:\s*35px 24px 18px 24px;\s*display:\s*flex;\s*display:\s*-webkit-flex;">\s*'
        r'<section style="([^"]*?background-color:\s*(#[0-9a-fA-F]{6})[^"]*?)">\s*([0-9]{2})\s*</section>\s*'
        r'<section style="([^"]*?)">\s*([\s\S]*?)\s*</section>\s*</section>',
        flags=re.I,
    )

    def repl(match: re.Match[str]) -> str:
        color = match.group(2)
        number = match.group(3).strip()
        title = re.sub(r"\s+", " ", match.group(5)).strip()
        return (
            '<section style="margin: 35px 24px 18px 24px; padding: 0; line-height: 1.5;">\n'
            f'  <span style="display: inline-block; vertical-align: middle; background-color: {color}; '
            'color: #ffffff; font-size: 12px; line-height: 1.6; padding: 2px 8px; '
            f'font-weight: bold; letter-spacing: 1px; margin-right: 10px;">{number}</span>\n'
            '  <span style="display: inline-block; vertical-align: middle; font-size: 20px; '
            f'font-weight: bold; color: #1a1a1a; line-height: 1.5;">{title}</span>\n'
            "</section>"
        )

    return pattern.sub(repl, content)


def prepare_wechat_draft_content(html: str, html_file: Path | None = None, cover_path: Path | None = None) -> str:
    content = strip_preview_shell(html)
    content = remove_page_shell(content)
    content = remove_leading_cover_image(content, html_file, cover_path)
    content = remove_content_title_block(content)
    content = normalize_section_headings(content)
    return content.strip()


def upload_article_image(token: str, image_path: Path) -> str:
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={urllib.parse.quote(token)}"
    result = multipart_post(url, "media", image_path)
    return result["url"]


def upload_thumb(token: str, image_path: Path) -> str:
    thumb = compress_thumb(image_path)
    url = (
        "https://api.weixin.qq.com/cgi-bin/material/add_material"
        f"?access_token={urllib.parse.quote(token)}&type=thumb"
    )
    result = multipart_post(url, "media", thumb)
    return result["media_id"]


def replace_local_images(content: str, html_file: Path, token: str) -> tuple[str, list[Path]]:
    uploaded: dict[str, str] = {}
    seen_files: list[Path] = []

    def repl(match: re.Match[str]) -> str:
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        image_path = resolve_image(src, html_file)
        if not image_path:
            return match.group(0)
        key = str(image_path.resolve())
        if key not in uploaded:
            uploaded[key] = upload_article_image(token, image_path)
            seen_files.append(image_path)
        return f'{prefix}{uploaded[key]}{suffix}'

    new_content = re.sub(r'(<img\b[^>]*\bsrc=")([^"]+)("[^>]*>)', repl, content, flags=re.I)
    return new_content, seen_files


def digest_from_content(content: str) -> str:
    text = html_lib.unescape(re.sub(r"<[^>]+>", "", content))
    text = re.sub(r"\s+", " ", text).strip()
    return text[:120]


def add_draft(token: str, article: dict) -> dict:
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={urllib.parse.quote(token)}"
    return api_json(url, {"articles": [article]})


def main() -> int:
    parser = argparse.ArgumentParser(description="Create WeChat Official Account draft from HTML.")
    parser.add_argument("--html", required=True, help="Local WeChat-formatted HTML file.")
    parser.add_argument("--env", default=os.environ.get("ARTICLE_PUBLISH_ENV", str(DEFAULT_ENV)))
    parser.add_argument("--appid")
    parser.add_argument("--appsecret")
    parser.add_argument("--author")
    parser.add_argument("--cover", help="Cover image path; defaults to first local image in HTML.")
    parser.add_argument("--thumb-media-id", help="Existing WeChat thumb media id.")
    parser.add_argument("--title")
    parser.add_argument("--digest")
    args = parser.parse_args()

    load_env_file(args.env)
    install_proxy_opener(configured_proxy())
    appid = args.appid or os.environ.get("WECHAT_APPID")
    appsecret = args.appsecret or os.environ.get("WECHAT_APPSECRET")
    if not appid or not appsecret:
        print("Missing WECHAT_APPID or WECHAT_APPSECRET.", file=sys.stderr)
        return 2

    html_file = Path(args.html).expanduser().resolve()
    raw_html = html_file.read_text(encoding="utf-8")
    title = (args.title or extract_title(raw_html))[:64]
    token = get_access_token(appid, appsecret)

    cover_path = Path(args.cover).expanduser().resolve() if args.cover else None
    content = prepare_wechat_draft_content(raw_html, html_file, cover_path)
    content, local_images = replace_local_images(content, html_file, token)

    thumb_media_id = args.thumb_media_id
    if not thumb_media_id:
        cover_path = cover_path or (local_images[0] if local_images else None)
        if not cover_path or not cover_path.exists():
            print("No cover image found. Provide --cover or --thumb-media-id.", file=sys.stderr)
            return 2
        thumb_media_id = upload_thumb(token, cover_path)

    article = {
        "title": title,
        "author": args.author or os.environ.get("WECHAT_AUTHOR", ""),
        "digest": (args.digest or digest_from_content(content))[:120],
        "content": content,
        "content_source_url": "",
        "thumb_media_id": thumb_media_id,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    result = add_draft(token, article)
    print(json.dumps({"success": True, "title": title, "result": result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

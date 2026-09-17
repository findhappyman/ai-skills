#!/usr/bin/env python3
"""Fix half-width punctuation in Chinese Markdown, HTML, or plain text files."""

from __future__ import annotations

import re
import sys


PUNCT_MAP = {
    ",": "，",
    ".": "。",
    ":": "：",
    ";": "；",
    "?": "？",
    "!": "！",
}

CJK = r"\u4e00-\u9fff"
CN_RIGHT_PUNCT = r"\u201d\u2019\u300d\u300f\u300b\u3009\uff09"
CN = rf"[{CJK}{CN_RIGHT_PUNCT}]"
EN = r"[a-zA-Z0-9\)]"


def fix_text_simple(text: str) -> str:
    text = re.sub(rf"({CN})([,;:?!])", lambda m: m.group(1) + PUNCT_MAP[m.group(2)], text)
    text = re.sub(rf"({CN})\.(?![0-9a-zA-Z])", lambda m: m.group(1) + "。", text)
    text = re.sub(
        rf"({EN})([,;:?!])(\s*)([{CJK}])",
        lambda m: m.group(1) + PUNCT_MAP[m.group(2)] + m.group(3) + m.group(4),
        text,
    )
    text = re.sub(rf"({EN})\.([{CJK}])", lambda m: m.group(1) + "。" + m.group(2), text)
    return text


def fix_markdown(text: str) -> str:
    out: list[str] = []
    parts = re.split(r"(```[\s\S]*?```)", text)
    in_image_prompt_section = False
    for part in parts:
        if part.startswith("```"):
            out.append(part)
            continue
        for line in part.splitlines(keepends=True):
            stripped = line.strip()
            if stripped.startswith("## "):
                in_image_prompt_section = stripped.lower() in {
                    "## gpt image prompt",
                    "## image prompt",
                    "## 图片 prompt",
                }
            if in_image_prompt_section and stripped.startswith(">"):
                out.append(line)
                continue
            inline_parts = re.split(r"(`[^`\n]+`)", line)
            for chunk in inline_parts:
                if chunk.startswith("`") and chunk.endswith("`"):
                    out.append(chunk)
                else:
                    out.append(fix_text_simple(chunk))
    return "".join(out)


def fix_html(html: str) -> str:
    parts: list[str] = []
    i = 0
    while i < len(html):
        if html[i] == "<":
            end = html.find(">", i)
            if end == -1:
                parts.append(html[i:])
                break
            parts.append(html[i : end + 1])
            i = end + 1
        else:
            next_tag = html.find("<", i)
            if next_tag == -1:
                parts.append(html[i:])
                break
            parts.append(html[i:next_tag])
            i = next_tag
    return "".join(part if part.startswith("<") else fix_text_simple(part) for part in parts)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fix_punct.py <file> [file ...]", file=sys.stderr)
        return 2
    for fp in sys.argv[1:]:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        if fp.endswith((".html", ".htm")):
            new_content = fix_html(content)
        elif fp.endswith((".md", ".markdown")):
            new_content = fix_markdown(content)
        else:
            new_content = fix_text_simple(content)
        if new_content != content:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"FIXED: {fp}")
        else:
            print(f"NO CHANGE: {fp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate an Article Optimizer run directory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


READY_FILES = [
    "{topic}_总览.md",
    "{topic}_审核版.md",
    "{topic}_公众号排版.html",
    "{topic}_X_Article.md",
    "{topic}_X_Article_发布版.md",
    "{topic}_小红书.txt",
    "{topic}_网站版.md",
    "{topic}_封面图.png",
    "{topic}_段落配图_01.png",
    "{topic}_段落配图_02.png",
    "{topic}_信息图.png",
]

SENSITIVE_PATTERNS = [
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"(?i)(appsecret|api[_-]?key|access[_-]?token|password|passwd|secret)\s*=\s*[^#\s]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)WECHAT_APPSECRET\s*[:=]\s*[^#\s]+"),
    re.compile(r"(?i)WECHAT_API_KEY\s*[:=]\s*[^#\s]+"),
]


def looks_like_image(path: Path) -> bool:
    if not path.exists() or path.stat().st_size <= 0:
        return False
    head = path.read_bytes()[:16]
    return (
        head.startswith(b"\x89PNG\r\n\x1a\n")
        or head.startswith(b"\xff\xd8\xff")
        or head.startswith(b"RIFF") and b"WEBP" in head
    )


def load_state(run_dir: Path, errors: list[str]) -> dict:
    state_path = run_dir / "TRIM_STATE.json"
    if not state_path.exists():
        errors.append("missing TRIM_STATE.json")
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid TRIM_STATE.json: {exc}")
        return {}


def scan_sensitive(run_dir: Path) -> list[str]:
    findings: list[str] = []
    for path in run_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern in SENSITIVE_PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path.relative_to(run_dir)}:{line_no}: possible sensitive value")
                    break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Article Optimizer run directory.")
    parser.add_argument("run_dir", nargs="?", help="Run directory to validate.")
    parser.add_argument("--topic", help="Topic prefix. Defaults to TRIM_STATE.topic.")
    parser.add_argument("--strict", action="store_true", help="Require all review-package files.")
    parser.add_argument("--scan-sensitive", action="store_true", help="Scan text files for obvious secrets and personal paths.")
    args = parser.parse_args()

    if not args.run_dir:
        parser.print_help()
        return 0

    run_dir = Path(args.run_dir).expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not run_dir.exists():
        errors.append(f"run dir does not exist: {run_dir}")
    if not (run_dir / "原始稿.txt").exists():
        errors.append("missing 原始稿.txt")

    state = load_state(run_dir, errors)
    original_path = run_dir / "原始稿.txt"
    if original_path.exists() and state.get("original_sha256"):
        if hashlib.sha256(original_path.read_bytes()).hexdigest() != state["original_sha256"]:
            errors.append("原始稿 hash changed; preserve original and write edits to a separate file")
    topic = args.topic or state.get("topic") or run_dir.name.rsplit("_", 1)[0]
    require_ready = args.strict or state.get("status") == "article_assets_ready"

    if require_ready:
        channels = state.get("channels", ["wechat", "x", "xhs", "website"])
        platform_files = {"wechat": ["公众号排版.html"], "x": ["X_Article.md", "X_Article_发布版.md"], "xhs": ["小红书.txt"], "website": ["网站版.md"]}
        required = ["{topic}_总览.md", "{topic}_审核版.md"]
        for channel in channels:
            if channel not in platform_files:
                errors.append(f"unknown channel: {channel}")
                continue
            required.extend("{topic}_" + name for name in platform_files[channel])
        required.extend(["{topic}_封面图.png", "{topic}_段落配图_01.png", "{topic}_段落配图_02.png", "{topic}_信息图.png"])
        if "required_files" in state:
            required = state["required_files"]
            if not isinstance(required, list) or not required or not all(isinstance(name, str) for name in required):
                errors.append("required_files must be a nonempty list of run-relative filenames")
                required = []
        for template in required:
            path = run_dir / template.format(topic=topic)
            if not path.resolve().is_relative_to(run_dir):
                errors.append("required_files must stay inside run dir")
                continue
            if not path.exists():
                errors.append(f"missing {path.name}")
            elif path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"} and not looks_like_image(path):
                errors.append(f"invalid or empty image {path.name}")

    for name in ("TRIM_STATE.json", "social-publish-status.json"):
        path = run_dir / name
        if path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid {name}: {exc}")

    if args.scan_sensitive:
        warnings.extend(scan_sensitive(run_dir))

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors or (args.scan_sensitive and warnings):
        return 1
    print(f"OK: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

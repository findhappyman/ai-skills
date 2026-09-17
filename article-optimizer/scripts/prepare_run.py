#!/usr/bin/env python3
"""Create an Article Optimizer run directory from a text transcript."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path


TRIGGER_RE = re.compile(r"^\s*(TRIM|trim|Quick|quick|TS|ts|QS|qs|t|q)\b[:：\s-]*")
CJK_SPACE_RE = re.compile(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])")


def clean_original(text: str, fix_cjk_spaces: bool = False) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if fix_cjk_spaces:
        text = CJK_SPACE_RE.sub("", text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip() + "\n"


def safe_topic(topic: str) -> str:
    topic = re.sub(r"[\\/:*?\"<>|\n\r\t]+", "-", topic.strip())
    topic = re.sub(r"\s+", "-", topic)
    topic = topic.strip("-._ ")
    return topic[:80] or "untitled"


def load_text(args: argparse.Namespace) -> str:
    if args.text_file:
        return Path(args.text_file).expanduser().read_text(encoding=args.encoding)
    if args.text:
        return args.text
    raise SystemExit("ERROR: provide --text-file or --text")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare an Article Optimizer run directory.")
    parser.add_argument("--workspace", default=os.environ.get("ARTICLE_WORKSPACE"), help="Article workspace root.")
    parser.add_argument("--runs-dir", default=os.environ.get("ARTICLE_RUNS_DIR", "runs"))
    parser.add_argument("--topic", required=True)
    parser.add_argument("--text-file", help="Transcript or draft text file.")
    parser.add_argument("--text", help="Transcript or draft text literal.")
    parser.add_argument("--encoding", default="utf-8")
    parser.add_argument("--timestamp", help="YYYYMMDD_HHMMSS; default now.")
    parser.add_argument("--source", default="manual-text", help="Source label written to TRIM_STATE.json.")
    parser.add_argument("--fix-cjk-spaces", action="store_true", help="Only use for confirmed transcription spacing artifacts.")
    args = parser.parse_args()

    if not args.workspace:
        raise SystemExit("ERROR: --workspace or ARTICLE_WORKSPACE is required")

    workspace = Path(args.workspace).expanduser().resolve()
    now = datetime.now()
    stamp = args.timestamp or now.strftime("%Y%m%d_%H%M%S")
    run_dir = workspace / args.runs_dir / now.strftime("%Y") / now.strftime("%m") / f"{safe_topic(args.topic)}_{stamp}"
    original = clean_original(load_text(args), args.fix_cjk_spaces)
    if not original.strip():
        raise SystemExit("ERROR: input is empty")
    run_dir.mkdir(parents=True, exist_ok=False)

    original_path = run_dir / "原始稿.txt"
    original_path.write_text(original, encoding="utf-8")

    state = {
        "status": "original_ready",
        "topic": args.topic,
        "created_at": now.isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "source": args.source,
        "original_file": "原始稿.txt",
        "original_sha256": hashlib.sha256(original.encode("utf-8")).hexdigest(),
        "review_required": True,
        "published": False,
    }
    state_path = run_dir / "TRIM_STATE.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifests = workspace / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    with (manifests / "runs.jsonl").open("a", encoding="utf-8") as fp:
        fp.write(json.dumps({"run_dir": str(run_dir), **state}, ensure_ascii=False) + "\n")

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

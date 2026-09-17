#!/usr/bin/env python3
"""只在明确配置的录音目录内查找当天录音。"""
import argparse
from datetime import date, datetime
import json
import os
from pathlib import Path
import re

EXTENSIONS = {".wav", ".m4a", ".mp3", ".flac", ".aac", ".ogg", ".opus", ".caf"}


def collect(root: Path, day: date, min_bytes: int = 102400, max_depth: int = 5):
    if not root.is_dir():
        raise ValueError("录音目录不存在或不可读取")
    candidates, errors = [], []
    def onerror(error):
        errors.append(str(error.filename))
    for current, dirs, files in os.walk(root, onerror=onerror, followlinks=False):
        dirs[:] = [d for d in dirs if not d.startswith(".") and not (Path(current) / d).is_symlink()]
        if len(Path(current).relative_to(root).parts) >= max_depth:
            dirs.clear()
        for name in files:
            file = Path(current) / name
            if name.startswith(".") or file.suffix.lower() not in EXTENSIONS or file.is_symlink():
                continue
            try:
                stat = file.stat()
            except OSError:
                errors.append(str(file))
                continue
            if stat.st_size < min_bytes:
                continue
            modified = datetime.fromtimestamp(stat.st_mtime)
            recorded = None
            match = re.search(r"(20\d{6})[_-](\d{6})", name)
            if match:
                try:
                    recorded = datetime.strptime("".join(match.groups()), "%Y%m%d%H%M%S")
                except ValueError:
                    pass
            if recorded and recorded.date() == day:
                when, basis = recorded, "filename"
            elif modified.date() == day:
                when, basis = modified, "mtime_fallback"
            else:
                continue
            candidates.append({"path": str(file), "recorded_at": when.isoformat(), "date_basis": basis, "bytes": stat.st_size})
    candidates.sort(key=lambda c: (c["recorded_at"], c["path"]))
    return {"date": day.isoformat(), "selected_paths": [c["path"] for c in candidates], "candidates": candidates, "unreadable_paths": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.environ.get("RECORDINGS_ROOT"))
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--min-bytes", type=int, default=102400)
    parser.add_argument("--max-depth", type=int, default=5)
    args = parser.parse_args()
    if not args.root:
        parser.error("需要 --root 或 RECORDINGS_ROOT；不会自动全盘扫描")
    try:
        result = collect(Path(args.root).expanduser().resolve(), args.date, args.min_bytes, args.max_depth)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result["unreadable_paths"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

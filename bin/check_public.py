#!/usr/bin/env python3
"""检查公开包；只打印规则与位置，绝不打印匹配的敏感值。"""
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RULES = {
    "personal-home-path": re.compile(r"(?:/Users/|/home/)[A-Za-z0-9._-]+/"),
    "credential-in-url": re.compile(r"https?://[^\s/]+:[^\s/@]+@"),
    "github-token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "api-secret": re.compile(r"\bsk-[A-Za-z0-9_-]{24,}"),
    "email": re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b"),
}


def findings(root=ROOT):
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root, capture_output=True, check=True)
    paths = sorted(set(result.stdout.decode().split("\0")) - {""})
    terms = [v.strip().lower() for v in os.environ.get("PUBLIC_FORBIDDEN_TERMS", "").split(",") if v.strip()]
    hits = []
    for rel in paths:
        path = root / rel
        if not path.exists():
            continue
        if path.is_symlink():
            hits.append((rel, 0, "symlink"))
            continue
        if any(p in {"runs", "outputs", "logs", "__pycache__", ".env"} for p in path.relative_to(root).parts) or path.suffix in {".wav", ".m4a", ".mp3", ".pyc", ".env"}:
            hits.append((rel, 0, "private-runtime-file"))
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            hits.append((rel, 0, "binary-needs-review"))
            continue
        for line_no, line in enumerate(content.splitlines(), 1):
            for name, pattern in RULES.items():
                if pattern.search(line):
                    hits.append((rel, line_no, name))
            if any(term in line.lower() for term in terms):
                hits.append((rel, line_no, "configured-personal-term"))
    return hits


if __name__ == "__main__":
    hits = findings()
    for file, line, rule in hits:
        print(f"{file}:{line}: {rule}")
    print(f"Public package scan: {len(hits)} finding(s)")
    sys.exit(bool(hits))

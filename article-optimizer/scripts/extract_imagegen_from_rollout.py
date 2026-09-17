#!/usr/bin/env python3
"""Extract Codex built-in image generation PNGs from a rollout JSONL file."""

from __future__ import annotations

import argparse
import base64
import json
import os
import struct
from pathlib import Path


def default_session_for_thread(thread_id: str) -> Path | None:
    sessions = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "sessions"
    matches = sorted(
        sessions.glob(f"**/rollout-*{thread_id}.jsonl"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return matches[0] if matches else None


def png_size(data: bytes) -> tuple[int | None, int | None]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        return None, None
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def decode_result(result: str) -> bytes | None:
    if result.startswith("data:image/"):
        _, _, result = result.partition(",")
    if not result.startswith("iVBOR"):
        return None
    return base64.b64decode(result)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Decode image_generation_end PNG payloads from a Codex rollout JSONL."
    )
    parser.add_argument("--session-jsonl", help="Explicit rollout JSONL path.")
    parser.add_argument(
        "--thread-id",
        default=os.environ.get("CODEX_THREAD_ID"),
        help="Codex thread id. Defaults to CODEX_THREAD_ID.",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory. Defaults to ~/.codex/generated_images/<thread-id>.",
    )
    args = parser.parse_args()

    session_path = Path(args.session_jsonl).expanduser() if args.session_jsonl else None
    if not session_path:
        if not args.thread_id:
            parser.error("--session-jsonl or --thread-id/CODEX_THREAD_ID is required")
        session_path = default_session_for_thread(args.thread_id)
    if not session_path or not session_path.exists():
        raise SystemExit(f"ERROR: rollout JSONL not found: {session_path or args.thread_id}")

    output_dir = (
        Path(args.output_dir).expanduser()
        if args.output_dir
        else Path.home() / ".codex" / "generated_images" / (args.thread_id or session_path.stem)
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    seen: set[str] = set()
    with session_path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = item.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "image_generation_end":
                continue
            call_id = str(payload.get("call_id") or f"line_{lineno}")
            if call_id in seen:
                continue
            data = decode_result(str(payload.get("result") or ""))
            if not data:
                continue
            seen.add(call_id)
            safe_id = "".join(char for char in call_id if char.isalnum() or char in "-_") or f"line_{lineno}"
            target = output_dir / f"{safe_id}.png"
            target.write_bytes(data)
            written.append(target)

    print(f"session: {session_path}")
    print(f"output_dir: {output_dir}")
    print(f"written: {len(written)}")
    for path in written:
        width, height = png_size(path.read_bytes())
        dims = f"{width}x{height}" if width and height else "unknown"
        print(f"{path}\t{path.stat().st_size}\t{dims}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())

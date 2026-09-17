#!/usr/bin/env python3
"""
TRIM 音频转原始稿。

输入 WAV、MP3、M4A、FLAC、AAC、OGG、OPUS 或常见视频文件，先用 ffmpeg
规整为 16kHz mono WAV，再用 openai-whisper 转写，输出原始稿 TXT 和可选 SRT。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path


def check_command(name: str, install_hint: str) -> None:
    if shutil.which(name):
        return
    raise SystemExit(f"缺少依赖：{name}。安装方式：{install_hint}")


def check_whisper() -> None:
    try:
        import whisper  # noqa: F401
    except ImportError as error:
        raise SystemExit("缺少依赖：openai-whisper。安装方式：pip install openai-whisper") from error


def normalize_audio(source: Path, wav_path: Path) -> None:
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-vn",
        "-ar",
        "16000",
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg 音频预处理失败：\n{result.stderr.strip()}")


def format_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_srt(path: Path, segments: list[dict]) -> None:
    lines: list[str] = []
    for index, segment in enumerate(segments, 1):
        start = format_srt_time(float(segment["start"]))
        end = format_srt_time(float(segment["end"]))
        text = str(segment["text"]).strip()
        lines.append(f"{index}\n{start} --> {end}\n{text}\n")
    path.write_text("\n".join(lines), encoding="utf-8")


def transcribe(source: Path, model_name: str, language: str) -> dict:
    import whisper

    with tempfile.TemporaryDirectory(prefix="trim_whisper_") as temp_dir:
        wav_path = Path(temp_dir) / "input.wav"
        normalize_audio(source, wav_path)

        model = whisper.load_model(model_name)
        language_arg = None if language == "auto" else language
        result = model.transcribe(
            str(wav_path),
            language=language_arg,
            verbose=False,
            fp16=False,
        )

    segments = result.get("segments", [])
    duration = float(segments[-1]["end"]) if segments else 0.0
    return {
        "text": result.get("text", "").strip(),
        "segments": [
            {
                "start": float(segment["start"]),
                "end": float(segment["end"]),
                "text": str(segment["text"]).strip(),
            }
            for segment in segments
        ],
        "duration_seconds": duration,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="TRIM 音频转原始稿")
    parser.add_argument("audio", help="音频或视频文件路径")
    parser.add_argument("--out-dir", required=True, help="输出目录")
    parser.add_argument(
        "--model",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper 模型，默认 medium；低配置设备可显式选 small",
    )
    parser.add_argument("--language", default="zh", help="语言代码，默认 zh；auto 为自动检测")
    parser.add_argument("--no-srt", action="store_true", help="不输出 SRT")
    args = parser.parse_args()

    source = Path(args.audio).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"音频文件不存在：{source}")

    out_dir = Path(args.out_dir).expanduser().resolve()
    if any((out_dir / name).exists() for name in ("原始稿.txt", "原始稿.srt", "trim-transcribe.json")):
        raise SystemExit("输出目录已有原始转写，请选择新目录以保护已有资料。")
    out_dir.mkdir(parents=True, exist_ok=True)

    check_command("ffmpeg", "brew install ffmpeg")
    check_whisper()

    started_at = datetime.now().isoformat(timespec="seconds")
    result = transcribe(source, args.model, args.language)

    transcript_path = out_dir / "原始稿.txt"
    transcript_path.write_text(result["text"] + "\n", encoding="utf-8")

    srt_path = None
    if not args.no_srt and result["segments"]:
        srt_path = out_dir / "原始稿.srt"
        write_srt(srt_path, result["segments"])

    metadata = {
        "source": str(source),
        "transcript": str(transcript_path),
        "srt": str(srt_path) if srt_path else None,
        "model": args.model,
        "language": args.language,
        "duration_seconds": result["duration_seconds"],
        "chars": len(result["text"]),
        "started_at": started_at,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }
    metadata_path = out_dir / "trim-transcribe.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

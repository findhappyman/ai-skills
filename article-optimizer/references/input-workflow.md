# 录音输入与重转写

需要 Python 3.10+、FFmpeg，音频识别可选安装 `openai-whisper`。首次加载模型会下载权重；录音在本地识别。按设备选模型，不假定 GPU。

```bash
python3 -m pip install openai-whisper
python3 "$SKILL_DIR/scripts/trim-transcribe.py" /path/to/recording.wav \
  --out-dir /path/to/new-transcription --model medium --language zh
python3 "$SKILL_DIR/scripts/prepare_run.py" --workspace "$ARTICLE_WORKSPACE" \
  --topic "文章主题" --text-file /path/to/new-transcription/原始稿.txt \
  --source /path/to/recording.wav
```

将 SRT 和元数据复制到 run，保留模型、来源、识别语言和时间。重跑写新目录，比较质量再选择；不覆盖稳定原始稿，不把录音或转写提交到 skill 仓库。

## 今天的录音

```bash
python3 "$SKILL_DIR/scripts/find_recordings.py" --root /path/to/recordings --date YYYY-MM-DD
```

日期缺省为系统本地当天，根目录缺省来自 `RECORDINGS_ROOT`。未配置则询问位置，不全盘扫描。返回按时间排序的全部有效录音、日期依据和 `selected_paths`。读取失败与没有录音区分；设备日期不可靠时报告修改时间兜底的事实。

多条录音可逐条转写，按顺序合并到新文本并标注来源边界。编码、采样率等一致时才直接拼接音频。完整列表写入状态的 `input_sources`，不能只取最大文件。

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime

SCRIPTS = Path(__file__).resolve().parents[1] / "article-optimizer" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from prepare_run import clean_original
from find_recordings import collect


class WorkflowTests(unittest.TestCase):
    def test_original_preserves_lines_and_literal_trigger_words(self):
        raw = "TS 是正文里的缩写\r\n\r\n第一 段\r\n第二段\r\n"
        self.assertEqual(clean_original(raw), raw.replace("\r\n", "\n"))
        self.assertIn("第一段\n第二段", clean_original(raw, True))

    def test_prepare_and_validate_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            output = subprocess.check_output([sys.executable, str(SCRIPTS / "prepare_run.py"), "--workspace", temp, "--topic", "测试", "--text", "第一段\n\n第二段"], text=True)
            run = Path(output.strip())
            state = json.loads((run / "TRIM_STATE.json").read_text())
            self.assertEqual(state["original_sha256"], hashlib.sha256((run / "原始稿.txt").read_bytes()).hexdigest())
            subprocess.run([sys.executable, str(SCRIPTS / "validate_trim_run.py"), str(run)], check=True, capture_output=True)
            (run / "原始稿.txt").write_text("changed")
            result = subprocess.run([sys.executable, str(SCRIPTS / "validate_trim_run.py"), str(run)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_today_returns_all_in_time_order_and_ignores_resource_forks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            today = datetime.now().date()
            for hour in (12, 9):
                (root / f"recording_{today:%Y%m%d}_{hour:02}0000.wav").write_bytes(b"audio")
            (root / "._recording.wav").write_bytes(b"audio")
            result = collect(root, today, min_bytes=1)
            self.assertEqual(len(result["selected_paths"]), 2)
            self.assertTrue(result["selected_paths"][0].endswith("090000.wav"))

    def test_transcribe_refuses_to_overwrite_before_loading_model(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "original.wav").write_bytes(b"audio")
            (root / "原始稿.txt").write_text("keep me")
            result = subprocess.run([sys.executable, str(SCRIPTS / "trim-transcribe.py"), str(root / "original.wav"), "--out-dir", temp], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / "原始稿.txt").read_text(), "keep me")

    def test_website_reads_env_before_defaults_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            site = root / "site"
            site.mkdir()
            source = root / "article.md"
            source.write_text("# 文章\n\n测试正文。")
            envfile = root / "config.env"
            envfile.write_text(f'ARTICLE_SITE_ROOT="{site}"\nARTICLE_SITE_AUTHOR="Demo Author"\n')
            env = {k:v for k,v in os.environ.items() if not k.startswith("ARTICLE_SITE_")}
            subprocess.run([sys.executable, str(SCRIPTS / "website_publish.py"), "--env", str(envfile), "--title", "文章", "--content", str(source), "--skip-build"], env=env, check=True, capture_output=True)
            self.assertIn('author: "Demo Author"', next(site.rglob("*.md")).read_text())


if __name__ == "__main__":
    unittest.main()

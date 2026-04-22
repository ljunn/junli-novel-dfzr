import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "project_scaffold.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


class ProjectScaffoldTests(unittest.TestCase):
    def test_init_creates_project_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            self.assertTrue((project_dir / "docs" / "项目总纲.md").exists())
            self.assertTrue((project_dir / "docs" / "章节规划.md").exists())
            self.assertTrue((project_dir / "plot" / "伏笔记录.md").exists())
            self.assertTrue((project_dir / "runtime").exists())
            self.assertTrue((project_dir / "manuscript").exists())

    def test_prepare_chapter_creates_runtime_and_manuscript_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            prepare_result = run_cli(
                "prepare-chapter",
                str(project_dir),
                "--chapter-num",
                "7",
                "--chapter-title",
                "雨夜追凶",
            )
            self.assertEqual(prepare_result.returncode, 0, msg=prepare_result.stderr)

            self.assertTrue((project_dir / "runtime" / "chapter-0007.intent.md").exists())
            self.assertTrue((project_dir / "runtime" / "chapter-0007.scenes.md").exists())
            self.assertTrue((project_dir / "runtime" / "chapter-0007.trace.md").exists())
            self.assertTrue((project_dir / "manuscript" / "第0007章-雨夜追凶.md").exists())


if __name__ == "__main__":
    unittest.main()

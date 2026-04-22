import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "novel_pipeline.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        check=False,
    )


class NovelPipelineTests(unittest.TestCase):
    def test_bootstrap_writes_canonical_project_materials(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            payload = {
                "story_bible": {
                    "one_liner": "被逐出宗门的少年用禁术债务反向修仙。",
                    "genre_tone": "黑色仙侠",
                    "protagonist_gap": "只会赌命，不会信人",
                    "core_conflict": "要活下去就得借更大的债",
                    "stakes": "若失控会沦为宗门和邪祟共同的祭品",
                    "inciting_incident": "他在祭河夜借来不该借的命火",
                    "destination": "撕开宗门与河神交易的真相",
                    "volume_anchor": "第一卷先活着回宗，再抢走命册",
                    "reader_hooks": ["高压求生", "禁术反噬", "反杀宗门"],
                },
                "worldview": {
                    "most_valuable": "寿命",
                    "most_dangerous": "命火债",
                    "beneficiaries": "上三宗和河神契约者",
                    "oppressed": "边地祭民",
                    "untouchable_rules": "凡人不得私借命火",
                    "how_it_blocks_protagonist": "主角每次动手都会透支剩余寿元",
                },
                "rules": {
                    "genre_promise": "高压仙侠爽文",
                    "style_limits": "单 POV，贴身近景",
                    "platform_constraints": "章末必须留钩",
                    "originality_boundary": "不直接借用成名门派设定",
                    "quality_gate": "每章有回报和新债",
                },
                "author_intent": {
                    "reader_promise": "压着打也能反咬一口",
                    "non_negotiable": "代价感不能丢",
                    "human_ai_split": "AI 做结构和初稿，作者定最终文字",
                },
                "current_focus": {
                    "current_volume": "第一卷",
                    "current_phase": "命火入体",
                    "active_chapter": "第0001章",
                    "goal": "先搭起前十章推进链",
                    "constraints": "不能破坏寿命货币规则",
                },
                "chapter_plan": [
                    {
                        "chapter": 1,
                        "title": "祭河借火",
                        "goal": "让主角活过祭河夜",
                        "conflict": "宗门与河神两头索命",
                        "payoff": "命火入体",
                        "pressure": "他成了全城猎物",
                    }
                ],
                "characters": [
                    {
                        "name": "林舟",
                        "identity": "边地祭民",
                        "external_goal": "活下去并查清家族冤案",
                        "internal_gap": "不敢相信任何盟友",
                        "fear": "再一次亲手害死亲人",
                        "logic": "先活，再赌，再反杀",
                        "tension": "和河神代理人互相利用",
                        "ooc_guardrail": "不会无代价地圣母",
                    }
                ],
            }
            payload_path = project_dir / "bootstrap.json"
            payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

            result = run_cli("bootstrap", str(project_dir), "--payload-file", str(payload_path))
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            outline_text = (project_dir / "docs" / "项目总纲.md").read_text(encoding="utf-8")
            worldview_text = (project_dir / "docs" / "世界观.md").read_text(encoding="utf-8")
            character_text = (project_dir / "characters" / "林舟.md").read_text(encoding="utf-8")
            chapter_plan_text = (project_dir / "docs" / "章节规划.md").read_text(encoding="utf-8")
            current_focus_text = (project_dir / "docs" / "当前焦点.md").read_text(encoding="utf-8")

            self.assertIn("被逐出宗门的少年用禁术债务反向修仙。", outline_text)
            self.assertIn("寿命", worldview_text)
            self.assertIn("林舟", character_text)
            self.assertIn("祭河借火", chapter_plan_text)
            self.assertIn("第一卷", current_focus_text)

    def test_next_and_finish_chapter_close_the_loop(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            next_result = run_cli(
                "next-chapter",
                str(project_dir),
                "--chapter-title",
                "雨夜追凶",
                "--pov",
                "林舟",
                "--goal",
                "查清血书来源",
                "--conflict",
                "巡夜司封锁城门",
                "--payoff",
                "拿到命册钥匙",
                "--end-pressure",
                "真凶先一步灭口",
            )
            self.assertEqual(next_result.returncode, 0, msg=next_result.stderr)

            intent_path = project_dir / "runtime" / "chapter-0001.intent.md"
            scenes_path = project_dir / "runtime" / "chapter-0001.scenes.md"
            trace_path = project_dir / "runtime" / "chapter-0001.trace.md"
            context_path = project_dir / "runtime" / "chapter-0001.context.json"
            rule_stack_path = project_dir / "runtime" / "chapter-0001.rule-stack.yaml"
            manuscript_path = project_dir / "manuscript" / "第0001章-雨夜追凶.md"

            self.assertTrue(intent_path.exists())
            self.assertTrue(scenes_path.exists())
            self.assertTrue(trace_path.exists())
            self.assertTrue(context_path.exists())
            self.assertTrue(rule_stack_path.exists())
            self.assertTrue(manuscript_path.exists())

            task_log_text = (project_dir / "task_log.md").read_text(encoding="utf-8")
            current_focus_text = (project_dir / "docs" / "当前焦点.md").read_text(encoding="utf-8")
            self.assertIn("第0001章", task_log_text)
            self.assertIn("第0001章", current_focus_text)

            manuscript_path.write_text(
                "# 第0001章 雨夜追凶\n\n"
                "雨从城楼檐角砸下来，像有人在黑夜里翻一盆滚烫的铁砂。\n"
                "林舟把那张血书按进袖口，转身时，巷口已经立着巡夜司的灯。\n",
                encoding="utf-8",
            )

            finish_result = run_cli(
                "finish-chapter",
                str(project_dir),
                "--chapter-num",
                "1",
                "--chapter-title",
                "雨夜追凶",
                "--summary",
                "林舟冒雨夺走命册钥匙，却发现灭口者来自宗门内线。",
                "--next-goal",
                "查出宗门内线身份",
                "--plot-note",
                "血书背后还有第二名写信人",
                "--foreshadow",
                "第二封血书|第0001章|第0005章|活跃|写信人并非一人",
                "--timeline-event",
                "雨夜|林舟夺走命册钥匙|林舟,巡夜司|宗门开始追杀",
            )
            self.assertEqual(finish_result.returncode, 0, msg=finish_result.stderr)

            chapter_plan_text = (project_dir / "docs" / "章节规划.md").read_text(encoding="utf-8")
            task_log_text = (project_dir / "task_log.md").read_text(encoding="utf-8")
            foreshadow_text = (project_dir / "plot" / "伏笔记录.md").read_text(encoding="utf-8")
            timeline_text = (project_dir / "plot" / "时间线.md").read_text(encoding="utf-8")
            trace_text = trace_path.read_text(encoding="utf-8")

            self.assertIn("雨夜追凶", chapter_plan_text)
            self.assertIn("林舟冒雨夺走命册钥匙", task_log_text)
            self.assertIn("查出宗门内线身份", task_log_text)
            self.assertIn("第二封血书", foreshadow_text)
            self.assertIn("宗门开始追杀", timeline_text)
            self.assertIn("完成摘要", trace_text)

    def test_finish_rejects_missing_or_empty_chapter_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            missing_finish = run_cli(
                "finish-chapter",
                str(project_dir),
                "--chapter-num",
                "1",
                "--chapter-title",
                "幽灵章",
                "--summary",
                "这章其实不存在。",
            )
            self.assertNotEqual(missing_finish.returncode, 0)
            self.assertIn("缺少意图卡", missing_finish.stderr)
            self.assertIn("缺少正文文件", missing_finish.stderr)

            task_log_text = (project_dir / "task_log.md").read_text(encoding="utf-8")
            self.assertIn("创作阶段：立项中", task_log_text)
            self.assertIn("累计完成章节：0", task_log_text)
            self.assertFalse((project_dir / "runtime" / "chapter-0001.trace.md").exists())

            next_result = run_cli(
                "next-chapter",
                str(project_dir),
                "--chapter-title",
                "空壳章",
                "--goal",
                "先把过程文件生成出来",
            )
            self.assertEqual(next_result.returncode, 0, msg=next_result.stderr)

            empty_finish = run_cli(
                "finish-chapter",
                str(project_dir),
                "--chapter-num",
                "1",
                "--chapter-title",
                "空壳章",
                "--summary",
                "正文还没写完。",
            )
            self.assertNotEqual(empty_finish.returncode, 0)
            self.assertIn("正文为空", empty_finish.stderr)

            task_log_text = (project_dir / "task_log.md").read_text(encoding="utf-8")
            self.assertIn("当前处理章节：第0001章-空壳章", task_log_text)
            self.assertIn("累计完成章节：0", task_log_text)

    def test_multichapter_history_and_resume_only_count_completed_chapters(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            first_body = (
                "# 第0001章 第一章\n\n"
                "夜风从断桥底下穿过去，像有人在桥洞深处磨刀。\n"
                "林舟背着抢来的木匣，踩着湿滑石阶往上跑，每一步都像踩在别人的命上。\n"
            )
            second_body = (
                "# 第0002章 第二章\n\n"
                "城门刚开一道缝，巡夜司的铁铃就响了。\n"
                "他知道自己只要慢半拍，昨夜抢来的命册就会变成追魂索。\n"
            )

            first_next = run_cli(
                "next-chapter",
                str(project_dir),
                "--chapter-title",
                "第一章",
                "--goal",
                "先抢到木匣",
            )
            self.assertEqual(first_next.returncode, 0, msg=first_next.stderr)
            first_manuscript = project_dir / "manuscript" / "第0001章-第一章.md"
            first_manuscript.write_text(first_body, encoding="utf-8")

            first_finish = run_cli(
                "finish-chapter",
                str(project_dir),
                "--chapter-num",
                "1",
                "--chapter-title",
                "第一章",
                "--summary",
                "林舟抢到木匣，却被巡夜司盯上了。",
                "--next-goal",
                "带着木匣冲出城门",
            )
            self.assertEqual(first_finish.returncode, 0, msg=first_finish.stderr)

            second_next = run_cli(
                "next-chapter",
                str(project_dir),
                "--chapter-title",
                "第二章",
                "--goal",
                "带着木匣冲出城门",
            )
            self.assertEqual(second_next.returncode, 0, msg=second_next.stderr)

            resume_before = run_cli("resume", str(project_dir))
            self.assertEqual(resume_before.returncode, 0, msg=resume_before.stderr)
            self.assertIn("累计章节/字数: 1 / ", resume_before.stdout)

            second_manuscript = project_dir / "manuscript" / "第0002章-第二章.md"
            second_manuscript.write_text(second_body, encoding="utf-8")
            second_finish = run_cli(
                "finish-chapter",
                str(project_dir),
                "--chapter-num",
                "2",
                "--chapter-title",
                "第二章",
                "--summary",
                "林舟带着木匣杀出半座城，城门外却有人等着截他。",
            )
            self.assertEqual(second_finish.returncode, 0, msg=second_finish.stderr)

            chapter_plan_text = (project_dir / "docs" / "章节规划.md").read_text(encoding="utf-8")
            self.assertIn("- [x] 第0001章：第一章", chapter_plan_text)
            self.assertIn("- [x] 第0002章：第二章", chapter_plan_text)
            self.assertEqual(chapter_plan_text.count("- [x] 第"), 2)

            resume_after = run_cli("resume", str(project_dir))
            self.assertEqual(resume_after.returncode, 0, msg=resume_after.stderr)
            self.assertIn("累计章节/字数: 2 / ", resume_after.stdout)

    def test_rule_stack_quotes_yaml_sensitive_values(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            next_result = run_cli(
                "next-chapter",
                str(project_dir),
                "--chapter-title",
                "标题: 风险",
                "--pov",
                "林舟: 第一视角",
                "--goal",
                "抢下令牌: 否则会死",
            )
            self.assertEqual(next_result.returncode, 0, msg=next_result.stderr)

            rule_stack_text = (project_dir / "runtime" / "chapter-0001.rule-stack.yaml").read_text(
                encoding="utf-8"
            )
            self.assertIn('title: "标题: 风险"', rule_stack_text)
            self.assertIn('promise: "抢下令牌: 否则会死"', rule_stack_text)
            self.assertIn('pov: "林舟: 第一视角"', rule_stack_text)

    def test_review_writes_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            chapter_path = project_dir / "manuscript" / "第0001章-套话测试.md"
            chapter_path.write_text(
                "# 第0001章 套话测试\n\n"
                "## 正文\n\n"
                "在这一刻，他的心中不由得涌起一种复杂的感觉，仿佛一切都变得不同了。\n"
                "某种难以言说的情绪在空气里慢慢弥漫开来。\n"
                "总之，这一切才刚刚开始。\n",
                encoding="utf-8",
            )

            review_result = run_cli("review", str(chapter_path), "--project-path", str(project_dir))
            self.assertEqual(review_result.returncode, 0, msg=review_result.stderr)

            report_path = project_dir / "审阅意见" / "第0001章-套话测试-审阅.md"
            self.assertTrue(report_path.exists())
            report_text = report_path.read_text(encoding="utf-8")

            self.assertIn("P1", report_text)
            self.assertIn("## 正文", report_text)
            self.assertIn("在这一刻", report_text)

    def test_governance_updates_stage_plan_and_change_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            init_result = run_cli("init", "测试小说", "--target-dir", temp_dir)
            self.assertEqual(init_result.returncode, 0, msg=init_result.stderr)

            project_dir = Path(temp_dir) / "测试小说"
            governance_result = run_cli(
                "governance",
                str(project_dir),
                "--current-volume",
                "第一卷",
                "--current-phase",
                "命火入体",
                "--phase-promise",
                "主角先活下来并撕开宗门缝隙",
                "--phase-main-problem",
                "命火债越滚越大",
                "--phase-climax",
                "夺走命册",
                "--phase-payoff",
                "确认宗门内鬼身份",
                "--new-risk",
                "河神开始索取正价",
                "--fulfilled",
                "主角已活过祭河夜",
                "--pending",
                "宗门内鬼尚未曝光",
                "--risk",
                "命火债失控",
                "--next-action",
                "追查第二封血书",
                "--next-action",
                "逼出内鬼失误",
                "--change-scope",
                "第一卷节奏重排",
                "--change-reason",
                "强化前三章钩子",
                "--change-impact",
                "需要同步章节规划和伏笔回收点",
            )
            self.assertEqual(governance_result.returncode, 0, msg=governance_result.stderr)

            stage_plan_text = (project_dir / "docs" / "阶段规划.md").read_text(encoding="utf-8")
            change_log_text = (project_dir / "docs" / "变更日志.md").read_text(encoding="utf-8")
            task_log_text = (project_dir / "task_log.md").read_text(encoding="utf-8")

            self.assertIn("第一卷", stage_plan_text)
            self.assertIn("命火债失控", stage_plan_text)
            self.assertIn("第一卷节奏重排", change_log_text)
            self.assertIn("命火入体", task_log_text)


if __name__ == "__main__":
    unittest.main()

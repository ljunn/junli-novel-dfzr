#!/usr/bin/env python3
"""Unified workflow CLI for the junli-novel-dfzr skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


MODE_LABELS = {
    "single": "单主角线",
    "dual": "双主角 / 双视角",
    "ensemble": "群像多线",
}


AI_TELL_PATTERNS = (
    "在这一刻",
    "心中",
    "不由得",
    "某种",
    "仿佛",
    "难以言说",
)


ENDING_SUMMARY_PATTERNS = (
    "总之",
    "这一切才刚刚开始",
    "一切才刚刚开始",
    "故事才刚刚开始",
)


def sanitize_filename(value: str) -> str:
    text = re.sub(r'[\\/:*?"<>|]+', "_", value).strip()
    return text or "未命名章节"


def chapter_tag(chapter_num: int) -> str:
    return f"chapter-{chapter_num:04d}"


def chapter_label(chapter_num: int) -> str:
    return f"第{chapter_num:04d}章"


def chapter_file_name(chapter_num: int, chapter_title: str) -> str:
    return f"{chapter_label(chapter_num)}-{sanitize_filename(chapter_title)}.md"


def read_text(path: Path, default: str = "") -> str:
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_if_needed(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        return False
    write_text(path, content)
    return True


def upsert_key_value(text: str, key: str, value: str) -> str:
    pattern = rf"(?m)^{re.escape(key)}.*$"
    replacement = f"{key}{value}"
    if re.search(pattern, text):
        return re.sub(pattern, replacement, text, count=1)
    lines = text.rstrip().splitlines()
    if lines:
        lines.insert(1, replacement)
        return "\n".join(lines) + "\n"
    return replacement + "\n"


def get_key_value(text: str, key: str, default: str = "未记录") -> str:
    match = re.search(rf"(?m)^{re.escape(key)}(.*)$", text)
    if not match:
        return default
    value = match.group(1).strip()
    return value or default


def get_int_key_value(text: str, key: str, default: int = 0) -> int:
    value = get_key_value(text, key, "")
    match = re.search(r"-?\d+", value)
    if not match:
        return default
    return int(match.group(0))


def replace_section(text: str, heading: str, lines: list[str]) -> str:
    section_body = "\n".join(lines).rstrip() + "\n"
    pattern = rf"(?ms)(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    match = re.search(pattern, text)
    if match:
        return text[: match.start(2)] + section_body + text[match.end(2) :]
    suffix = f"\n## {heading}\n{section_body}"
    return text.rstrip() + suffix


def replace_subsection(text: str, heading: str, lines: list[str]) -> str:
    section_body = "\n".join(lines).rstrip() + "\n"
    pattern = rf"(?ms)(^### {re.escape(heading)}\n)(.*?)(?=^### |\n## |\Z)"
    match = re.search(pattern, text)
    if match:
        return text[: match.start(2)] + section_body + text[match.end(2) :]
    suffix = f"\n### {heading}\n{section_body}"
    return text.rstrip() + suffix


def parse_markdown_table_rows(text: str, heading: str) -> tuple[str, list[str]] | None:
    pattern = rf"(?ms)(^## {re.escape(heading)}\n\n\|.*?\n\|[-:| ]+\n)(.*?)(?=^\n## |\n### |\Z)"
    match = re.search(pattern, text)
    if not match:
        return None
    prefix = match.group(1)
    rows = [line for line in match.group(2).splitlines() if line.strip()]
    return prefix, rows


def get_subsection_lines(text: str, heading: str) -> list[str]:
    pattern = rf"(?ms)^### {re.escape(heading)}\n(.*?)(?=^### |\n## |\Z)"
    match = re.search(pattern, text)
    if not match:
        return []
    return [line.strip() for line in match.group(1).splitlines() if line.strip()]


def markdown_cell(value: Any) -> str:
    text = str(value or "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("|", r"\|")
    return text.replace("\n", "<br>")


def markdown_row(cells: list[Any]) -> str:
    return "| " + " | ".join(markdown_cell(cell) for cell in cells) + " |"


def render_task_log(project_name: str) -> str:
    return f"""# 任务日志

书名：{project_name}
创作阶段：立项中
最新章节：无
当前处理章节：无
累计完成章节：0
累计完成字数：0
目标总字数：未记录
目标卷数：未记录
当前卷：未记录
当前阶段：未记录
当前阶段目标：未记录
当前视角：未记录
主角位置：未记录
主角状态：未记录
下一章目标：未记录
设定变更待同步：无

## 最近摘要
- 暂无

## 活跃伏笔
- 暂无

## 待办
- 暂无
"""


def render_project_files(project_name: str, mode: str) -> dict[str, str]:
    mode_label = MODE_LABELS[mode]
    return {
        "docs/项目总纲.md": f"""# 项目总纲

项目名：{project_name}
模式：{mode_label}

## 一句话卖点

## 题材与调性

## 主角核心缺口

## 核心冲突

## 失败代价

## 起爆事件

## 终点站

## 第一卷锚点

## 读者主要追点
""",
        "docs/章节规划.md": """# 章节规划

- 已完成章节数：0 章
- 累计字数：0 字
- 完成进度：0%

## 章节规划

| 章节 | 标题 | 本章目标 | 核心冲突 | 回报 | 章末压力 |
| --- | --- | --- | --- | --- | --- |

## 章节摘要
（后续章节摘要依次追加）

### 待创作
- 暂无

### 进行中
- 暂无

### 已完成
- 暂无
""",
        "docs/卷纲.md": """# 卷纲

## 第一卷
- 阶段承诺：
- 阶段主问题：
- 阶段高潮：
- 阶段回报：
- 阶段结束后新增风险：
""",
        "docs/阶段规划.md": """# 阶段规划

当前卷：
当前阶段：
阶段承诺：
阶段主问题：
阶段高潮：
阶段回报：
阶段结束后新增风险：

## 已兑现承诺
- 暂无

## 未兑现承诺
- 暂无

## 活跃风险
- 暂无

## 下一阶段 3 个核心动作
- 暂无
""",
        "docs/变更日志.md": """# 变更日志

| 日期 | 变更范围 | 改动原因 | 连带影响 |
| --- | --- | --- | --- |
""",
        "docs/世界观.md": """# 世界观

## 世界最值钱的东西

## 世界最危险 / 最禁忌的东西

## 谁因此受益

## 谁因此被压制

## 不可触碰的规则

## 主角如何被这套规则卡住
""",
        "docs/法则.md": """# 法则

## 题材承诺

## POV / 风格限制

## 平台约束

## 原创边界

## 质量门
""",
        "docs/作者意图.md": """# 作者意图

这本书这阶段最想兑现给读者的东西：

这轮最不能丢的卖点：

人机分工：
""",
        "docs/当前焦点.md": """# 当前焦点

当前卷：
当前阶段：
当前进行中章节：
本轮目标：
本轮限制：

## 近期焦点
- 暂无

## 禁止偏航
- 暂无
""",
        "plot/伏笔记录.md": """# 伏笔记录

| 伏笔 | 首次出现 | 计划回收 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
""",
        "plot/时间线.md": """# 时间线

| 时间点 | 事件 | 涉及角色 | 影响 |
| --- | --- | --- | --- |
""",
        "task_log.md": render_task_log(project_name),
    }


def render_character_card(character: dict[str, Any]) -> str:
    return f"""# {character.get("name", "未命名角色")}

角色名：{character.get("name", "")}
身份与位置：{character.get("identity", "")}
外部目标：{character.get("external_goal", "")}
内部缺口：{character.get("internal_gap", "")}
最大恐惧：{character.get("fear", "")}
行动逻辑：{character.get("logic", "")}
关系张力：{character.get("tension", "")}
OOC 警报线：{character.get("ooc_guardrail", "")}
"""


def render_story_bible(payload: dict[str, Any], project_name: str, mode_label: str) -> str:
    hooks = payload.get("reader_hooks") or []
    hook_text = "、".join(str(item) for item in hooks) if hooks else ""
    return f"""# 项目总纲

项目名：{project_name}
模式：{mode_label}

## 一句话卖点
{payload.get("one_liner", "")}

## 题材与调性
{payload.get("genre_tone", "")}

## 主角核心缺口
{payload.get("protagonist_gap", "")}

## 核心冲突
{payload.get("core_conflict", "")}

## 失败代价
{payload.get("stakes", "")}

## 起爆事件
{payload.get("inciting_incident", "")}

## 终点站
{payload.get("destination", "")}

## 第一卷锚点
{payload.get("volume_anchor", "")}

## 读者主要追点
{hook_text}
"""


def render_worldview(payload: dict[str, Any]) -> str:
    return f"""# 世界观

## 世界最值钱的东西
{payload.get("most_valuable", "")}

## 世界最危险 / 最禁忌的东西
{payload.get("most_dangerous", "")}

## 谁因此受益
{payload.get("beneficiaries", "")}

## 谁因此被压制
{payload.get("oppressed", "")}

## 不可触碰的规则
{payload.get("untouchable_rules", "")}

## 主角如何被这套规则卡住
{payload.get("how_it_blocks_protagonist", "")}
"""


def render_rules(payload: dict[str, Any]) -> str:
    return f"""# 法则

## 题材承诺
{payload.get("genre_promise", "")}

## POV / 风格限制
{payload.get("style_limits", "")}

## 平台约束
{payload.get("platform_constraints", "")}

## 原创边界
{payload.get("originality_boundary", "")}

## 质量门
{payload.get("quality_gate", "")}
"""


def render_author_intent(payload: dict[str, Any]) -> str:
    return f"""# 作者意图

这本书这阶段最想兑现给读者的东西：
{payload.get("reader_promise", "")}

这轮最不能丢的卖点：
{payload.get("non_negotiable", "")}

人机分工：
{payload.get("human_ai_split", "")}
"""


def render_current_focus(payload: dict[str, Any]) -> str:
    return f"""# 当前焦点

当前卷：{payload.get("current_volume", "")}
当前阶段：{payload.get("current_phase", "")}
当前进行中章节：{payload.get("active_chapter", "")}
本轮目标：{payload.get("goal", "")}
本轮限制：{payload.get("constraints", "")}

## 近期焦点
- {payload.get("goal", "暂未记录")}

## 禁止偏航
- {payload.get("constraints", "暂未记录")}
"""


def render_chapter_plan(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# 章节规划",
        "",
        "- 已完成章节数：0 章",
        "- 累计字数：0 字",
        "- 完成进度：0%",
        "",
        "## 章节规划",
        "",
        "| 章节 | 标题 | 本章目标 | 核心冲突 | 回报 | 章末压力 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            markdown_row(
                [
                    chapter_label(int(row.get("chapter", 0))) if row.get("chapter") else "",
                    row.get("title", ""),
                    row.get("goal", ""),
                    row.get("conflict", ""),
                    row.get("payoff", ""),
                    row.get("pressure", ""),
                ]
            )
        )
    lines.extend(
        [
            "",
            "## 章节摘要",
            "（后续章节摘要依次追加）",
            "",
            "### 待创作",
            "- 暂无",
            "",
            "### 进行中",
            "- 暂无",
            "",
            "### 已完成",
            "- 暂无",
        ]
    )
    return "\n".join(lines) + "\n"


def render_volume_outline(rows: list[dict[str, Any]]) -> str:
    lines = ["# 卷纲", ""]
    if not rows:
        rows = [{"name": "第一卷"}]
    for row in rows:
        lines.extend(
            [
                f"## {row.get('name', '未命名卷')}",
                f"- 阶段承诺：{row.get('promise', '')}",
                f"- 阶段主问题：{row.get('main_problem', '')}",
                f"- 阶段高潮：{row.get('climax', '')}",
                f"- 阶段回报：{row.get('payoff', '')}",
                f"- 阶段结束后新增风险：{row.get('new_risk', '')}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_stage_plan(payload: dict[str, Any]) -> str:
    fulfilled = payload.get("fulfilled") or ["暂无"]
    pending = payload.get("pending") or ["暂无"]
    risks = payload.get("risks") or ["暂无"]
    next_actions = payload.get("next_actions") or ["暂无"]
    return "\n".join(
        [
            "# 阶段规划",
            "",
            f"当前卷：{payload.get('current_volume', '')}",
            f"当前阶段：{payload.get('current_phase', '')}",
            f"阶段承诺：{payload.get('phase_promise', '')}",
            f"阶段主问题：{payload.get('phase_main_problem', '')}",
            f"阶段高潮：{payload.get('phase_climax', '')}",
            f"阶段回报：{payload.get('phase_payoff', '')}",
            f"阶段结束后新增风险：{payload.get('new_risk', '')}",
            "",
            "## 已兑现承诺",
            *[f"- {item}" for item in fulfilled],
            "",
            "## 未兑现承诺",
            *[f"- {item}" for item in pending],
            "",
            "## 活跃风险",
            *[f"- {item}" for item in risks],
            "",
            "## 下一阶段 3 个核心动作",
            *[f"- {item}" for item in next_actions],
            "",
        ]
    )


def count_story_units(text: str) -> int:
    chinese_chars = re.findall(r"[\u4e00-\u9fff]", text)
    latin_words = re.findall(r"[A-Za-z0-9_]+", text)
    return len(chinese_chars) + len(latin_words)


def extract_story_body(text: str) -> str:
    cleaned = re.sub(r"^# .*$", "", text, count=1, flags=re.MULTILINE).strip()
    cleaned = cleaned.replace("## 正文", "").strip()
    return cleaned


def parse_chapter_number_from_name(name: str) -> int | None:
    match = re.search(r"第0*(\d+)章", name)
    if match:
        return int(match.group(1))
    match = re.search(r"chapter-(\d+)", name)
    if match:
        return int(match.group(1))
    return None


def get_chapter_files(project_dir: Path) -> list[Path]:
    manuscript_dir = project_dir / "manuscript"
    if not manuscript_dir.exists():
        return []
    paths = []
    for path in sorted(manuscript_dir.glob("*.md")):
        if parse_chapter_number_from_name(path.name) is not None:
            paths.append(path)
    return paths


def compute_manuscript_stats(project_dir: Path) -> tuple[int, int]:
    chapter_files = get_chapter_files(project_dir)
    total_words = 0
    for chapter_path in chapter_files:
        total_words += count_story_units(extract_story_body(read_text(chapter_path)))
    return len(chapter_files), total_words


def collect_completed_chapter_nums(project_dir: Path) -> list[int]:
    chapter_plan = read_text(project_dir / "docs" / "章节规划.md")
    completed = set()
    for line in get_subsection_lines(chapter_plan, "已完成"):
        if line == "- 暂无":
            continue
        chapter_num = parse_chapter_number_from_name(line)
        if chapter_num is not None:
            completed.add(chapter_num)
    return sorted(completed)


def get_completed_stats(project_dir: Path, extra_completed: dict[int, Path] | None = None) -> tuple[int, int]:
    task_log = read_text(project_dir / "task_log.md")
    task_log_count = get_int_key_value(task_log, "累计完成章节：", 0)
    task_log_words = get_int_key_value(task_log, "累计完成字数：", 0)

    completed_nums = set(collect_completed_chapter_nums(project_dir))
    chapter_map: dict[int, Path] = {}
    for path in get_chapter_files(project_dir):
        chapter_num = parse_chapter_number_from_name(path.name)
        if chapter_num is not None:
            chapter_map[chapter_num] = path

    if extra_completed:
        completed_nums.update(extra_completed)
        chapter_map.update(extra_completed)

    if not completed_nums:
        return task_log_count, task_log_words

    total_words = 0
    for chapter_num in sorted(completed_nums):
        chapter_path = chapter_map.get(chapter_num)
        if chapter_path is None:
            continue
        total_words += count_story_units(extract_story_body(read_text(chapter_path)))

    computed_count = len(completed_nums)
    if task_log_count > computed_count:
        return task_log_count, task_log_words
    return computed_count, total_words


def latest_chapter_num(project_dir: Path) -> int:
    nums = [parse_chapter_number_from_name(path.name) for path in get_chapter_files(project_dir)]
    clean = [num for num in nums if num is not None]
    return max(clean, default=0)


def runtime_paths(project_dir: Path, chapter_num: int, chapter_title: str) -> dict[str, Path]:
    prefix = chapter_tag(chapter_num)
    manuscript_name = chapter_file_name(chapter_num, chapter_title)
    runtime_dir = project_dir / "runtime"
    return {
        "runtime_dir": runtime_dir,
        "intent": runtime_dir / f"{prefix}.intent.md",
        "scenes": runtime_dir / f"{prefix}.scenes.md",
        "trace": runtime_dir / f"{prefix}.trace.md",
        "context": runtime_dir / f"{prefix}.context.json",
        "rule_stack": runtime_dir / f"{prefix}.rule-stack.yaml",
        "manuscript": project_dir / "manuscript" / manuscript_name,
    }


def read_project_state(project_dir: Path) -> dict[str, Any]:
    task_log = read_text(project_dir / "task_log.md")
    focus = read_text(project_dir / "docs" / "当前焦点.md")
    outline = read_text(project_dir / "docs" / "项目总纲.md")
    chapter_count, total_words = get_completed_stats(project_dir)
    return {
        "project_dir": str(project_dir),
        "project_name": get_key_value(task_log, "书名：", project_dir.name),
        "stage": get_key_value(task_log, "创作阶段：", "未知"),
        "latest_chapter": get_key_value(task_log, "最新章节：", "无"),
        "current_chapter": get_key_value(task_log, "当前处理章节：", "无"),
        "current_volume": get_key_value(task_log, "当前卷：", get_key_value(focus, "当前卷：", "未记录")),
        "current_phase": get_key_value(task_log, "当前阶段：", get_key_value(focus, "当前阶段：", "未记录")),
        "phase_goal": get_key_value(task_log, "当前阶段目标：", "未记录"),
        "viewpoint": get_key_value(task_log, "当前视角：", "未记录"),
        "next_goal": get_key_value(task_log, "下一章目标：", "未记录"),
        "chapter_count": chapter_count,
        "total_words": total_words,
        "outline_excerpt": excerpt_text(outline, max_chars=240),
    }


def excerpt_text(text: str, max_chars: int = 240) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rstrip() + "..."


def render_chapter_intent(
    chapter_num: int,
    chapter_title: str,
    *,
    pov: str,
    info_boundary: str,
    hidden_info: str,
    goal: str,
    conflict: str,
    payoff: str,
    end_pressure: str,
) -> str:
    return f"""# {chapter_label(chapter_num)} 意图卡

本章主 POV：{pov}
信息边界：{info_boundary}
隐藏信息：{hidden_info}
本章目标：{goal}
核心冲突：{conflict}
回报类型：{payoff}
章末压力：{end_pressure}
"""


def render_chapter_scenes(
    chapter_num: int,
    chapter_title: str,
    *,
    goal: str,
    conflict: str,
    payoff: str,
    end_pressure: str,
) -> str:
    label = chapter_label(chapter_num)
    return f"""# {label} 场景卡

## 场景 1
场景名：{chapter_title} / 起压
场景类型：铺垫 / 冲突
状态变化：从被动承压到被迫行动
行动目的：让主角先碰到本章主问题
明面阻力：{conflict or "外部封锁与即时危险"}
暗线：旧悬念开始回响
副功能：开场钩子、POV 锚定

## 场景 2
场景名：{chapter_title} / 逼选
场景类型：冲突 / 转折
状态变化：从试探到代价兑现
行动目的：逼主角为 {goal or "当前目标"} 付出选择
明面阻力：压力升级，旧债追上来
暗线：关系张力或规则代价显影
副功能：补充信息、强化人物逻辑

## 场景 3
场景名：{chapter_title} / 回报与新债
场景类型：高潮 / 收尾
状态变化：从局部得手到更大麻烦
行动目的：兑现 {payoff or "一次实感回报"}
明面阻力：更强敌人或更硬规则登场
暗线：{end_pressure or "章末留下未决压力"}
副功能：章末钩子、下一章驱动
"""


def render_trace_markdown(
    project_dir: Path,
    chapter_num: int,
    chapter_title: str,
    *,
    goal: str,
    conflict: str,
    output_paths: dict[str, Path],
) -> str:
    label = chapter_label(chapter_num)
    relative_outputs = [
        output_paths["intent"].relative_to(project_dir),
        output_paths["scenes"].relative_to(project_dir),
        output_paths["trace"].relative_to(project_dir),
        output_paths["context"].relative_to(project_dir),
        output_paths["rule_stack"].relative_to(project_dir),
        output_paths["manuscript"].relative_to(project_dir),
    ]
    return "\n".join(
        [
            f"# {label} 执行追踪",
            "",
            "本道：围绕单章读者承诺推进核心压力和回报。",
            "法栈：遵守 POV 边界、章末造压、正文与过程文件分离。",
            "术路：resume -> intent -> scenes -> manuscript -> finish -> review。",
            "器单：意图卡、场景卡、追踪文件、context、rule-stack、正文文件。",
            "",
            "## 输入来源",
            "- docs/项目总纲.md",
            "- docs/章节规划.md",
            "- docs/卷纲.md",
            "- docs/阶段规划.md",
            "- docs/当前焦点.md",
            "- plot/伏笔记录.md",
            "- plot/时间线.md",
            "- characters/*.md",
            "",
            "## 本章决策",
            f"- 标题：{chapter_title}",
            f"- 目标：{goal or '推进当前主线'}",
            f"- 核心冲突：{conflict or '外部阻力与内在代价共同压进'}",
            "",
            "## 输出文件",
            *[f"- {path.as_posix()}" for path in relative_outputs],
            "",
            "## 完成摘要",
            "- 待 finish-chapter 回写。",
        ]
    ) + "\n"


def render_context_payload(state: dict[str, Any], chapter_num: int, chapter_title: str, args: argparse.Namespace) -> dict[str, Any]:
    return {
        "chapter": chapter_num,
        "title": chapter_title,
        "goal": args.goal or state.get("next_goal") or "推进当前主线",
        "conflict": args.conflict or "",
        "payoff": args.payoff or "",
        "endPressure": args.end_pressure or "",
        "currentVolume": state.get("current_volume", "未记录"),
        "currentPhase": state.get("current_phase", "未记录"),
        "phaseGoal": state.get("phase_goal", "未记录"),
        "viewpoint": args.pov or state.get("viewpoint", "未记录"),
        "projectSummary": state.get("outline_excerpt", ""),
    }


def render_rule_stack_yaml(state: dict[str, Any], chapter_num: int, chapter_title: str, args: argparse.Namespace) -> str:
    goal = args.goal or state.get("next_goal") or "推进当前主线"
    pov = args.pov or state.get("viewpoint") or "未记录"
    lines = [
        f"chapter: {chapter_num}",
        f"title: {json.dumps(chapter_title, ensure_ascii=False)}",
        "dao:",
        f"  promise: {json.dumps(goal, ensure_ascii=False)}",
        "fa:",
        f"  pov: {json.dumps(pov, ensure_ascii=False)}",
        "  chapter_guardrails:",
        "    - 前 20% 必须有钩子",
        "    - 本章至少给一次回报",
        "    - 章末停在未决压力上",
        "shu:",
        "  workflow:",
        "    - resume",
        "    - intent",
        "    - scenes",
        "    - draft",
        "    - finish",
        "qi:",
        "  outputs:",
        "    - runtime intent",
        "    - runtime scenes",
        "    - runtime trace",
        "    - manuscript",
    ]
    return "\n".join(lines) + "\n"


def render_manuscript_shell(chapter_num: int, chapter_title: str) -> str:
    return f"""# {chapter_label(chapter_num)} {chapter_title}

## 正文

"""


def normalize_line_items(values: list[str] | None) -> list[str]:
    if not values:
        return []
    return [value.strip() for value in values if value.strip()]


def init_project(project_name: str, target_dir: str, mode: str, force: bool) -> int:
    target = Path(target_dir).expanduser().resolve()
    project_dir = target / project_name
    created: list[Path] = []
    skipped: list[Path] = []

    for relative_path, content in render_project_files(project_name, mode).items():
        path = project_dir / relative_path
        if write_if_needed(path, content, force):
            created.append(path)
        else:
            skipped.append(path)

    for directory in (
        project_dir / "characters",
        project_dir / "manuscript",
        project_dir / "runtime",
        project_dir / "审阅意见",
        project_dir / "marketing",
    ):
        directory.mkdir(parents=True, exist_ok=True)

    print(f"项目目录: {project_dir}")
    if created:
        print("创建文件:")
        for path in created:
            print(f"- {path}")
    if skipped:
        print("已存在，未覆盖:")
        for path in skipped:
            print(f"- {path}")
    return 0


def handle_init(args: argparse.Namespace) -> int:
    return init_project(args.project_name, args.target_dir, args.mode, args.force)


def load_payload(payload_file: str) -> dict[str, Any]:
    path = Path(payload_file).expanduser().resolve()
    return json.loads(path.read_text(encoding="utf-8"))


def update_bootstrap_task_log(project_dir: Path, payload: dict[str, Any]) -> None:
    task_log_path = project_dir / "task_log.md"
    task_log = read_text(task_log_path, render_task_log(project_dir.name))

    current_focus = payload.get("current_focus") or {}
    task_log = upsert_key_value(task_log, "创作阶段：", "立项完成")
    task_log = upsert_key_value(task_log, "当前卷：", str(current_focus.get("current_volume", "未记录")))
    task_log = upsert_key_value(task_log, "当前阶段：", str(current_focus.get("current_phase", "未记录")))
    task_log = upsert_key_value(task_log, "当前阶段目标：", str(current_focus.get("goal", "未记录")))
    task_log = upsert_key_value(task_log, "当前处理章节：", str(current_focus.get("active_chapter", "无")))
    task_log = upsert_key_value(task_log, "下一章目标：", str(current_focus.get("goal", "未记录")))
    write_text(task_log_path, task_log)


def handle_bootstrap(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    payload = load_payload(args.payload_file)
    mode_label = MODE_LABELS.get(args.mode or "single", MODE_LABELS["single"])

    story_bible = payload.get("story_bible") or {}
    worldview = payload.get("worldview") or {}
    rules = payload.get("rules") or {}
    author_intent = payload.get("author_intent") or {}
    current_focus = payload.get("current_focus") or {}
    chapter_plan = payload.get("chapter_plan") or []
    volume_outline = payload.get("volume_outline") or []
    stage_plan = payload.get("stage_plan") or {}
    characters = payload.get("characters") or []

    write_text(project_dir / "docs" / "项目总纲.md", render_story_bible(story_bible, project_dir.name, mode_label))
    write_text(project_dir / "docs" / "世界观.md", render_worldview(worldview))
    write_text(project_dir / "docs" / "法则.md", render_rules(rules))
    write_text(project_dir / "docs" / "作者意图.md", render_author_intent(author_intent))
    write_text(project_dir / "docs" / "当前焦点.md", render_current_focus(current_focus))
    if chapter_plan:
        write_text(project_dir / "docs" / "章节规划.md", render_chapter_plan(chapter_plan))
    if volume_outline:
        write_text(project_dir / "docs" / "卷纲.md", render_volume_outline(volume_outline))
    if stage_plan:
        write_text(project_dir / "docs" / "阶段规划.md", render_stage_plan(stage_plan))

    for character in characters:
        name = str(character.get("name", "")).strip() or "未命名角色"
        write_text(project_dir / "characters" / f"{sanitize_filename(name)}.md", render_character_card(character))

    update_bootstrap_task_log(project_dir, payload)

    print(f"已落盘立项材料: {project_dir}")
    print("- docs/项目总纲.md")
    print("- docs/世界观.md")
    print("- docs/法则.md")
    if characters:
        print(f"- characters/ ({len(characters)} 个角色文件)")
    return 0


def upsert_recent_summary(task_log: str, chapter_label_text: str, summary: str) -> str:
    pattern = r"(?ms)(^## 最近摘要\n)(.*?)(?=^## |\Z)"
    match = re.search(pattern, task_log)
    lines: list[str] = []
    if match:
        lines = [line for line in match.group(2).splitlines() if line.strip() and line.strip() != "- 暂无"]
    new_line = f"- {chapter_label_text}：{summary}"
    lines = [new_line] + [line for line in lines if line != new_line]
    return replace_section(task_log, "最近摘要", lines[:5] or ["- 暂无"])


def upsert_task_bullets(task_log: str, heading: str, new_line: str) -> str:
    pattern = rf"(?ms)(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    match = re.search(pattern, task_log)
    lines: list[str] = []
    if match:
        lines = [line for line in match.group(2).splitlines() if line.strip() and line.strip() != "- 暂无"]
    if new_line not in lines:
        lines.insert(0, new_line)
    return replace_section(task_log, heading, lines[:8] or ["- 暂无"])


def update_focus_for_chapter(project_dir: Path, chapter_label_text: str, goal: str) -> None:
    focus_path = project_dir / "docs" / "当前焦点.md"
    focus = read_text(focus_path)
    focus = upsert_key_value(focus, "当前进行中章节：", chapter_label_text)
    if goal:
        focus = upsert_key_value(focus, "本轮目标：", goal)
    focus_line = (
        f"- 下一章目标：{goal or '推进当前主线'}"
        if chapter_label_text == "无"
        else f"- {chapter_label_text}：{goal or '推进当前主线'}"
    )
    focus = replace_section(focus, "近期焦点", [focus_line])
    write_text(focus_path, focus)


def parse_intent_card(path: Path) -> dict[str, str]:
    text = read_text(path)
    return {
        "pov": get_key_value(text, "本章主 POV：", ""),
        "goal": get_key_value(text, "本章目标：", ""),
        "conflict": get_key_value(text, "核心冲突：", ""),
        "payoff": get_key_value(text, "回报类型：", ""),
        "end_pressure": get_key_value(text, "章末压力：", ""),
    }


def prepare_chapter(
    project_dir: Path,
    chapter_num: int,
    chapter_title: str,
    *,
    pov: str = "未记录",
    info_boundary: str = "只写本章主 POV 可见、可知、可误判的内容",
    hidden_info: str = "暂不揭露全貌，保留下一章推进空间",
    goal: str = "推进当前主线",
    conflict: str = "外部阻力与代价共同压进",
    payoff: str = "一次实感回报",
    end_pressure: str = "留下未决压力",
    force: bool = False,
) -> dict[str, Path]:
    paths = runtime_paths(project_dir, chapter_num, chapter_title)
    paths["runtime_dir"].mkdir(parents=True, exist_ok=True)
    write_if_needed(
        paths["intent"],
        render_chapter_intent(
            chapter_num,
            chapter_title,
            pov=pov,
            info_boundary=info_boundary,
            hidden_info=hidden_info,
            goal=goal,
            conflict=conflict,
            payoff=payoff,
            end_pressure=end_pressure,
        ),
        force,
    )
    write_if_needed(
        paths["scenes"],
        render_chapter_scenes(
            chapter_num,
            chapter_title,
            goal=goal,
            conflict=conflict,
            payoff=payoff,
            end_pressure=end_pressure,
        ),
        force,
    )
    write_if_needed(
        paths["trace"],
        render_trace_markdown(
            project_dir,
            chapter_num,
            chapter_title,
            goal=goal,
            conflict=conflict,
            output_paths=paths,
        ),
        force,
    )
    state = read_project_state(project_dir)
    write_if_needed(
        paths["context"],
        json.dumps(
            {
                "chapter": chapter_num,
                "title": chapter_title,
                "goal": goal,
                "conflict": conflict,
                "payoff": payoff,
                "endPressure": end_pressure,
                "currentVolume": state.get("current_volume", "未记录"),
                "currentPhase": state.get("current_phase", "未记录"),
                "phaseGoal": state.get("phase_goal", "未记录"),
                "viewpoint": pov,
                "projectSummary": state.get("outline_excerpt", ""),
            },
            ensure_ascii=False,
            indent=2,
        ),
        force,
    )
    write_if_needed(
        paths["rule_stack"],
        render_rule_stack_yaml(
            state,
            chapter_num,
            chapter_title,
            argparse.Namespace(
                goal=goal,
                pov=pov,
            ),
        ),
        force,
    )
    write_if_needed(paths["manuscript"], render_manuscript_shell(chapter_num, chapter_title), force)
    return paths


def handle_next_chapter(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    chapter_num = args.chapter_num or latest_chapter_num(project_dir) + 1
    chapter_title = args.chapter_title or "未命名章节"
    state = read_project_state(project_dir)
    paths = prepare_chapter(
        project_dir,
        chapter_num,
        chapter_title,
        pov=args.pov or state.get("viewpoint", "未记录"),
        info_boundary=args.info_boundary or "只写本章主 POV 可见、可知、可误判的内容",
        hidden_info=args.hidden_info or "真正关键的信息延迟到回报或章末揭露",
        goal=args.goal or state.get("next_goal", "推进当前主线"),
        conflict=args.conflict or "外部阻力与代价共同压进",
        payoff=args.payoff or "一次实感回报",
        end_pressure=args.end_pressure or "章末抬高未决压力",
        force=args.force,
    )
    trace = render_trace_markdown(
        project_dir,
        chapter_num,
        chapter_title,
        goal=args.goal or state.get("next_goal", "推进当前主线"),
        conflict=args.conflict or "外部阻力与代价共同压进",
        output_paths=paths,
    )
    context_payload = render_context_payload(state, chapter_num, chapter_title, args)
    rule_stack = render_rule_stack_yaml(state, chapter_num, chapter_title, args)
    write_if_needed(paths["trace"], trace, args.force)
    write_if_needed(paths["context"], json.dumps(context_payload, ensure_ascii=False, indent=2), args.force)
    write_if_needed(paths["rule_stack"], rule_stack, args.force)

    label = chapter_label(chapter_num)
    chapter_label_text = f"{label}-{chapter_title}"
    task_log_path = project_dir / "task_log.md"
    task_log = read_text(task_log_path, render_task_log(project_dir.name))
    task_log = upsert_key_value(task_log, "创作阶段：", "正文创作中")
    task_log = upsert_key_value(task_log, "当前处理章节：", chapter_label_text)
    task_log = upsert_key_value(task_log, "当前视角：", args.pov or state.get("viewpoint", "未记录"))
    task_log = upsert_key_value(task_log, "下一章目标：", args.goal or state.get("next_goal", "推进当前主线"))
    task_log = upsert_task_bullets(task_log, "待办", f"- 完成 {chapter_label_text} 初稿")
    write_text(task_log_path, task_log)
    update_focus_for_chapter(project_dir, label, args.goal or state.get("next_goal", "推进当前主线"))

    print(f"项目目录: {project_dir}")
    print(f"章节: {label}")
    print(f"意图文件: {paths['intent']}")
    print(f"场景卡文件: {paths['scenes']}")
    print(f"追踪文件: {paths['trace']}")
    print(f"context 文件: {paths['context']}")
    print(f"rule-stack 文件: {paths['rule_stack']}")
    print(f"正文文件: {paths['manuscript']}")
    return 0


def parse_foreshadow_row(raw: str) -> list[str]:
    parts = [part.strip() for part in raw.split("|")]
    while len(parts) < 5:
        parts.append("")
    return parts[:5]


def append_table_row(path: Path, row: list[str]) -> None:
    content = read_text(path)
    table_row = markdown_row(row)
    if table_row in content:
        return
    write_text(path, content.rstrip() + "\n" + table_row + "\n")


def update_chapter_plan_for_finish(
    project_dir: Path,
    chapter_num: int,
    chapter_title: str,
    summary: str,
    goal: str,
    conflict: str,
    payoff: str,
    end_pressure: str,
    chapter_count: int,
    total_words: int,
) -> None:
    path = project_dir / "docs" / "章节规划.md"
    text = read_text(path)
    parsed = parse_markdown_table_rows(text, "章节规划")
    target_label = chapter_label(chapter_num)
    new_row = markdown_row([target_label, chapter_title, goal, conflict, payoff, end_pressure])

    if parsed:
        prefix, rows = parsed
        updated_rows: list[str] = []
        replaced = False
        for row in rows:
            cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
            if cells and cells[0] == target_label:
                updated_rows.append(new_row)
                replaced = True
            else:
                updated_rows.append(row)
        if not replaced:
            updated_rows.append(new_row)
        table = prefix + "\n".join(updated_rows).rstrip() + "\n"
        text = re.sub(r"(?ms)^## 章节规划\n\n\|.*?\n\|[-:| ]+\n.*?(?=^\n## |\n### |\Z)", table.strip() + "\n", text)
    else:
        text += f"\n## 章节规划\n\n| 章节 | 标题 | 本章目标 | 核心冲突 | 回报 | 章末压力 |\n| --- | --- | --- | --- | --- | --- |\n{new_row}\n"

    text = re.sub(r"(?m)^- 已完成章节数：.*$", f"- 已完成章节数：{chapter_count} 章", text)
    text = re.sub(r"(?m)^- 累计字数：.*$", f"- 累计字数：{total_words} 字", text)
    in_progress = [
        line
        for line in get_subsection_lines(text, "进行中")
        if line != "- 暂无" and target_label not in line
    ]
    completed = [
        line
        for line in get_subsection_lines(text, "已完成")
        if line != "- 暂无" and target_label not in line
    ]
    completed.append(f"- [x] {target_label}：{chapter_title}")
    completed.sort(key=lambda line: parse_chapter_number_from_name(line) or 0)
    text = replace_subsection(text, "进行中", in_progress or ["- 暂无"])
    text = replace_subsection(text, "已完成", completed or ["- 暂无"])
    summary_line = f"### {target_label}：{chapter_title}\n**摘要**：{summary}"
    summary_pattern = rf"(?ms)^### {re.escape(target_label)}：.*?(?=^### 第\d+章|^## |\Z)"
    if re.search(summary_pattern, text):
        text = re.sub(summary_pattern, summary_line, text, count=1)
    else:
        summary_section = re.search(r"(?ms)(^## 章节摘要\n)(.*?)(?=^### 待创作|\Z)", text)
        if summary_section:
            body = summary_section.group(2).rstrip()
            if "（后续章节摘要依次追加）" in body:
                body = body + "\n\n" + summary_line + "\n"
            else:
                body = body + "\n\n" + summary_line + "\n"
            text = text[: summary_section.start(2)] + body + text[summary_section.end(2) :]
        else:
            text += f"\n## 章节摘要\n（后续章节摘要依次追加）\n\n{summary_line}\n"
    write_text(path, text)


def update_trace_finish(trace_path: Path, summary: str, next_goal: str) -> None:
    trace = read_text(trace_path)
    replacement = "## 完成摘要\n"
    lines = [f"- {summary}"]
    if next_goal:
        lines.append(f"- 下一章目标：{next_goal}")
    block = replacement + "\n".join(lines) + "\n"
    pattern = r"(?ms)^## 完成摘要\n.*$"
    if re.search(pattern, trace):
        trace = re.sub(pattern, block.rstrip(), trace, count=1)
    else:
        trace = trace.rstrip() + "\n\n" + block
    write_text(trace_path, trace)


def handle_finish_chapter(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    chapter_num = args.chapter_num
    chapter_title = args.chapter_title or "未命名章节"
    label = chapter_label(chapter_num)
    chapter_label_text = f"{label}-{chapter_title}"
    paths = runtime_paths(project_dir, chapter_num, chapter_title)
    manuscript_path = args.chapter_path
    if manuscript_path:
        manuscript = Path(manuscript_path).expanduser().resolve()
    else:
        manuscript = paths["manuscript"]

    missing_inputs: list[str] = []
    if not paths["intent"].exists():
        missing_inputs.append(f"缺少意图卡：{paths['intent']}")
    if not manuscript.exists():
        missing_inputs.append(f"缺少正文文件：{manuscript}")
    if missing_inputs:
        print("finish-chapter 失败：", file=sys.stderr)
        for item in missing_inputs:
            print(f"- {item}", file=sys.stderr)
        return 1

    intent_fields = parse_intent_card(paths["intent"])
    body = extract_story_body(read_text(manuscript))
    if not body.strip():
        print(
            f"finish-chapter 失败：正文为空，先完成 {manuscript.name} 再回写项目状态。",
            file=sys.stderr,
        )
        return 1

    word_count = count_story_units(body)
    task_log_path = project_dir / "task_log.md"
    task_log = read_text(task_log_path, render_task_log(project_dir.name))
    completed_nums = set(collect_completed_chapter_nums(project_dir))
    chapter_count, total_words = get_completed_stats(project_dir, {chapter_num: manuscript})
    existing_count = get_int_key_value(task_log, "累计完成章节：", 0)
    existing_words = get_int_key_value(task_log, "累计完成字数：", 0)
    if existing_count > len(completed_nums):
        chapter_count = existing_count if chapter_num in completed_nums else existing_count + 1
        total_words = existing_words if chapter_num in completed_nums else existing_words + word_count

    task_log = upsert_key_value(task_log, "创作阶段：", "章节已完成")
    task_log = upsert_key_value(task_log, "最新章节：", chapter_label_text)
    task_log = upsert_key_value(task_log, "当前处理章节：", "无")
    task_log = upsert_key_value(task_log, "累计完成章节：", str(chapter_count))
    task_log = upsert_key_value(task_log, "累计完成字数：", str(total_words))
    if args.next_goal:
        task_log = upsert_key_value(task_log, "下一章目标：", args.next_goal)
    task_log = upsert_recent_summary(task_log, chapter_label_text, args.summary)
    if args.plot_note:
        task_log = upsert_task_bullets(task_log, "活跃伏笔", f"- {args.plot_note}")
    write_text(task_log_path, task_log)

    update_focus_for_chapter(project_dir, "无", args.next_goal or "推进当前主线")
    update_chapter_plan_for_finish(
        project_dir,
        chapter_num,
        chapter_title,
        args.summary,
        args.goal or intent_fields["goal"] or "待人工补全",
        args.conflict or intent_fields["conflict"] or "待人工补全",
        args.payoff or intent_fields["payoff"] or "待人工补全",
        args.end_pressure or intent_fields["end_pressure"] or "待人工补全",
        chapter_count,
        total_words,
    )

    if args.foreshadow:
        row = parse_foreshadow_row(args.foreshadow)
        append_table_row(project_dir / "plot" / "伏笔记录.md", row)
    if args.timeline_event:
        timeline_row = [part.strip() for part in args.timeline_event.split("|")]
        while len(timeline_row) < 4:
            timeline_row.append("")
        append_table_row(project_dir / "plot" / "时间线.md", timeline_row[:4])

    update_trace_finish(paths["trace"], args.summary, args.next_goal or "")

    print(f"已完成: {chapter_label_text}")
    print(f"字数统计: {word_count}")
    print(f"正文文件: {manuscript}")
    return 0


def analyze_chapter(text: str) -> dict[str, list[dict[str, str]]]:
    findings: dict[str, list[dict[str, str]]] = {"P0": [], "P1": [], "P2": []}
    if "## 正文" in text:
        findings["P1"].append(
            {
                "location": "全文",
                "problem": "正文里泄露了模板标题 `## 正文`。",
                "impact": "会把过程壳子带进成稿，破坏沉浸。",
                "fix": "删除模板标题，只保留故事正文。",
            }
        )

    ai_hits = [pattern for pattern in AI_TELL_PATTERNS if pattern in text]
    if len(ai_hits) >= 2:
        findings["P1"].append(
            {
                "location": "全文",
                "problem": f"命中套语/解释腔：{', '.join(ai_hits)}。",
                "impact": "语言发虚，情绪停留在命名层，不落在动作和后果上。",
                "fix": "把抽象词拆成动作、停顿、环境反馈和具体代价。",
            }
        )
    elif ai_hits:
        findings["P2"].append(
            {
                "location": "全文",
                "problem": f"出现轻度套语：{', '.join(ai_hits)}。",
                "impact": "会抬高 AI 味。",
                "fix": "对命中句做局部去味。",
            }
        )

    ending_excerpt = excerpt_text(text[-120:], max_chars=120)
    if any(pattern in ending_excerpt for pattern in ENDING_SUMMARY_PATTERNS):
        findings["P1"].append(
            {
                "location": "结尾",
                "problem": "章末更像总结句，不是未决压力。",
                "impact": "追更驱动力偏弱。",
                "fix": "把结尾改成动作、发现、危险或未决选择。",
            }
        )

    if count_story_units(extract_story_body(text)) < 120:
        findings["P2"].append(
            {
                "location": "全文",
                "problem": "章节过短，像片段或壳子，不像完整正文。",
                "impact": "回报和压力难以成立。",
                "fix": "补齐核心事件、回报和章末造压。",
            }
        )
    return findings


def render_review_report(chapter_path: Path, findings: dict[str, list[dict[str, str]]]) -> str:
    lines = [f"# 审阅报告：{chapter_path.name}", ""]
    for level in ("P0", "P1", "P2"):
        lines.append(f"{level}：")
        items = findings[level]
        if not items:
            lines.append("- 未发现明显问题")
            lines.append("")
            continue
        for item in items:
            lines.extend(
                [
                    f"- 位置：{item['location']}",
                    f"- 问题：{item['problem']}",
                    f"- 影响：{item['impact']}",
                    f"- 修法：{item['fix']}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def handle_review(args: argparse.Namespace) -> int:
    chapter_path = Path(args.chapter_path).expanduser().resolve()
    project_dir = (
        Path(args.project_path).expanduser().resolve()
        if args.project_path
        else chapter_path.parent.parent
    )
    text = read_text(chapter_path)
    findings = analyze_chapter(text)
    report = render_review_report(chapter_path, findings)
    report_path = project_dir / "审阅意见" / f"{chapter_path.stem}-审阅.md"
    write_text(report_path, report)

    print(f"审阅完成: {report_path}")
    for level in ("P0", "P1", "P2"):
        print(f"{level}: {len(findings[level])}")
    return 0


def append_change_log(path: Path, scope: str, reason: str, impact: str) -> None:
    content = read_text(path)
    today = datetime.now().strftime("%Y-%m-%d")
    row = markdown_row([today, scope, reason, impact])
    if row in content:
        return
    write_text(path, content.rstrip() + "\n" + row + "\n")


def handle_governance(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    payload = {
        "current_volume": args.current_volume,
        "current_phase": args.current_phase,
        "phase_promise": args.phase_promise,
        "phase_main_problem": args.phase_main_problem,
        "phase_climax": args.phase_climax,
        "phase_payoff": args.phase_payoff,
        "new_risk": args.new_risk,
        "fulfilled": normalize_line_items(args.fulfilled),
        "pending": normalize_line_items(args.pending),
        "risks": normalize_line_items(args.risk),
        "next_actions": normalize_line_items(args.next_action),
    }
    write_text(project_dir / "docs" / "阶段规划.md", render_stage_plan(payload))

    if args.change_scope:
        append_change_log(
            project_dir / "docs" / "变更日志.md",
            args.change_scope,
            args.change_reason or "",
            args.change_impact or "",
        )

    task_log_path = project_dir / "task_log.md"
    task_log = read_text(task_log_path, render_task_log(project_dir.name))
    task_log = upsert_key_value(task_log, "当前卷：", args.current_volume or "未记录")
    task_log = upsert_key_value(task_log, "当前阶段：", args.current_phase or "未记录")
    task_log = upsert_key_value(task_log, "当前阶段目标：", args.phase_promise or "未记录")
    write_text(task_log_path, task_log)

    focus_path = project_dir / "docs" / "当前焦点.md"
    focus = read_text(focus_path)
    focus = upsert_key_value(focus, "当前卷：", args.current_volume or "未记录")
    focus = upsert_key_value(focus, "当前阶段：", args.current_phase or "未记录")
    focus = upsert_key_value(focus, "本轮目标：", args.phase_promise or "未记录")
    write_text(focus_path, focus)

    print(f"治理文件已更新: {project_dir}")
    return 0


def handle_resume(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_path).expanduser().resolve()
    state = read_project_state(project_dir)
    if args.json:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    print(f"项目目录: {state['project_dir']}")
    print(f"书名: {state['project_name']}")
    print(f"创作阶段: {state['stage']}")
    print(f"最新章节: {state['latest_chapter']}")
    print(f"当前处理章节: {state['current_chapter']}")
    print(f"当前卷/阶段: {state['current_volume']} / {state['current_phase']}")
    print(f"累计章节/字数: {state['chapter_count']} / {state['total_words']}")
    return 0


def handle_commands(_: argparse.Namespace) -> int:
    print("可用命令:")
    print("- init")
    print("- bootstrap")
    print("- resume")
    print("- next-chapter")
    print("- finish-chapter")
    print("- review")
    print("- governance")
    print("- commands")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="junli-novel-dfzr unified workflow CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="初始化小说项目目录")
    init_parser.add_argument("project_name", help="项目名")
    init_parser.add_argument("--target-dir", default=".", help="项目创建目录，默认当前目录")
    init_parser.add_argument("--mode", choices=tuple(MODE_LABELS), default="single", help="项目结构模式")
    init_parser.add_argument("--force", action="store_true", help="覆盖已有模板文件")
    init_parser.set_defaults(handler=handle_init)

    bootstrap_parser = subparsers.add_parser("bootstrap", help="把立项/设定/大纲材料落盘到 canonical 文件")
    bootstrap_parser.add_argument("project_path", help="项目根目录")
    bootstrap_parser.add_argument("--payload-file", required=True, help="bootstrap JSON 文件")
    bootstrap_parser.add_argument("--mode", choices=tuple(MODE_LABELS), default="single", help="项目模式")
    bootstrap_parser.set_defaults(handler=handle_bootstrap)

    resume_parser = subparsers.add_parser("resume", help="恢复项目当前状态")
    resume_parser.add_argument("project_path", help="项目根目录")
    resume_parser.add_argument("--json", action="store_true", help="输出 JSON")
    resume_parser.set_defaults(handler=handle_resume)

    next_parser = subparsers.add_parser("next-chapter", help="生成下一章过程文件和正文壳子")
    next_parser.add_argument("project_path", help="项目根目录")
    next_parser.add_argument("--chapter-num", type=int, help="章节号；不传则自动取下一章")
    next_parser.add_argument("--chapter-title", default="未命名章节", help="章节标题")
    next_parser.add_argument("--pov", help="本章主 POV")
    next_parser.add_argument("--info-boundary", help="信息边界")
    next_parser.add_argument("--hidden-info", help="隐藏信息")
    next_parser.add_argument("--goal", help="本章目标")
    next_parser.add_argument("--conflict", help="核心冲突")
    next_parser.add_argument("--payoff", help="回报类型")
    next_parser.add_argument("--end-pressure", help="章末压力")
    next_parser.add_argument("--force", action="store_true", help="覆盖已有章节文件")
    next_parser.set_defaults(handler=handle_next_chapter)

    finish_parser = subparsers.add_parser("finish-chapter", help="章节完成后回写 task_log / 章节规划 / 伏笔 / 时间线")
    finish_parser.add_argument("project_path", help="项目根目录")
    finish_parser.add_argument("--chapter-num", type=int, required=True, help="章节号")
    finish_parser.add_argument("--chapter-title", default="未命名章节", help="章节标题")
    finish_parser.add_argument("--chapter-path", help="章节文件路径；不传则按默认命名推断")
    finish_parser.add_argument("--summary", required=True, help="本章摘要")
    finish_parser.add_argument("--next-goal", help="下一章目标")
    finish_parser.add_argument("--plot-note", help="活跃伏笔备注")
    finish_parser.add_argument("--foreshadow", help="伏笔记录，格式：伏笔|首次出现|计划回收|状态|备注")
    finish_parser.add_argument("--timeline-event", help="时间线记录，格式：时间点|事件|涉及角色|影响")
    finish_parser.add_argument("--goal", help="本章目标，用于回写章节规划")
    finish_parser.add_argument("--conflict", help="核心冲突，用于回写章节规划")
    finish_parser.add_argument("--payoff", help="回报，用于回写章节规划")
    finish_parser.add_argument("--end-pressure", help="章末压力，用于回写章节规划")
    finish_parser.set_defaults(handler=handle_finish_chapter)

    review_parser = subparsers.add_parser("review", help="生成章节审阅报告")
    review_parser.add_argument("chapter_path", help="章节文件路径")
    review_parser.add_argument("--project-path", help="项目目录；不传则从章节路径推断")
    review_parser.set_defaults(handler=handle_review)

    governance_parser = subparsers.add_parser("governance", help="更新阶段规划与变更日志")
    governance_parser.add_argument("project_path", help="项目根目录")
    governance_parser.add_argument("--current-volume", required=True, help="当前卷")
    governance_parser.add_argument("--current-phase", required=True, help="当前阶段")
    governance_parser.add_argument("--phase-promise", required=True, help="阶段承诺")
    governance_parser.add_argument("--phase-main-problem", required=True, help="阶段主问题")
    governance_parser.add_argument("--phase-climax", required=True, help="阶段高潮")
    governance_parser.add_argument("--phase-payoff", required=True, help="阶段回报")
    governance_parser.add_argument("--new-risk", required=True, help="新增风险")
    governance_parser.add_argument("--fulfilled", action="append", help="已兑现承诺")
    governance_parser.add_argument("--pending", action="append", help="未兑现承诺")
    governance_parser.add_argument("--risk", action="append", help="活跃风险")
    governance_parser.add_argument("--next-action", action="append", help="下一阶段动作")
    governance_parser.add_argument("--change-scope", help="变更范围")
    governance_parser.add_argument("--change-reason", help="改动原因")
    governance_parser.add_argument("--change-impact", help="连带影响")
    governance_parser.set_defaults(handler=handle_governance)

    commands_parser = subparsers.add_parser("commands", help="查看命令列表")
    commands_parser.set_defaults(handler=handle_commands)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

# 君黎网文道法术器

以“道法术器”为骨架的 AI 小说与网文创作技能。

这个技能把顶层创作哲学、叙事规则、执行工作流和交付产物拆成四层，用来处理：

- 脑洞立项
- 书名策略
- 世界观设定
- 人物卡设计
- 主线梗概与分卷规划
- 章节细纲与下一章续写
- 单章扩写、重写、润色
- 去 AI 味返修
- 长篇治理与阶段审计
- 营销包装

## 核心思路

### 道

先确定这本书为什么值得写，读者究竟在追什么，AI 在这次任务里扮演什么角色。

### 法

再确定题材承诺、平台约束、POV 边界、人物一致性、原创边界和质量门。

### 术

按任务类型选择工作流：立项、章节执行、返修评审、长篇治理。

### 器

最后只交付当前真正需要的产物，例如故事圣经、人物卡、卷纲、章节意图卡、场景推进卡、审稿报告或营销 Brief。
默认会把这些产物写进项目目录，并把章节过程文件和正文分开保存。

## 仓库结构

```text
.
├── SKILL.md
├── scripts/
│   ├── novel_pipeline.py
│   └── project_scaffold.py
├── tests/
│   ├── test_novel_pipeline.py
│   └── test_project_scaffold.py
└── references/
    ├── dao-fa-shu-qi-map.md
    ├── project-bootstrapping.md
    ├── project-file-layout.md
    ├── chapter-execution.md
    ├── revision-and-review.md
    ├── longform-governance.md
    ├── quality-gates.md
    └── output-templates.md
```

## 适用场景

当用户说下面这些话时，这个技能应该能接住：

- “帮我写小说”
- “给我搭一个世界观”
- “做人设和主线”
- “给这本书出大纲和分卷”
- “续写下一章”
- “扩写这一章”
- “帮我重写这段，降低 AI 味”
- “检查这一章的爽点、毒点和章末钩子”
- “帮我做长篇控盘”

## 技能特点

- 用“道法术器”统一创作方向、规则和执行
- 强调题材承诺、冲突链、人物边界、代价系统
- 支持从立项到长篇治理的完整链路
- 内置章节质量门、返修分级和最小输出模板
- 默认落盘到项目目录，保留章节过程文件和正文文件
- 内置统一 CLI：立项落盘、章节起停、轻量规则审阅、治理都能走命令闭环
- 避免把设定写成百科，把正文写成模板

## 使用方式

把本仓库作为技能目录加载，核心入口是 [`SKILL.md`](./SKILL.md)。

工作时按需读取 `references/` 下对应文件，不需要一次全部载入。

推荐加载顺序：

1. `SKILL.md`
2. 按任务类型选择一个主 workflow
3. 需要长期保存时补 `references/project-file-layout.md`
4. 只补充当前任务需要的其他 reference

初始化项目或章节过程文件时，可直接用：

```bash
python3 scripts/novel_pipeline.py init "项目名" --target-dir ./novels
python3 scripts/novel_pipeline.py next-chapter ./novels/项目名 --chapter-title "标题"
```

立项 / 世界观 / 人设 / 大纲落盘走 `bootstrap`，输入 JSON 至少包含这些 key：

```json
{
  "story_bible": {},
  "worldview": {},
  "rules": {},
  "author_intent": {},
  "current_focus": {},
  "chapter_plan": [],
  "characters": []
}
```

常用命令：

```bash
python3 scripts/novel_pipeline.py commands
python3 scripts/novel_pipeline.py bootstrap ./novels/项目名 --payload-file ./bootstrap.json
python3 scripts/novel_pipeline.py finish-chapter ./novels/项目名 --chapter-num 1 --chapter-title "标题" --summary "本章摘要"
python3 scripts/novel_pipeline.py review ./novels/项目名/manuscript/第0001章-标题.md --project-path ./novels/项目名
python3 scripts/novel_pipeline.py governance ./novels/项目名 --current-volume "第一卷" --current-phase "阶段1" --phase-promise "阶段承诺" --phase-main-problem "阶段主问题" --phase-climax "阶段高潮" --phase-payoff "阶段回报" --new-risk "新增风险"
```

补充说明：

- `finish-chapter` 现在会校验意图卡和非空正文；如果还只是壳子，不会回写 `task_log.md` 或章节状态。
- `review` 当前定位是轻量规则预检，只检查模板残留、成串 AI 套语、结尾总结腔和“像壳子”的短章。爽点 / 毒点 / POV / 世界规则 / 逻辑硬伤仍按 `SKILL.md` 与 `references/revision-and-review.md` 的完整工作流由模型或人工深审。

`scripts/project_scaffold.py` 仍保留 `init / prepare-chapter` 兼容入口，方便旧调用继续工作。

## 设计来源

本技能以“道法术器”创作体系为方法论骨架，并结合 `junli-ai-novel` 项目的网文工作流思路重构而成，目标不是简单复刻旧项目，而是抽出一套更适合通用技能分发的结构。

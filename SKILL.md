---
name: junli-novel-dfzr
description: 以“道法术器”为骨架的 AI 小说与网文创作技能。处理脑洞立项、书名策略、世界观设定、人物卡、主线梗概、分卷大纲、章节细纲、续写下一章、单章扩写、重写润色、降 AI 味、冲突钩子优化、长篇治理、营销包装。用户说“帮我写小说”“搭世界观”“做人设”“写大纲”“出细纲”“续写下一章”“扩写这章”“重写这章”“给这段降 AI 味”“检查爽点毒点”“规划分卷”“做连载方案”时使用。
---

# 君黎网文道法术器

IRON LAW: 先立道与法，再选术与器；在题材承诺、冲突链、人物边界、世界规则未锁定前，禁止直接开写大纲或正文。

Red Flags（命中任一项，回到 Step 1）：
- 设定越来越多，却回答不了“谁想要什么、谁在阻止、失败代价是什么”
- 正准备整章推倒重写，但实际问题只落在开头、对白、结尾或单场景
- 正文开始出现解释腔、总结腔、AI 套语，说明法栈没有压住写法

## Workflow

Copy this checklist and check off items as you complete them:

```text
Junli Novel DFZR Progress:

- [ ] Step 1: 锁定任务层级与道法术器栈 ⚠️ REQUIRED
  - [ ] 1.1 判断任务类型：立项 / 设定 / 大纲 / 章节 / 返修 / 治理 / 营销
  - [ ] 1.2 判断创作模式：导演 / 协同 / 启发 / 演化
  - [ ] 1.3 写出本道、法栈、术路、器单
- [ ] Step 2: 组装最小输入包 ⚠️ REQUIRED
  - [ ] 2.1 新项目：补齐 5 个阻塞信息
  - [ ] 2.2 旧项目：按顺序恢复记忆
  - [ ] 2.3 明确这轮允许修改的范围
  - [ ] 2.4 锁定项目目录、文件落点与过程文件
- [ ] Step 3: 选择工作流并加载 reference ⚠️ REQUIRED
- [ ] Step 4: 生成目标产物
- [ ] Step 5: 过质量门并交付
```

## Step 1: 锁定任务层级与道法术器栈 ⚠️ REQUIRED

Ask：
- 这次真正要交付的是脑洞包、故事圣经、卷纲、章节、返修稿、治理备忘录还是营销稿？
- 读者这轮最该追的是什么：爽点、悬念、权谋、情绪、关系还是成长？
- 人类作者这次更像导演、合作者、灵感挑选者，还是反馈驱动的迭代者？

先写 4 行工作底稿：
- 道：主题命题、读者承诺、人机分工
- 法：伦理边界、题材规则、平台约束、POV/风格/长度限制
- 术：本次采用的流程
- 器：这轮要交付的产物

只在这些信息足以支撑当前任务时继续。缺的是阻塞条件时，只问最少问题，不做大问卷。

需要完整映射或模式矩阵时，加载 `references/dao-fa-shu-qi-map.md`。

## Step 2: 组装最小输入包 ⚠️ REQUIRED

新项目至少锁定这 5 项：
- 题材与调性
- 主角结构与核心缺口
- 核心冲突与失败代价
- 平台或目标读者
- 目标体量或章节密度

旧项目 / 续写 / 返修按这个顺序恢复上下文：
1. 用户本轮目标
2. 既有总纲 / 卷纲 / 阶段规划
3. 章节规划 / 伏笔 / 时间线
4. 相关角色与世界规则
5. 目标章节及相邻章节

如果用户只让你修局部，不要擅自放大成全章重写或世界观重构。

默认落盘规则：
- 默认把产物写入项目目录，不只在聊天里交付一版文本。
- 只有用户明确要求“先别写文件”“只给聊天稿”“我先看草案”时，才暂时不落盘。
- 新项目先锁定项目名和项目目录；用户没给路径时，默认在当前工作目录下创建 `novels/<项目名>/`。如果连项目名都没有，先问项目名。
- 需要初始化目录时，优先运行 `python3 scripts/novel_pipeline.py init "<项目名>" --target-dir <父目录>`；兼容旧入口时可用 `python3 scripts/project_scaffold.py init "<项目名>" --target-dir <父目录>`。
- 立项 / 世界观 / 人设 / 章节规划落盘时，优先运行 `python3 scripts/novel_pipeline.py bootstrap <项目目录> --payload-file <json文件>`，把 canonical 文档写进 `docs/`、`characters/`。
- 章节任务写前，优先运行 `python3 scripts/novel_pipeline.py next-chapter <项目目录> --chapter-title "标题"`；兼容旧入口时可用 `python3 scripts/project_scaffold.py prepare-chapter <项目目录> --chapter-num <章节号> --chapter-title "标题"`。`next-chapter` 默认同时生成意图卡、场景卡、追踪文件、context、rule-stack 和正文壳子。
- 正文完成后，运行 `python3 scripts/novel_pipeline.py finish-chapter <项目目录> --chapter-num <章节号> --chapter-title "标题" --summary "本章摘要"`，把摘要、章节规划、伏笔、时间线、task_log 回写闭环。`finish-chapter` 只接受“意图卡已存在 + 正文非空”的章节，空壳不会被标成已完成。
- 审阅与治理分别走 `python3 scripts/novel_pipeline.py review ...` 和 `python3 scripts/novel_pipeline.py governance ...`。其中 `review` 目前只做轻量规则预检，不替代完整审稿。

按需加载：
- `references/project-bootstrapping.md`
- `references/chapter-execution.md`
- `references/revision-and-review.md`
- `references/longform-governance.md`
- `references/project-file-layout.md`

## Step 3: 选择工作流并加载 reference ⚠️ REQUIRED

匹配一个主工作流，不要几条同时乱跑：
- 立项 / 世界观 / 人物 / 大纲：加载 `references/project-bootstrapping.md` 和 `references/output-templates.md`
- 章节续写 / 场景卡 / 细纲：加载 `references/chapter-execution.md` 和 `references/quality-gates.md`
- 评审 / 改稿 / 去 AI 味：加载 `references/revision-and-review.md` 和 `references/quality-gates.md`。如果只是跑 CLI `review`，把它当模板残留 / 套语 / 结尾总结腔 / 短章壳子的预检，不要当完整审稿结论。
- 长篇治理 / 分卷 / 结构变更：加载 `references/longform-governance.md` 和 `references/output-templates.md`
- 营销包装：加载 `references/output-templates.md` 和 `references/quality-gates.md`

只要这轮产物要长期保存、后续续写、跨轮复用或多人协同，额外加载 `references/project-file-layout.md`。

确认门：
- 如果要写 3000 字以上正文、重写用户已有章节、或改变全书级设定，先给 5-10 行执行方案或变更摘要。
- 只有在用户明确要求“直接写”“直接改”时，才跳过这个确认门。

## Step 4: 生成目标产物

按产物类型执行，不把模板说明写进最终内容：
- 立项：先给一句话卖点，再给主线发动机、人物缺口、世界冲突、阶段锚点
- 设定：设定必须直接长出冲突、代价、剧情使用面，不做百科清单
- 大纲：用“终点站 -> 起爆事件 -> 连锁反应 -> 分卷锚点”推进
- 章节：先定 POV、信息边界、场景推进链，再写正文
- 返修：先判轻修 / 中修 / 重修，优先定向修，不默认整章推翻
- 评审：完整审稿先给 P0 / P1 / P2 问题，再给证据和修法；如果只是调用 CLI `review`，默认只产出轻量规则报告
- 治理：输出当前阶段、未兑现承诺、风险点、下一阶段动作

默认文件映射：
- 故事圣经 / 主线梗概 / 立项摘要 -> `docs/项目总纲.md`
- 世界观 / 设定铁律 -> `docs/世界观.md`、`docs/法则.md`
- 人物卡 -> `characters/<角色名>.md`
- 章节规划 / 分卷规划 -> `docs/章节规划.md`、`docs/卷纲.md`
- 治理 / 结构变更 -> `docs/阶段规划.md`、`docs/变更日志.md`
- 章节意图 / 场景拆分 -> `runtime/chapter-XXXX.intent.md`、`runtime/chapter-XXXX.scenes.md`
- 过程记录 -> `runtime/chapter-XXXX.trace.md`
- 运行时上下文 -> `runtime/chapter-XXXX.context.json`、`runtime/chapter-XXXX.rule-stack.yaml`
- 正文 -> `manuscript/第XXXX章-标题.md`
- 评审 / 返修报告 -> `审阅意见/`
- 营销包装 -> `marketing/`

先写文件，再在聊天里给摘要和路径。除非用户明确要求只看聊天稿，不要把大纲、世界观、过程文件、正文混在一条纯聊天回复里就算完成。

## Step 5: 过质量门并交付

交付前加载 `references/quality-gates.md`。

最低检查项：
- 输出类型与用户要求一致
- 道与法在产物里被兑现，不只是说明文字
- 情节 / 人物 / 世界 / 情感四维至少有一处清晰推进
- 没有成串 AI 套语、解释腔、总结腔
- 如果是章节：前 20% 有钩子，中段有回报，章末有未决压力
- 如果是设定或大纲：能看出冲突来源、推进链和代价系统
- 如果是返修：没有越权改动无关部分
- 该落盘的产物已经写入正确目录
- 正文与过程文件已经分离
- 如果走 CLI，`task_log.md`、`docs/当前焦点.md`、`docs/章节规划.md` 已完成同步

## Anti-Patterns

- 把“道”写成空泛哲学，不落到故事决策
- 把“法”写成百科式禁令堆，不能指导当前任务
- 把“术”写成流水账模板，甚至把 Beat 编号直接抄进正文
- 把“器”做成一堆无用产物，不管用户这次真正需要什么
- 以整章重写逃避局部修复
- 为了去 AI 味把信息、爽点、钩子一起洗掉
- 只在聊天里给大纲、世界观、正文，不同步项目文件
- 把正文、意图卡、场景卡和追踪记录塞进同一个文件
- 只写结果，不留后续续写可复用的过程文件

## Pre-Delivery Checklist

- [ ] 已写出本道、法栈、术路、器单
- [ ] 只加载了当前任务真正需要的 reference
- [ ] 产物能回答“谁想要什么、被什么阻止、失败代价是什么”
- [ ] 没有把设定写成与冲突脱节的清单
- [ ] 没有把章节结尾写成感悟或总结
- [ ] 没有把局部返修扩大成整章推翻
- [ ] 该落盘的内容已写入约定目录
- [ ] 章节任务已同步过程文件和正文文件

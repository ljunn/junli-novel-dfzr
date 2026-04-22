# 项目文件布局与落盘协议

只要任务结果要被后续续写、返修、审计或多人协同复用，就必须落盘。不要只在聊天窗口里交付。

## 一、默认模式

- 默认模式：写文件 + 聊天摘要
- 例外模式：用户明确说“先别写文件”“只聊天”“我先看草稿”
- 新项目如果没有目录但已有项目名，默认在当前工作目录下创建 `novels/<项目名>/`
- 没有项目名时，先问项目名，再建目录

可用脚手架：

```bash
python3 scripts/novel_pipeline.py init "<项目名>" --target-dir <父目录>
python3 scripts/novel_pipeline.py bootstrap <项目目录> --payload-file <json文件>
python3 scripts/novel_pipeline.py next-chapter <项目目录> --chapter-title "标题"
python3 scripts/novel_pipeline.py finish-chapter <项目目录> --chapter-num <章节号> --chapter-title "标题" --summary "本章摘要"
```

兼容旧入口：

```bash
python3 scripts/project_scaffold.py init "<项目名>" --target-dir <父目录>
python3 scripts/project_scaffold.py prepare-chapter <项目目录> --chapter-num <章节号> --chapter-title "标题"
```

## 二、标准目录

```text
[项目目录]/
├── docs/
│   ├── 项目总纲.md
│   ├── 章节规划.md
│   ├── 卷纲.md
│   ├── 阶段规划.md
│   ├── 变更日志.md
│   ├── 世界观.md
│   ├── 法则.md
│   ├── 作者意图.md
│   └── 当前焦点.md
├── characters/
├── manuscript/
├── plot/
│   ├── 伏笔记录.md
│   └── 时间线.md
├── runtime/
├── 审阅意见/
├── marketing/
└── task_log.md
```

## 三、产物落点

- 脑洞包 / 故事圣经 / 主线梗概：`docs/项目总纲.md`
- 世界规则 / 社会规则 / 系统代价：`docs/世界观.md`、`docs/法则.md`
- 人物卡：`characters/<角色名>.md`
- 前 3-10 章规划 / 节奏表：`docs/章节规划.md`
- 分卷 / 阶段治理：`docs/卷纲.md`、`docs/阶段规划.md`
- 结构性改动：`docs/变更日志.md`
- 章节意图卡：`runtime/chapter-XXXX.intent.md`
- 场景推进卡：`runtime/chapter-XXXX.scenes.md`
- 过程追踪：`runtime/chapter-XXXX.trace.md`
- 运行时上下文：`runtime/chapter-XXXX.context.json`
- 章节规则栈：`runtime/chapter-XXXX.rule-stack.yaml`
- 正文：`manuscript/第XXXX章-标题.md`
- 审阅稿 / 返修报告：`审阅意见/`
- 营销 Brief / 书名策略：`marketing/`

## 四、过程文件最低要求

章节任务至少保留 3 份过程文件：

1. `intent.md`
   - 本章主 POV
   - 信息边界
   - 隐藏信息
   - 本章目标
   - 核心冲突
   - 回报类型
   - 章末压力
2. `scenes.md`
   - 3-5 个场景卡
   - 每个场景都要有状态变化、行动目的、明面阻力、暗线、副功能
3. `trace.md`
   - 道 / 法 / 术 / 器
   - 输入来源
   - 关键决策
   - 本轮产出文件

如果走 `scripts/novel_pipeline.py next-chapter`，默认还会额外生成：

4. `context.json`
   - 当前卷 / 阶段 / 阶段目标
   - 本章目标、冲突、回报、章末压力
   - 本章 POV 与项目摘要摘录
5. `rule-stack.yaml`
   - 章节级道 / 法 / 术 / 器约束
   - 本章 workflow 与输出清单

过程文件是为了下一轮续写、返修和审计，不是给读者看的正文。

## 五、更新纪律

- 直接更新 canonical 文件，不要堆 `世界观-最终版.md`、`大纲-v2-真的最终.md`
- 正文文件只放故事正文，不放模板字段、Beat 编号、工作说明
- 过程文件可以保留模板字段和工作痕迹
- 用户只授权局部返修时，只改目标正文和必要过程文件，不顺手重做世界观
- 交付时先写文件，再在聊天里说明写了哪些路径、哪些还没写、下一步建议是什么

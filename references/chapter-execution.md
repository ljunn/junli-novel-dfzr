# 章节执行工作流

用于续写下一章、生成章节细纲、做场景推进卡或直接写正文。

## 一、写前恢复顺序

章节任务默认先恢复这些内容：
1. 用户本轮目标
2. 项目总纲 / 卷纲 / 阶段规划
3. 章节规划 / 伏笔 / 时间线
4. 相关人物与世界规则
5. 上一章正文
6. 当前章目标

如果缺关键文件，要明确报告阻塞，不要假装已经恢复上下文。

如果项目走 CLI，建议顺序：

```bash
python3 scripts/novel_pipeline.py resume <项目目录>
python3 scripts/novel_pipeline.py next-chapter <项目目录> --chapter-title "标题"
```

`next-chapter` 会默认生成：
- `runtime/chapter-XXXX.intent.md`
- `runtime/chapter-XXXX.scenes.md`
- `runtime/chapter-XXXX.trace.md`
- `runtime/chapter-XXXX.context.json`
- `runtime/chapter-XXXX.rule-stack.yaml`
- `manuscript/第XXXX章-标题.md`

## 二、先产出章节意图卡

正文前至少锁定：
- 本章主 POV
- 当前 POV 能看到、知道、误判到什么
- 本章准备暂时隐藏什么
- 本章目标
- 本章核心冲突
- 本章回报类型
- 本章章末压力

如果上面 7 项写不出来，先别进正文。

## 三、先拆 3-5 个场景

每个场景至少写清：
- 场景类型：铺垫 / 冲突 / 高潮 / 转折 / 收尾
- 状态变化：从 A 到 B
- 行动目的：谁想拿到、守住、证明、隐瞒或逃离什么
- 明面阻力：谁或什么直接拦着
- 暗线：伏笔、误导、利益或关系潜流
- 副功能：顺手承载哪 1-2 项，如人设、关系、信息、世界规则

场景不是事件目录。没有行动目的和状态变化的场景，大概率是流水段。

## 四、正文硬规则

- 前 20% 必须有即时冲突、异常信息、强认知钩子或高吸引力动作
- 每章至少推进一条主线或重要支线
- 每章至少回应一个旧悬念
- 每章至少设置一个新钩子或升级现有钩子
- 每章至少有一次实感回报：翻盘、揭示、关系推进、资源落袋四选一
- 主角受挫后，要给补偿基础、信息收益或关系回应

正文默认只输出故事内容，不写模板标题、字段说明、分隔线。

## 五、语言与 POV 护栏

- 贴紧本章主 POV，不在同一段里钻两个人脑内
- 情绪优先落在动作、环境、停顿和后果里，不直接命名大词
- 对话服务冲突、试探、遮掩或暴露性格，不做说明书
- 高压场景可以短句提速，但因果和情绪必须连着
- 章节结尾停在动作、发现、危险或未决选择上，不停在总结

## 六、章节完成前复查

- 去掉本章后，主线、人物或关系是否明显受损
- 本章有没有逼出选择、代价或误判，而不是只发生一件事
- 章末是否仍有前台未决压力，能拉动下一章

正文完成后，如果走 CLI，记得执行：

```bash
python3 scripts/novel_pipeline.py finish-chapter <项目目录> --chapter-num <章节号> --chapter-title "标题" --summary "本章摘要"
```

它会回写：
- `task_log.md`
- `docs/当前焦点.md`
- `docs/章节规划.md`
- `plot/伏笔记录.md`（传入 `--foreshadow` 时）
- `plot/时间线.md`（传入 `--timeline-event` 时）
- `runtime/chapter-XXXX.trace.md`

详细质量门见 `references/quality-gates.md`。

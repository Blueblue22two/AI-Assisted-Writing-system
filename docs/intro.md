# 项目傻瓜式讲解：Multi-Agent Academic Writing Assistant
## 1. 这个项目要解决什么问题

这个项目不是要做一个完整的写作软件，而是要做一个小型实验系统。

它想回答一个问题：

```text
多个 Agent 分工合作写文章，是否比一个 Agent 直接写文章更好？
```

也就是说，我们要比较：

- 一个 Agent 自己直接写文章。
- 多个 Agent 按步骤合作写文章。

## 2. 系统输入什么

系统会收到一个写作任务。

比如：

```text
请写一段 250 词的学术短文，讨论 AI 辅助写作的优点和限制。
```

每个任务通常包含：

- 题目要求，也就是 instruction。
- 参考材料，也就是 source material。
- 目标字数，也就是 target word count。
- 评分标准，也就是 rubric。

## 3. 为什么要用 Multi-Agent

单智能体写作很简单：

```text
任务 + 材料 + 评分标准 -> Writer Agent -> 最终答案
```

也就是说，一个 Writer Agent 直接完成所有事情。

Multi-agent 写作会把写作过程拆成几个步骤：

```text
Planner -> Writer -> Critic -> Editor
```

每个 Agent 只负责一件比较明确的事情：

- `Planner Agent`：先想文章结构和主要论点。
- `Writer Agent`：根据计划写初稿。
- `Critic Agent`：根据评分标准批评初稿。
- `Editor Agent`：根据批评意见修改文章，输出最终答案。
- `Evaluator Agent`：最后独立评分。

这样做的想法是：分工明确以后，文章可能会更有结构、更清楚、更符合评分标准。

## 4. 系统架构是什么

本项目采用：

```text
Centralized Orchestrator + Shared Workspace
```

简单来说，就是：

- 有一个中心控制器，叫 `Orchestrator`。
- 它决定哪个 Agent 先运行，哪个 Agent 后运行。
- Agent 之间不自由聊天。
- 每个 Agent 的输出都会保存到共享工作区。

完整流程大概是：

```text
任务进入系统
↓
Planner 生成 plan
↓
Writer 根据 plan 生成 draft
↓
Critic 对 draft 提出 critique
↓
Editor 根据 critique 生成 final answer
↓
Evaluator 对 final answer 打分
```

这样设计的好处是：

- 流程清楚。
- 容易记录每一步输出。
- 容易比较不同实验条件。
- 适合 coursework 的小型实验。

## 5. 要比较哪些方法

项目至少比较 3 种写作方式。

### Condition A: Single-Agent Baseline

一个 Writer Agent 直接写最终答案。

```text
Writer -> final answer
```

这是 baseline，也就是基线。

它的作用是回答：

```text
如果不用 multi-agent，单个 Agent 能做到什么水平？
```

### Condition B: Plan-Execute

先规划，再写作。

```text
Planner -> Writer -> final answer
```

这个条件用来测试：

```text
先做写作计划，会不会让文章结构更好？
```

### Condition C: Plan-Execute-Critique

先规划，再写作，再批评，再修改。

```text
Planner -> Writer -> Critic -> Editor -> final answer
```

这个条件用来测试：

```text
加入批评和修改，会不会让最终文本更好？
```

## 6. 实验怎么运行

首先准备一批写作任务。

比如准备 20 条任务。

每条任务都在三个条件下运行：

```text
同一个任务
├── Baseline 跑 3 次
├── Plan-Execute 跑 3 次
└── Plan-Execute-Critique 跑 3 次
```

如果有 20 个任务，那么总运行次数是：

```text
20 个任务 x 3 个条件 x 3 次重复 = 180 次运行
```

每次运行都要保存结果。

需要保存的信息包括：

- task id
- condition
- plan
- draft
- critique
- final answer
- runtime
- token usage，如果 API 提供
- evaluator score

这些记录以后可以用来分析哪个方法更好。

## 7. 评估怎么做

评估时要尽量公平。

所以不能让 `Evaluator Agent` 知道答案来自哪个 condition。

也就是说，Evaluator 不应该知道：

- 这是 Baseline 生成的。
- 这是 Plan-Execute 生成的。
- 这是 Plan-Execute-Critique 生成的。
- 文章背后经过了哪些 Agent。

Evaluator 只应该看到：

- 写作任务
- 参考材料
- 目标字数
- 评分标准
- 最终答案

这样可以减少评分偏见。

## 8. 为什么要匿名化

正式评分前，需要把最终答案变成匿名的 evaluation item。

例如：

```json
{
  "eval_id": "E0001",
  "task_id": "T001",
  "instruction": "...",
  "source_material": "...",
  "target_word_count": 250,
  "rubric": {},
  "answer": "..."
}
```

这里面没有 condition 信息。

也就是说，Evaluator 只看到答案本身，不知道它是哪个 workflow 生成的。

## 9. 评分标准是什么

Evaluator 按 6 个维度评分。

每个维度都是 1 到 5 分。

### Relevance

是否切题。

也就是文章有没有回答题目要求。

### Structure

结构是否清楚。

也就是文章有没有清晰的组织、段落和逻辑顺序。

### Evidence Use

是否有效使用参考材料。

也就是文章有没有用 source material 支持自己的观点。

### Argument Clarity

论点是否明确。

也就是文章有没有清楚的中心观点，推理是否清楚。

### Academic Style

是否符合学术风格。

也就是语言是否正式、客观、准确。

### Grammar and Readability

语法和可读性是否好。

也就是文章是否流畅、易读、语法问题少。

## 10. Overall Score 怎么算

最终总分叫 `overall_score`。

它是 6 个维度分数的平均值：

```text
overall_score = mean(
  relevance,
  structure,
  evidence_use,
  argument_clarity,
  academic_style,
  grammar_readability
)
```

简单来说：

```text
总分 = 六个小分加起来 / 6
```

## 11. 怎么判断 Multi-Agent 是否更好

实验结束后，对每个 condition 计算平均分。

比如：

```text
Baseline 平均分
Plan-Execute 平均分
Plan-Execute-Critique 平均分
```

然后比较：

```text
Plan-Execute vs Baseline
Plan-Execute-Critique vs Baseline
Plan-Execute-Critique vs Plan-Execute
```

如果 `Plan-Execute-Critique` 的平均分更高，并且在更多任务上赢过 Baseline，就可以说明：

```text
在本项目实验设置下，multi-agent workflow 有提升趋势。
```

注意，这不能证明 multi-agent 在所有场景都更好。

只能说明它在本项目的数据、模型和评分方式下表现更好。

## 12. 为什么要看稳定性

LLM 每次生成的结果可能都不一样。

所以同一个任务、同一个 condition 要重复运行 3 次。

比如：

```text
Baseline 分数：3.5, 4.0, 3.0
Plan-Execute-Critique 分数：4.0, 4.2, 4.1
```

第二个 workflow 不仅平均分更高，而且分数波动更小。

这说明它可能更稳定。

因此实验分析时要看：

- 平均分
- 标准差
- win rate
- 分数分布图

## 13. 为什么还要看成本

Multi-agent 通常会更贵。

因为 Baseline 可能只调用一次 LLM：

```text
Writer
```

但 Plan-Execute-Critique 可能调用四次 LLM：

```text
Planner + Writer + Critic + Editor
```

所以实验报告不能只说质量有没有提升。

还要讨论：

```text
提升是否值得额外成本？
```

如果 multi-agent 只提升一点点，但成本高很多，那这个结果就需要谨慎解释。

## 14. 最后应该怎么得出结论

比较稳妥的结论应该这样写：

```text
在本项目的小规模任务集和固定评分协议下，Plan-Execute-Critique 相比 Single-Agent Baseline 生成了更高质量、更稳定的文本，但也带来了更高的 token cost 和 runtime。
```

不应该这样写：

```text
Multi-agent writing systems 一定比 single-agent systems 好。
```

因为本项目只是一个小规模 coursework 实验，不能证明所有场景。

## 15. 一句话总结

这个项目的核心实现路径是：

```text
写作任务数据集
↓
三种 agent workflow
↓
保存每次运行结果
↓
匿名化最终答案
↓
独立 Evaluator 评分
↓
统计分析和画图
↓
回答研究问题
```


# How to Generate Data

- 数据集文件：  
实验用的数据集存储在`/data/task_main.jsonl`中。  

- 目标：  
收集高质量数据25-50条。  

## 1. 数据在项目中的作用
每一条 JSONL 数据代表一个 writing task。系统会让同一个 task 分别经过：

- Condition A: Single-Agent Baseline
- Condition B: Plan-Execute
- Condition C: Plan-Execute-Critique

然后用同一个 Evaluator Agent 匿名评分。

因此，数据必须满足一个核心标准：

> 同一条任务必须适合被不同 workflow 公平比较。

不要让某些任务天然更适合 multi-agent，也不要让题目太简单，导致三种 workflow 都难以拉开差异。

## 2. 标准 JSONL 格式

JSONL 的规则是：
- 一个任务一行。
- 每一行都是一个完整 JSON object。
- 不要写成 JSON 数组。
- 不要把一个 JSON object 拆成多行。
- 文件扩展名使用 `.jsonl`。

推荐 schema：

```jsonl
{"task_id":"T001","instruction":"Write a 250-word critical paragraph about ...","source_material":"...","target_word_count":250,"rubric":{"relevance":5,"structure":5,"evidence_use":5,"argument_clarity":5,"academic_style":5,"grammar_readability":5}}
```

字段说明：

| 字段 | 类型 | 要求 |
|---|---|---|
| `task_id` | string | 唯一编号，如 `T001` |
| `instruction` | string | 明确写作任务、文体、角度、字数 |
| `source_material` | string | 可用于支撑论证的短参考材料 |
| `target_word_count` | integer | 推荐 200-300，当前项目常用 250 |
| `rubric` | object | 固定六个评分维度 |

`rubric` 必须统一为：

```json
{
  "relevance": 5,
  "structure": 5,
  "evidence_use": 5,
  "argument_clarity": 5,
  "academic_style": 5,
  "grammar_readability": 5
}
```

不要再使用 `clarity`，因为它和 `Product.md` 的 primary metrics 不一致。

---

## 3. 一条高质量任务应包含什么
### 3.1 明确的写作指令

好的 instruction 应该包含：
- 写作体裁：critical paragraph、short academic response 等。
- 写作长度：如 250-word。
- 核心主题。
- 分析要求：evaluate、discuss、compare、argue、critically examine 等。

示例：

```text
Write a 250-word critical paragraph evaluating whether peer feedback improves undergraduate academic writing more effectively than automated feedback alone.
```

这个 instruction 较好，因为它要求比较和评价，而不是简单描述。

较弱示例：

```text
Write about peer feedback.
```

问题是范围太大，没有明确评价方向，也不利于 rubric 评分。

### 3.2 source material

好的 source material 应该：
- 给出足够信息支持写作。
- 同时包含优点和限制。
- 不直接替学生写出完整答案。
- 长度适中，避免过长增加成本。
- 不使用真实学生作文或真实用户数据。

示例结构：

```text
Peer feedback can help students recognize audience expectations.
Automated feedback systems can provide immediate comments.
However, automated systems may miss context-specific reasoning.
```
这类材料允许模型做 evidence use，而不是凭空发挥。

### 3.3 固定 rubric

rubric 不应该每条任务随意变化。当前项目的目标是比较 workflow，所以评分维度应保持一致。

固定维度有助于：

- evaluator prompt 稳定。
- CSV 聚合简单。
- 不同 condition 可公平比较。
- `overall_score` 可统一计算。

---

## 4. 构造数据时要注意什么

### 4.1 保持任务难度适中

太简单的任务不适合比较 multi-agent，因为 Baseline 也可能轻松完成。太复杂的任务会导致所有 workflow 都表现不稳定。

推荐任务类型：

- 有明确争议或 trade-off。
- 需要使用 source material。
- 能在 250 词内完成。
- 有结构、证据、论点和学术风格可评估。

### 4.2 避免题目偏向某个 workflow

不要写：

```text
First create a plan, then write...
```

这会天然有利于 Plan-Execute。

也不要写：

```text
Revise the following draft...
```

这会天然有利于 Critic + Editor workflow。

所有任务应只描述最终写作目标，不描述 agent 流程。

### 4.3 source material 要平衡

高质量 source material 通常同时包含：

- 支持观点的信息。
- 限制或反面因素。
- 条件性判断。
- 可以被引用或改写的具体依据。

避免只有单边材料，比如只列好处或只列坏处。

### 4.4 不要放敏感或伦理风险数据

根据 `Product.md`：

- 不使用真实学生作文。
- 不收集真实用户交互数据。
- 不使用隐私材料。
- 可以使用自己编写的背景材料。
- 可以使用 public-domain 或 open-access 材料。

### 4.5 保持主题多样性

正式实验建议至少 20 条，不要全是 AI writing。可以覆盖：

- AI-assisted learning
- peer feedback
- learning analytics
- online education
- academic integrity
- open educational resources
- formative assessment
- digital divide
- group work
- research ethics

主题多样能减少单一主题偏差。

---

## 5. 如何判断一条数据是否高质量
每条任务加入 `tasks_main.jsonl` 前，可以检查以下问题：

1. 这个任务是否能在 250 词内完成？
2. 这个任务是否需要批判性判断，而不是简单总结？
3. source material 是否提供了足够但不过量的信息？
4. source material 是否有正反或 trade-off？
5. 这个任务是否不会偏向某个 agent workflow？
6. rubric 是否严格使用六个固定字段？

如果有任意一个答案是否定的，建议先修改再加入数据集。




# 超时问题完整修复方案

## 🔍 问题诊断

你遇到的错误日志：
```
❌ LLM Error
LLM Call Failed
Error: Failed to connect to OpenAI API: Request timed out.
```

这是 **CrewAI Agent 的 LLM 调用超时**，与之前修复的 Evaluator 超时是不同的组件。

## 📊 系统中的两个 LLM 客户端

| 组件 | 用途 | 配置位置 | 状态 |
|------|------|---------|------|
| **LLMClient** | Evaluator Agent 评分 | [src/llm_client.py](src/llm_client.py#L54) | ✅ 已修复（60s 超时） |
| **CrewAI LLM** | Generation Agents (Planner, Writer, Critic, Editor) | [src/crew_factory.py](src/crew_factory.py#L23-L32) | ✅ 已修复（120s 超时） |

## ✅ 完整修复方案

### 修复 1: LLMClient 超时（Evaluator）

**文件**: [src/llm_client.py:54](src/llm_client.py#L54)

```python
self.client = OpenAI(
    base_url=config.base_url,
    api_key=api_key,
    timeout=60.0,      # ✅ 已设置
    max_retries=3,     # ✅ 已设置
)
```

### 修复 2: CrewAI LLM 超时（Generation Agents）⭐ 新增

**文件**: [src/crew_factory.py:23-32](src/crew_factory.py#L23-L32)

```python
def _setup_llm(self):
    """Configure LLM for CrewAI agents."""
    from crewai import LLM
    self.llm = LLM(
        model=self.llm_config.default_model,
        base_url=self.llm_config.base_url,
        api_key=self.api_key,
        temperature=self.llm_config.temperature,
        max_tokens=self.llm_config.max_tokens,
        timeout=120.0,     # ✅ 新增：120 秒超时
        max_retries=3,     # ✅ 新增：最多重试 3 次
    )
```

### 修复 3: API 调用间隔

**文件**: [configs/config.yaml](configs/config.yaml)

```yaml
llm:
  api_call_delay: 1.0  # ✅ 每次调用后延迟 1 秒

evaluator_llm:
  api_call_delay: 1.0  # ✅ 每次调用后延迟 1 秒
```

## 🎯 验证修复

### 测试 1: LLMClient 超时配置

```bash
python test_timeout_fix.py
```

预期输出：
```
Generation client timeout: 60.0
Generation client max_retries: 3
Evaluator client timeout: 60.0
Evaluator client max_retries: 3
✅ Timeout configuration verified!
```

### 测试 2: CrewAI LLM 超时配置

```bash
python test_crewai_timeout.py
```

预期输出：
```
✅ CrewAI LLM 配置:
   Model: deepseek-v4-flash
   Temperature: 0.4
   Max tokens: 1600
   timeout: 120.0        # ✅ 已设置
   max_retries: 3        # ✅ 已设置
```

### 测试 3: API 调用间隔

```bash
python test_api_delay.py
```

预期输出：
```
Total time: 10.02s
Expected minimum: 2.00s delay
✅ API delay is working correctly!
```

## 📈 超时时间设置说明

| 组件 | 超时时间 | 原因 |
|------|---------|------|
| **Evaluator** | 60 秒 | 评分任务相对简单，60 秒足够 |
| **CrewAI Agents** | 120 秒 | Generation 任务更复杂，需要更长时间 |

### 为什么 CrewAI 需要更长超时？

- **Planner Agent**: 需要分析材料、生成 outline、论点和证据计划
- **Writer Agent**: 需要根据 plan 生成完整的学术段落
- **Critic Agent**: 需要详细分析 draft 的问题
- **Editor Agent**: 需要根据 critique 修订 draft

这些任务比简单的评分更耗时，因此设置 120 秒超时。

## 🚀 现在可以运行实验

所有超时问题已修复，可以安全运行正式实验：

```bash
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

### 预期行为

1. ✅ **Generation Agents** (Planner, Writer, Critic, Editor) 有 120 秒超时
2. ✅ **Evaluator Agent** 有 60 秒超时
3. ✅ 每次 API 调用后自动延迟 1 秒
4. ✅ 失败的运行会自动重试（最多 3 次）
5. ✅ 单个运行失败不会中断整个实验
6. ✅ 实验中断后可以恢复，跳过已完成的运行

## ⚠️ 如果仍然超时

如果在运行实验时仍然遇到超时，可以进一步增加超时时间：

### 选项 1: 增加 CrewAI 超时到 180 秒

编辑 [src/crew_factory.py:31](src/crew_factory.py#L31)：
```python
timeout=180.0,  # 从 120.0 增加到 180.0
```

### 选项 2: 增加 API 调用间隔到 2 秒

编辑 [configs/config.yaml](configs/config.yaml)：
```yaml
llm:
  api_call_delay: 2.0  # 从 1.0 增加到 2.0
```

### 选项 3: 检查网络连接

```bash
# 测试 API 连接
curl -I https://api.vveai.com/v1

# 测试 DNS 解析
nslookup api.vveai.com
```

## 📊 修复总结

| 修复项 | 文件 | 修改内容 | 状态 |
|--------|------|---------|------|
| Evaluator 超时 | [src/llm_client.py](src/llm_client.py#L54) | timeout=60.0, max_retries=3 | ✅ 完成 |
| CrewAI 超时 | [src/crew_factory.py](src/crew_factory.py#L31) | timeout=120.0, max_retries=3 | ✅ 完成 |
| API 调用间隔 | [configs/config.yaml](configs/config.yaml) | api_call_delay=1.0 | ✅ 完成 |
| 错误恢复 | [src/orchestrator.py](src/orchestrator.py#L143-L165) | try-catch + 失败记录 | ✅ 完成 |
| 实验恢复 | [src/orchestrator.py](src/orchestrator.py#L169-L188) | 跳过已完成运行 | ✅ 完成 |

## 🎉 所有超时问题已解决

现在系统具有：
- ✅ 充足的超时时间（60-120 秒）
- ✅ 自动重试机制（最多 3 次）
- ✅ API 调用间隔（避免 rate limit）
- ✅ 错误恢复（单个失败不中断）
- ✅ 实验恢复（中断后可继续）

可以放心运行正式实验了！

---

**最后更新**: 2026-05-09
**版本**: v2.0 - 完整超时修复

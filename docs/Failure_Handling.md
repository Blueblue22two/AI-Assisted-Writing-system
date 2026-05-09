# 失败运行处理指南

## 🔄 当前的失败处理行为

### API 调用失败或超时时会发生什么？

1. **第一次运行时**：
   - ❌ 捕获异常，记录失败到 `results/runs.jsonl`
   - ⏭️ 继续运行下一个任务（不中断实验）
   - 📝 失败记录包含 `"status": "failed"` 和错误信息

2. **重新运行实验时**：
   - 🔄 **自动重试失败的运行**
   - ✅ 跳过已成功的运行
   - 💡 这样可以从中断处恢复，最终获得完整数据

### 示例失败记录

```json
{
  "task_id": "T001",
  "condition": "single_agent",
  "repetition_id": 1,
  "status": "failed",
  "error": "openai.APITimeoutError: Request timed out"
}
```

## 📊 查看失败运行

### 方法 1: 使用管理工具

```bash
python tools/manage_failed_runs.py --action analyze
```

输出示例：
```
======================================================================
📊 实验运行统计
======================================================================
总运行次数: 50
✅ 成功: 45 (90.0%)
❌ 失败: 5 (10.0%)
======================================================================

❌ 失败运行详情 (5 次):
----------------------------------------------------------------------

1. Task: T003, Condition: plan_execute, Rep: 2
   错误: openai.APITimeoutError: Request timed out

2. Task: T007, Condition: single_agent, Rep: 1
   错误: Connection reset by peer

...

======================================================================
📋 按错误类型分组:
======================================================================

错误类型: openai.APITimeoutError: Request timed out
出现次数: 3
影响的运行:
  - T003, plan_execute, rep 2
  - T007, single_agent, rep 1
  - T012, plan_execute_critique, rep 3
```

### 方法 2: 手动检查

```bash
# 统计失败次数
grep '"status": "failed"' results/runs.jsonl | wc -l

# 查看失败详情
grep '"status": "failed"' results/runs.jsonl | jq .
```

## 🛠️ 处理失败运行的策略

### 策略 1: 自动重试（推荐）⭐

**适用场景**：
- 临时网络问题
- API 限流
- 偶发性超时

**操作**：
```bash
# 直接重新运行实验，系统会自动重试失败的运行
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

**优点**：
- ✅ 无需手动干预
- ✅ 最终获得完整数据
- ✅ 适合大多数情况

**缺点**：
- ⚠️ 如果某个任务本身有问题，会反复失败

### 策略 2: 标记为已完成（跳过重试）

**适用场景**：
- 确认某些任务无法完成
- 想要快速完成剩余任务
- 接受部分数据缺失

**操作**：
```bash
# 1. 分析失败运行
python tools/manage_failed_runs.py --action analyze

# 2. 将失败运行标记为已完成（评分为 0）
python tools/manage_failed_runs.py --action mark-completed --output results/runs_cleaned.jsonl

# 3. 备份并替换
cp results/runs.jsonl results/runs_backup.jsonl
mv results/runs_cleaned.jsonl results/runs.jsonl

# 4. 继续运行实验（会跳过这些失败的运行）
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

**优点**：
- ✅ 避免反复失败
- ✅ 快速完成实验

**缺点**：
- ⚠️ 失败运行的评分为 0，会影响统计结果
- ⚠️ 数据不完整

### 策略 3: 删除失败记录（完全重试）

**适用场景**：
- 修复了导致失败的问题（如增加超时时间）
- 想要完全重新运行失败的任务

**操作**：
```bash
# 1. 删除失败记录
python tools/manage_failed_runs.py --action remove --output results/runs_cleaned.jsonl

# 2. 备份并替换
cp results/runs.jsonl results/runs_backup.jsonl
mv results/runs_cleaned.jsonl results/runs.jsonl

# 3. 重新运行（会重新尝试之前失败的运行）
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

**优点**：
- ✅ 清理失败记录
- ✅ 重新开始失败的运行

**缺点**：
- ⚠️ 如果问题未修复，可能再次失败

## 🔍 常见失败原因及解决方案

### 1. API 超时

**错误信息**：
```
openai.APITimeoutError: Request timed out
httpcore.ConnectTimeout: The handshake operation timed out
```

**解决方案**：
```yaml
# 增加超时时间（configs/config.yaml）
llm:
  api_call_delay: 2.0  # 从 1.0 增加到 2.0

evaluator_llm:
  api_call_delay: 2.0
```

或修改 [src/llm_client.py:54](src/llm_client.py#L54)：
```python
timeout=120.0,  # 从 60.0 增加到 120.0
```

### 2. API 限流

**错误信息**：
```
Rate limit exceeded
429 Too Many Requests
```

**解决方案**：
```yaml
# 增加调用间隔（configs/config.yaml）
llm:
  api_call_delay: 3.0  # 增加到 3 秒

evaluator_llm:
  api_call_delay: 3.0
```

### 3. 网络连接问题

**错误信息**：
```
Connection reset by peer
Connection refused
```

**解决方案**：
- 检查网络连接
- 检查 API endpoint 是否可访问
- 考虑使用代理或 VPN

### 4. API Key 问题

**错误信息**：
```
Invalid API key
Authentication failed
```

**解决方案**：
- 检查 `.env` 文件中的 API key
- 确认 API key 有效且有足够余额

## 📈 失败率分析

### 可接受的失败率

- **< 5%**: ✅ 正常，可能是临时网络问题
- **5-10%**: ⚠️ 需要关注，考虑增加超时或延迟
- **> 10%**: ❌ 有系统性问题，需要排查

### 如果失败率过高

1. **检查网络稳定性**
2. **增加超时时间**（60s → 120s）
3. **增加调用间隔**（1s → 2-3s）
4. **检查 API 服务状态**
5. **考虑分批运行**（先运行 5 个任务测试）

## 💡 最佳实践

### 1. 先小规模测试

```bash
# 使用 debug 模式测试
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_debug.jsonl --debug
```

### 2. 定期检查进度

```bash
# 查看已完成的运行数
wc -l results/runs.jsonl

# 查看失败次数
grep '"status": "failed"' results/runs.jsonl | wc -l
```

### 3. 备份结果文件

```bash
# 定期备份
cp results/runs.jsonl results/runs_backup_$(date +%Y%m%d_%H%M%S).jsonl
```

### 4. 监控实验日志

```bash
# 实时查看日志
tail -f experiment.log

# 查看错误
grep "ERROR" experiment.log
```

## 🔧 高级配置

### 在代码中添加更智能的重试逻辑

如果你想要更细粒度的控制，可以修改 [src/llm_client.py](src/llm_client.py) 添加指数退避重试：

```python
import time
from openai import OpenAI, APITimeoutError, RateLimitError

def chat_completion_with_retry(self, messages, max_retries=3, base_delay=2.0):
    """带指数退避的重试逻辑"""
    for attempt in range(max_retries):
        try:
            return self.chat_completion(messages)
        except (APITimeoutError, RateLimitError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # 指数退避: 2s, 4s, 8s
            logger.warning(f"API call failed (attempt {attempt+1}/{max_retries}), retrying in {delay}s: {e}")
            time.sleep(delay)
```

## 📞 需要帮助？

如果遇到持续的失败问题：

1. 运行诊断工具：
   ```bash
   python tools/manage_failed_runs.py --action analyze
   ```

2. 检查日志文件：
   ```bash
   grep "ERROR" experiment.log | tail -20
   ```

3. 查看具体错误信息，根据上述解决方案调整配置

---

**最后更新**: 2026-05-09
**版本**: v1.0

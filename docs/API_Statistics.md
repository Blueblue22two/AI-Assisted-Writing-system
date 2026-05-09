# API 调用统计与进度显示功能

## 📊 正式实验 API 调用统计

### 实验规模
- **任务数量**: 25 个
- **实验条件**: 3 个 (single_agent, plan_execute, plan_execute_critique)
- **每条件重复次数**: 3 次
- **总运行次数**: 25 × 3 × 3 = **225 次**

### API 调用次数详细计算

每次运行的 API 调用次数取决于实验条件：

| 条件 | Agent 调用 | Evaluator 调用 | 每次运行总调用 |
|------|-----------|---------------|---------------|
| **Condition A: single_agent** | Writer (1) | 1 | **2 次** |
| **Condition B: plan_execute** | Planner (1) + Writer (1) | 1 | **3 次** |
| **Condition C: plan_execute_critique** | Planner (1) + Writer (1) + Critic (1) + Editor (1) | 1 | **5 次** |

### 总 API 调用次数

- **Condition A**: 25 tasks × 3 reps × 2 calls = **150 次**
- **Condition B**: 25 tasks × 3 reps × 3 calls = **225 次**
- **Condition C**: 25 tasks × 3 reps × 5 calls = **375 次**
- **总计**: 150 + 225 + 375 = **750 次 API 调用**

### 预计运行时间

基于当前配置（`api_call_delay = 1.0s`）：

- **仅延迟时间**: 750 次 × 1 秒 = 12.5 分钟
- **API 响应时间**: 平均 2-5 秒/次 × 750 = 25-62.5 分钟
- **总预计时间**: **约 2-4 小时**

## ✅ 已实现的进度显示功能

### 1. 启动时显示总体信息

```
INFO - Loaded 25 tasks
INFO - Running 3 repetitions per condition
INFO - Total planned runs: 225 (25 tasks × 3 conditions × 3 reps)
```

### 2. 任务级进度条

使用 tqdm 显示整体任务进度：

```
Overall Progress:  40%|████      | 10/25 [00:45<01:08,  4.56s/task]
```

### 3. 详细的运行日志

每次运行都会输出详细信息：

```
INFO - 📋 Starting task T001 (1/25)
INFO - Task T001: 0/9 runs already completed
INFO - 🚀 Starting: task=T001, condition=single_agent, rep=1/3
INFO - ✅ Completed: task=T001, condition=single_agent, rep=1, score=4.75
INFO - 🚀 Starting: task=T001, condition=single_agent, rep=2/3
INFO - ✅ Completed: task=T001, condition=single_agent, rep=2, score=4.82
...
INFO - 📊 Task T001 completed: 9 runs
```

### 4. 跳过已完成运行的提示

如果实验中断后恢复：

```
INFO - ⏭️  Skipping completed: task=T001, condition=single_agent, rep=1
```

### 5. 错误处理提示

如果某次运行失败：

```
ERROR - ❌ Failed: task=T001, condition=single_agent, rep=1: Connection timeout
INFO - 📊 Task T001 completed: 8 successful, 1 failed
```

## 🎯 日志输出示例

完整的实验运行日志示例：

```
2026-05-09 10:00:00 - INFO - Loading configuration
2026-05-09 10:00:00 - INFO - Loaded 25 tasks
2026-05-09 10:00:00 - INFO - Running 3 repetitions per condition
2026-05-09 10:00:00 - INFO - Total planned runs: 225 (25 tasks × 3 conditions × 3 reps)
2026-05-09 10:00:00 - INFO - Starting experiment runs

Overall Progress:   0%|          | 0/25 [00:00<?, ?task/s]
2026-05-09 10:00:01 - INFO - 📋 Starting task T001 (1/25)
2026-05-09 10:00:01 - INFO - Task T001: 0/9 runs already completed
2026-05-09 10:00:01 - INFO - 🚀 Starting: task=T001, condition=single_agent, rep=1/3
2026-05-09 10:00:08 - INFO - ✅ Completed: task=T001, condition=single_agent, rep=1, score=4.75
2026-05-09 10:00:08 - INFO - 🚀 Starting: task=T001, condition=single_agent, rep=2/3
2026-05-09 10:00:15 - INFO - ✅ Completed: task=T001, condition=single_agent, rep=2, score=4.82
...
2026-05-09 10:00:45 - INFO - 📊 Task T001 completed: 9 runs

Overall Progress:   4%|▍         | 1/25 [00:45<18:00, 45.0s/task]
2026-05-09 10:00:45 - INFO - 📋 Starting task T002 (2/25)
...
```

## 📝 使用说明

### 运行正式实验

```bash
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

### 调整 API 调用间隔

编辑 `configs/config.yaml`：

```yaml
llm:
  api_call_delay: 1.0  # 调整此值（秒）

evaluator_llm:
  api_call_delay: 1.0  # 调整此值（秒）
```

建议值：
- **快速测试**: 0.5 秒
- **正常运行**: 1.0 秒（当前设置）
- **避免 rate limit**: 2.0-3.0 秒

### 实验中断恢复

如果实验中途中断，直接重新运行相同命令即可：

```bash
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

系统会自动：
1. 检查 `results/runs.jsonl` 中已完成的运行
2. 跳过已完成的 (task_id, condition, repetition_id) 组合
3. 只运行未完成的部分

## 🔍 监控实验进度

### 实时查看日志

```bash
tail -f experiment.log
```

### 查看已完成的运行数

```bash
wc -l results/runs.jsonl
```

### 查看最新完成的运行

```bash
tail -n 1 results/runs.jsonl | jq .
```

## ⚠️ 注意事项

1. **API 成本**: 750 次调用，请确保 API 账户余额充足
2. **运行时间**: 预计 2-4 小时，建议在稳定网络环境下运行
3. **中断恢复**: 支持中断后恢复，不会重复已完成的运行
4. **错误处理**: 单个运行失败不会中断整个实验
5. **日志文件**: 所有日志保存在 `experiment.log`

## 📈 实验完成后

运行结果分析：

```bash
python -m src.experiments.analyze --results results/runs.jsonl
```

将生成：
- `results/scores.csv` - 所有运行的分数
- `results/condition_summary.csv` - 条件级聚合统计
- `results/win_rates.csv` - 配对比较结果
- `results/mean_scores.png` - 平均分对比图
- `results/score_distribution.png` - 分数分布图
- `results/detailed_metrics.png` - 六维指标对比图
- `results/runtime.png` - 运行时间对比图

---

**最后更新**: 2026-05-09
**版本**: v1.0

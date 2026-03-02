# ISSUE-005: 实时工作状态 + API 用量监控

**状态**: 🔄 进行中  
**优先级**: 高  
**创建时间**: 2026-03-02  
**负责人**: Codex（执行）+ 虾哥（审查）

---

## 任务描述

用户需要通过 Dashboard 实时观察：
1. Codex CLI 调用情况和用量统计
2. OpenClaw API 调用情况和用量统计
3. 当前工作状态（工作中/空闲/具体任务）

---

## 验收标准

### 1. Codex 用量展示
- [ ] 今日 Codex 会话数量
- [ ] 今日 Token 使用量
- [ ] 最近 Codex 调用记录（时间、任务、token 用量）
- [ ] Rate Limit 状态

### 2. OpenClaw API 用量展示
- [ ] 今日 API 调用次数
- [ ] Token 使用统计（输入/输出）
- [ ] 成本统计
- [ ] 最近 API 调用记录

### 3. 实时工作状态
- [ ] 当前状态（工作中/空闲/思考中/执行中）
- [ ] 当前任务描述
- [ ] 任务开始时间
- [ ] 任务进度（百分比或步骤）
- [ ] 最近活动日志（最后更新时间）

---

## 技术实现

### 状态文件
创建 `~/.openclaw/workspace/.state.json` 记录：
```json
{
  "status": "working",
  "current_task": "开发 ISSUE-005",
  "started_at": "2026-03-02T11:54:00+08:00",
  "progress": 45,
  "last_update": "2026-03-02T11:54:00+08:00",
  "activity_log": [...]
}
```

### API 扩展
- `/api/usage` - 返回用量统计
- `/api/status` - 返回实时工作状态

### 前端展示
- 新增"用量统计"卡片
- 新增"工作状态"指示器
- 实时更新（每 5 秒）

---

## 相关文件

- `src/main.py` - 新增 API 端点
- `src/openclaw_api.py` - 用量统计函数
- `src/templates/index.html` - 前端展示
- `.state.json` - 状态文件（自动创建）

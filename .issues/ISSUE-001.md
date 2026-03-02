# ISSUE-001: FastAPI 后端框架

**状态**: ✅ 已完成  
**优先级**: 高  
**创建时间**: 2026-03-02  
**完成时间**: 2026-03-02  
**负责人**: Codex（执行）+ 虾哥（审查）

---

## 完成说明

- [x] 创建 `requirements.txt` - 包含 fastapi, uvicorn, jinja2, python-multipart
- [x] 创建 `src/main.py` - FastAPI 应用，包含根路径和 /api/health
- [x] 创建 `src/templates/index.html` - 基础 HTML 页面
- [x] 服务启动测试通过 - `curl http://localhost:8000/api/health` 返回 `{"status":"ok"}`

---

## 任务描述

创建 FastAPI 后端框架，作为仪表板的基础。

---

## 验收标准

- [ ] 创建 `src/main.py` - FastAPI 应用入口
- [ ] 创建 `requirements.txt` - 项目依赖
- [ ] 创建基础 HTML 模板
- [ ] 实现健康检查接口 `/api/health`
- [ ] 服务可以启动并访问

---

## 技术提示

### 依赖
```
fastapi>=0.100.0
uvicorn>=0.23.0
jinja2>=3.1.0
python-multipart>=0.0.6
```

### 基础结构
```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="OpenClaw Dashboard")

@app.get("/")
async def index():
    return HTMLResponse("<h1>OpenClaw Dashboard</h1>")

@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

### 启动命令
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 相关文件

- `src/main.py`
- `requirements.txt`
- `src/templates/index.html`

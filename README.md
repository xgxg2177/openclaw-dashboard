# OpenClaw Dashboard 📊

**OpenClaw 实时监控仪表板**

---

## 🎯 项目目标

实时展示 OpenClaw 运行状态：
- 是否在工作、在做什么
- 当前对话内容
- 已加载技能
- 配置信息（模型、token 等）

---

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/main.py

# 访问 http://localhost:8000
```

---

## 📁 项目结构

```
openclaw-dashboard/
├── src/
│   ├── main.py           # FastAPI 应用
│   ├── openclaw_api.py   # OpenClaw API 封装
│   └── templates/        # HTML 模板
├── static/               # 静态资源
├── tests/                # 测试
├── requirements.txt
└── README.md
```

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python + FastAPI |
| 前端 | HTML + HTMX + Tailwind CSS |
| 数据源 | OpenClaw 工具 API |

---

## 📊 功能模块

- [ ] 运行状态展示
- [ ] 当前任务展示
- [ ] 会话列表
- [ ] 技能展示
- [ ] 配置查看
- [ ] 实时刷新

---

**状态**: 🔄 开发中  
**创建时间**: 2026-03-02

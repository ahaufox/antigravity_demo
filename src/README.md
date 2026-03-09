# Source Code (src) 

本项目源代码目录，遵循 **Antigravity** 开发规范。

## 技术栈概览
- **Backend**: Python 3.10+ / FastAPI
- **Database**: PostgreSQL (SQLAlchemy + Alembic)
- **Cache**: Redis
- **Governance**: 严格遵循 [开发规则](../.agents/rules/development_rules.md)

## 目录结构
- `backend/`: 服务端逻辑与模型定义。
  - `alembic/`: 数据库架构迁移管理。
- `utils/`: 统一样式的工具库（如日志、路径处理等）。

## 开发注意事项
- **日志**: 必须通过项目统一的初始化函数配置。
- **异常**: 遵循标准化捕获与返回逻辑。
- **注释**: 核心业务逻辑注释必须使用**简体中文**。

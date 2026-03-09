---
trigger: always_on
---

# 开发技术规范 (Development Rules)

## 1. 技术栈要求
- **后端**: 严格基于 FastAPI 生命周期 (`lifespan`) 管理。数据库使用 PostgreSQL 16+，优化 SQL 性能。
- **前端**: UI/UX 极度克制、注重留白。遵守设定的字体规范（Noto Sans, ZCOOL）。
- **质量保证**: 核心业务流必须有 Playwright 自动化测试覆盖。

## 2. 编码习惯
- **中文本地化**: 代码注释、函数说明、类描述、Docstrings 必须使用中文。日志消息优先中文。
- **命名规范**: 变量、函数、类名保持英文。
- **路径规范**: 始终使用**相对路径**，严禁硬编码用户特定路径。
- **Python 标准**: 遵循 PEP 8。使用 Pydantic V2 (`model_config`)。
- **时间处理**: 使用 `datetime.now(datetime.UTC)`。

## 3. 数据库与日志
- **架构变更**: 必须使用 Alembic。详情参阅 [db_rules.md](db_rules.md)。
- **日志记录**: 必须通过 `logging_utils` 初始化，严禁 `print()`。详情参阅 [logging_rules.md](logging_rules.md)。

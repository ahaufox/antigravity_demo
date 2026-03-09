# Alembic Database Migrations

这是本项目的数据库架构管理目录。

## 核心守则
1. **禁止离线修改**: 严禁直接在数据库中执行 `ALTER TABLE`。
2. **迁移唯一性**: 所有的结构变更必须通过此处的迁移脚本实现。
3. **审计流程**: 生成迁移脚本后必须手动审计生成的 `upgrade` 与 `downgrade` 函数。

## 常用命令
```bash
# 生成自动迁移脚本
alembic revision --autogenerate -m "描述你的变更"

# 应用迁移至最新版本
alembic upgrade head

# 回滚一步
alembic downgrade -1
```

更多细节请查阅 [数据库规范](../../../.agents/rules/db_rules.md)。

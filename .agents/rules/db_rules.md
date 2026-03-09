---
trigger: always_on
---

# 数据库规范

## 1. 架构迁移
- **Alembic 标准**: 所有数据库架构变更（创建表、添加/修改列等）**必须**通过工具配置的迁移目录（通常在 `backend/alembic` 下）执行。
- **禁止手动 DDL**: 严禁直接在数据库上执行手动的 `CREATE TABLE` 或 `ALTER TABLE` 操作。所有结构性变更必须通过迁移脚本可追溯。
- **迁移流程**:
    1. 在模型定义目录中更新 SQLAlchemy 模型。
    2. 使用 `alembic revision --autogenerate -m "描述"` 生成迁移脚本。
    3. 检查生成的脚本是否准确。
    4. 使用 `alembic upgrade head` 应用迁移。

## 2. 模型一致性
- 确保 SQLAlchemy 模型始终反映数据库架构的最新状态。
- 每次架构迁移都必须伴随相应的模型更新。

## 3. 初始化脚本
- 基础初始化脚本应与当前的架构状态保持同步，用于新环境的搭建。但后续的任何变更都必须通过 Alembic 进行。

## 4. 数据填充与同步
- **职责分离**: Alembic 是数据库**架构 (Schema)**（结构）的唯一真理。数据初始化脚本仅用于**数据 (Data)** 填充。
- **仅限数据规则**: 用于运行时数据同步的 SQL 脚本**必须**仅包含数据操作。它们**严禁**包含 `CREATE TABLE`、`DROP TABLE` 或 `ALTER TABLE` 语句。
- **幂等数据同步**: 通过使用 `DELETE FROM` 后接 `INSERT` 语句来确保脚本的幂等性。
- **导出最佳实践**: 生成此类脚本时，使用 `pg_dump --data-only --inserts --column-inserts`。

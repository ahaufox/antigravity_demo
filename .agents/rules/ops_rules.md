# 部署与运维手册 (OPS Rules)

## 1. 服务控制
基础编排文件通常位于: `[PROJECT_ROOT]/deploy/docker-compose.yml`

| 动作 | 命令 |
|------|------|
| 启动数据库 | `docker compose up -d db` |
| 启动全量服务 | `docker compose up -d` |
| 监控启动 | `docker compose -f docker-compose.monitoring.yml up -d` |

## 2. 核心运维脚本
建议位置: `[PROJECT_ROOT]/scripts/deploy/`

- `setup.sh`: 环境初始化。
- `deploy.sh`: 一键流水线（Pull/Build/Up）。
- `backup.sh`: 数据冷备份。
- `restore.sh`: 数据恢复（**高危，需审批**）。

## 3. 测试与监控入口
- **测试种子**: `python [PATH_TO_SEEDER]/test_data_seeder.py --target all` (仅限 Dev/Test 环境)。
- **监控终端**: 
  - Grafana: `:3001` (admin/admin)
  - Prometheus: `:9090`
- **DB 连接**: 统一使用环境变量 `DATABASE_URL` 配置。例：`postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DB_NAME]`

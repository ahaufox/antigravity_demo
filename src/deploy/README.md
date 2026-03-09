# 部署与运维指南 (Deployment & OPS)

本目录包含项目的部署配置、运维脚本及自动化发布流程。

## 🏗️ 部署架构

项目采用 Docker 化部署方案，核心组件包括：
- **FastAPI Backend**: 业务逻辑层。
- **PostgreSQL 16**: 核心持久化数据库。
- **Redis**: 缓存与异步任务队列。
- **Nginx/Caddy**: 反向代理与 SSL 终端。

## 🚀 快速部署

### 1. 环境准备
确保已安装 `docker` 和 `docker-compose`。

### 2. 配置环境变量
复制并配置 `.env` 文件：
```bash
cp .env.example .env
# 编辑 .env 填写数据库、密钥及 Redis 配置
```

### 3. 启动服务
```bash
docker-compose up -d --build
```

## 🛠️ 运维操作

### 数据库迁移
所有架构变更必须通过 Alembic 执行：
```bash
# 执行迁移
docker-compose exec backend alembic upgrade head
```

### 日志查看
```bash
docker-compose logs -f [service_name]
```

### 备份与恢复
详见 `scripts/` 目录下的备份脚本。

---
> [!IMPORTANT]
> **生产安全须知**：
> 1. 严禁在 `docker-compose.yml` 中硬编码任何正式环境的密码或密钥。
> 2. 定期执行数据库备份，并验证恢复脚本的有效性。
> 3. 所有的 DDL 操作必须经过审计并由 Alembic 记录。

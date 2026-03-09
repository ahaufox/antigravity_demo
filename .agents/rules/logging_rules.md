# 日志规范 (Logging Rules)

## 1. 核心原则
- **一处配置，全局生效**：严禁在业务代码中直接调用 `logging.basicConfig()` 或手动添加 `Handlers`。
- **全量收敛**：所有日志行为必须通过统一的配置文件（如 `logging.yaml`）进行统一管控。
- **标准化初始化**：应用入口及独立运行的脚本必须在最早期调用统一的初始化函数。

## 2. 使用规范

## 2.1 日志初始化 (标准范式)
为了确保任何模块独立运行时都能拥有正确的日志格式，**每个 Python 文件**在导入 `logging` 后都应立即调用项目定义的 `init_log_config()`。

```python
import logging
# 从项目工具库导入初始化函数
from [UTILS_PATH].logging_utils import init_log_config

# 初始化日志
init_log_config()
logger = logging.getLogger(__name__)
```

## 2.2 记录器获取
- **业务模块**：始终使用 `logging.getLogger(__name__)`。
- **核心组件**: 可以定义特定命名获取记录器以实现日志分流存储。

## 2.3 严禁行为
- ❌ **严禁 `print()`**：所有调试信息必须使用 `logger.debug()` 或 `logger.info()`。
- ❌ **严禁硬编码路径**：严禁在代码中硬编码日志目录路径，所有持久化路径应在配置文件中定义。
- ❌ **时间格式**: 除非特殊需求，时间格式统一锁定为 `MM-DD HH:MM:SS`，且必须强制东八区。

## 3. 配置文件管理
- 配置文件是日志系统的唯一真值来源。
- 严禁在业务代码中手动创建 `FileHandler` 或手动修改 Handler 的输出路径。

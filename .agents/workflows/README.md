---
name: workflow-index
description: AI 助手工作流库
---

# AI 助手工作流库 (Workflows Library)

本目录存储 AI 助手的自动化工作流,涵盖开发、维护、内容创作等多个领域。

## 📁 目录索引

### 🔧 通用工作流 (General)
- [Bug 修复 (Bug Fix)](general/bug-fix.md): 修复 bug 并补齐测试与约定式提交信息
- [README 更新 (README Update)](general/readme-update.md): 自动更新技术型 README.md 的规范工作流
- [全栈验证 (Auto PRD Check)](general/auto-prd-check.md): 自动化项目全栈验证工作流
- [哲学同步 (Philosophy Sync)](general/philosophy-sync.md): 自动将哲学智慧同步为思维模型

### ✍️ 内容创作工作流 (Write)
- [小红书笔记生成 (Note Gen)](write/note-gen.md): 小红书爆款笔记生成工作流

### 🎨 MindSeed 内容工作流 (MindSeed)
位于 `general/mindseed/`:
- [MindSeed 内容生成 (MindSeed Content Gen)](general/mindseed/mindseed-content-gen.md): MindSeed 精神高潮育儿文案生成工作流(Matrix → Draft → HTML)
- [MindSeed CSV 自动化 (MindSeed CSV Automation)](general/mindseed/mindseed-csv-automation.md): MindSeed 全流程自动化 - 文案生成(MD) → 数据结构化(JSON) → 视觉渲染(HTML)

### 🎭 UI 设计工作流 (UI Design)
位于 `general/ui_design/`:
- [理性设计 (Rational Design)](general/ui_design/01-rational-design.md): 专注于逻辑架构、数据流与组件结构
- [感性设计 (Emotional Design)](general/ui_design/02-emotional-design.md): 专注于视觉美学、情感共鸣与动态交互
- [整合设计 (Design Synthesis)](general/ui_design/03-design-synthesis.md): 专注于理性与感性的融合、冲突解决与最终交付

### 📋 顶层工作流
- [AI 助手进化 (Agent Evolution)](agent-evolution.md): AI 助手每日进化与维护协议
- [API测试覆盖扩充 (API Test Coverage)](api-test-coverage.md): 自动化识别、生成与验证 API 单元测试
- [新UI设计 (New UI)](new-ui.md): 新UI设计工作流

### 🤖 Agent 工作流
位于 `agents/`:
- [ADM (Agent Decision Model)](agents/adm.md): Agent 决策模型
- [Anti](agents/anti.md): 反模式工作流
- [CC (Creative Context)](agents/cc.md): 创意上下文
- [SD (System Design)](agents/sd.md): 系统设计

---

## 🎯 使用指南

### 触发工作流
在对话中使用 `/workflow-name` 命令触发对应工作流,例如:
- `/agent-evolution` - 执行 AI 助手每日进化审计
- `/mindseed-csv-automation` - 执行 MindSeed 全流程自动化

### 工作流分类原则
- **general/**: 通用开发与维护工作流,适用于任何项目
- **write/**: 内容创作与调研工作流,专注于文案、笔记、商业分析
- **general/mindseed/**: MindSeed 项目专用工作流,处理育儿内容生成与渲染
- **general/ui_design/**: UI 设计工作流,分为理性(架构)、感性(视觉)与整合三个阶段
- **agents/**: Agent 相关工作流,用于 AI 助手自身决策与设计

---

> [!TIP]
> 工作流文件遵循 YAML frontmatter + Markdown 格式。如需创建新工作流,请参考现有工作流的结构,并确保包含清晰的触发条件、执行步骤和角色建议。

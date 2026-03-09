# Agent Evolution 工作流 - 使用指南

> **MindSeed 首席架构师** - AI 助手定期自审计与优化系统
> 
> **格言**: 用最理性的架构，构建最感性的连接。

---

## 📋 概述

Agent Evolution 工作流实现了 AI 助手对项目的 `.agents` 基础设施、代码资产和 PRD 一致性的自动化审计，确保代码实现与 PRD 文档保持一致。

**核心定位**: MindSeed 家庭通心平台 - 连接代际情感的智能桥梁。

---

## 🚀 快速开始

### 1. 执行全量审计

```bash
cd f:\mindseed
python .agents/workflows/scripts/agent-evolution.py --type full
```

### 2. 查看审计报告

审计完成后会生成两个文件：
- `agent_evolution_report_YYYYMMDD_HHMMSS.md` - Markdown 格式报告
- `agent_evolution_report_YYYYMMDD_HHMMSS.json` - JSON 格式报告

---

## 📖 命令参数

### 审计类型（--type）

| 参数 | 说明 | 适用场景 |
|------|------|----------|
| `full` | 全量审计（默认） | 每周例行审计 |
| `infra` | 仅审计基础设施 | 快速检查 `.agents` 健康度 |
| `code` | 仅审计代码资产 | 代码审查前检查 |
| `prd` | 仅审计 PRD 一致性 | 功能开发完成后验收 |

### 输出目录（--output-dir）

```bash
# 指定报告输出目录
python .agents/workflows/scripts/agent-evolution.py --type full --output-dir .agents/workflows/reports/
```

### 项目根目录（--project-root）

```bash
# 指定项目根目录（默认当前目录）
python .agents/workflows/scripts/agent-evolution.py --type full --project-root /path/to/project
```

---

## 🔍 审计模块

### 1. 基础设施审计

**检查项**:
- ✅ 工作流健康度（frontmatter、description、执行步骤）
- ✅ 技能可用性（SKILL.md、可执行脚本）
- ✅ 规则一致性（core_rules.md、db_rules.md）

**关键指标**:
- 工作流健康率
- 技能可用率
- 规则一致性得分

### 2. 代码资产审计

**检查项**:
- ✅ 后端 Router 测试覆盖率
- ✅ 前端组件测试覆盖率
- ✅ 总体测试覆盖率

**关键指标**:
- 后端测试覆盖率
- 前端测试覆盖率
- 测试文件/源文件比例

### 3. PRD 一致性审计

**检查项**:
- ✅ 功能对照（PRD 定义 vs 代码实现）
- ✅ 埋点验证（事件名称、参数）
- ✅ 合规检查（敏感词过滤、数据加密、隐私保护）

**关键指标**:
- 功能实现率
- 埋点验证率
- 合规检查通过率

---

## 📊 审计报告

### 报告结构

```markdown
# Agent Evolution 审计报告

## 概览
- 发现问题总数
- 按严重程度分类统计

## 基础设施健康度
- 状态
- 关键指标
- 发现问题

## 代码资产质量
- 状态
- 关键指标
- 发现问题

## PRD 一致性
- 状态
- 关键指标
- 发现问题

## 改进建议
1. ...
2. ...

## 负向约束检查
- Alembic 迁移
- 测试覆盖率
- PRD 对比
- 安全合规
- 路径规范
```

### 问题严重程度

| 级别 | 说明 | 响应时间 |
|------|------|----------|
| **Critical** | 严重问题，影响系统安全或核心功能 | 立即处理 |
| **High** | 高优先级问题，影响重要功能 | 24 小时内 |
| **Medium** | 中优先级问题，影响用户体验 | 72 小时内 |
| **Low** | 低优先级问题，优化建议 | 1 周内 |

---

## ✅ 使用示例

### 示例 1: 每周例行审计

```bash
# 周一上午执行全量审计
python .agents/workflows/scripts/agent-evolution.py --type full --output-dir .agents/workflows/reports/

# 查看报告
cat .agents/workflows/reports/agent_evolution_report_*.md
```

### 示例 2: 快速检查基础设施

```bash
# 代码提交前快速检查
python .agents/workflows/scripts/agent-evolution.py --type infra
```

### 示例 3: 功能开发完成后验收

```bash
# 新功能开发完成后检查 PRD 一致性
python .agents/workflows/scripts/agent-evolution.py --type prd
```

---

## 🧠 最佳实践

### 1. 定期执行

**建议频率**:
- **全量审计**: 每周一次（建议周一上午）
- **基础设施审计**: 每日一次（可选）
- **代码资产审计**: 每次代码提交前
- **PRD 一致性审计**: 每个功能开发完成后

### 2. 报告评审

**评审流程**:
1. 查看总体状态（passed/warning/failed）
2. 优先处理 Critical 和 High 级别问题
3. 制定 Medium/Low 级别问题修复计划
4. 跟踪改进建议执行情况

### 3. 问题跟踪

**问题管理**:
- 使用审计报告的 `FINDING-XXXX` ID 作为问题追踪编号
- 在 Git Issue 或任务管理系统中创建对应任务
- 标记优先级和责任人
- 定期回顾问题解决进度

---

## 🛠️ 扩展与定制

### 添加新的审计检查项

编辑 `.agents/workflows/scripts/agent-evolution.py`，在对应的审计模块中添加检查逻辑：

```python
def audit_infrastructure(self) -> AuditModuleResult:
    # 添加新的检查项
    # ...
    
    # 创建问题发现
    findings.append(AuditFinding(
        id=self.generate_finding_id(),
        severity=Severity.HIGH,
        category="new_category",
        title="新问题标题",
        description="问题描述",
        location="问题位置",
        recommendation="修复建议"
    ))
```

### 自定义报告模板

编辑 `.agents/workflows/templates/audit-report-template.md`，修改报告格式和内容。

### 集成到 CI/CD

```yaml
# GitHub Actions 示例
name: Agent Evolution Audit

on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一上午 9 点
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Agent Evolution Audit
        run: |
          python .agents/workflows/scripts/agent-evolution.py --type full
      
      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: agent_evolution_report_*.md
```

---

## 📁 文件结构

```
.agents/workflows/
├── agent-evolution.md              # 工作流定义
├── scripts/
│   └── agent-evolution.py          # 主执行脚本
├── templates/
│   └── audit-report-template.md    # 审计报告模板
├── checklists/
│   └── agent-evolution-checklist.md # 审计检查清单
└── reports/                        # 审计报告输出目录（需创建）
    └── .gitkeep
```

---

## 🔗 相关文档

- [工作流定义](agent-evolution.md)
- [检查清单](checklists/agent-evolution-checklist.md)
- [审计报告模板](templates/audit-report-template.md)
- [PRD 文档](../../src/core/docs/prd/01_main.md)
- [核心规则](../../.trae/rules/core_rules.md)
- [数据库规范](../../.trae/rules/db_rules.md)

---

## ❓ 常见问题

### Q1: 审计报告显示"warning"状态，是否需要立即处理？

**A**: 视情况而定。如果只有 Medium/Low 级别问题，可以按计划逐步修复。如果有 High 级别问题，建议 24 小时内处理。

### Q2: 如何忽略某些误报？

**A**: 可以在审计脚本中添加白名单逻辑，或者在审计后手动标记某些问题为"已接受风险"。

### Q3: 审计报告是否可以自定义格式？

**A**: 可以。修改 `templates/audit-report-template.md` 即可自定义 Markdown 报告格式。JSON 格式报告始终包含完整数据。

### Q4: 审计执行时间过长怎么办？

**A**: 可以使用 `--type infra` 或 `--type code` 执行增量审计，仅检查特定模块。

---

## 📝 更新日志

### v1.0 (2026-03-01)
- ✅ 初始版本发布
- ✅ 基础设施审计模块
- ✅ 代码资产审计模块
- ✅ PRD 一致性审计模块
- ✅ 审计报告生成（Markdown + JSON）
- ✅ 检查清单和模板

---

> [!IMPORTANT]
> **元原则**: 一切为了**家庭通心**。代码的终极目标是连接代际情感，而非技术本身。
> 
> **格言**: 用最理性的架构，构建最感性的连接。

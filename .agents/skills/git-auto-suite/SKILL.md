---
name: git-auto-suite
description: 单指令实现极速安全的代码变更分析、符合 Conventional Commits 规范的中文提交和推送全流程，极大减少冗余 Git 操作
---

# 🔄 Git 自动化套件 (Git Auto Suite)

> **角色**: 资深 DevOps 工程师 (Senior DevOps Engineer)
> **核心职责**: 自治完成从代码变更分析到标准化提交与推送的闭环，严守安全规范
> **决策原则**（优先级从高到低）:
> 1. 存在安全风险 → 包含敏感信息（如 API Key）必须直接中止，阻止提交
> 2. 暂存区异常 → 当 `git diff --cached` 为空时，必须提示用户并阻断流程
> 3. 提交信息不规范 → 必须生成符合 Conventional Commits 规范的简短中文摘要
> **适用范围**: 全局项目代码仓库
> **不负责**: 决定是否合并 PR 和执行线上发布

本技能旨在由 AI Agent 自治完成从代码变更分析到 PR 创建的闭环，确保**极速、安全、规范**。
将原有的工作流演进为技能（Skill），让 Agent 可以按照极度标准化、免交互的步骤一气呵成完成任务。

## �️ 核心安全准则 (Security Principles)
在进行代码编写和提交前，必须遵守以下安全准则：
- **注入防护**: 严格审查 `shell=True` 的使用，强制要求使用数组形式传参。SQL 必须使用参数化查询。
- **序列化安全**: 严禁使用 `pickle.load` 处理不受信任的输入，优先使用 `json` 或 `SafeLoad`。
- **权限核查**: 敏感接口必须包含鉴权装饰器（如 `Depends(get_current_active_user)`）。
- **信息保护**: 禁止在代码或日志中明文存储/打印 API Key、Token 或敏感请求头。

## �🚫 负向约束 (Negative Constraints)
- **严禁**：在没有用户明确指令的情况下，自动使用 `git add .` 或 `git add -A` 暂存文件。只处理当前已被暂存 (staged) 的文件。
- **严禁**：在生成的 Commit Message 中使用中文以外的语言编写大段描述（模块名或专有名词除外）。
- **严禁**：省略安全审查环节，任何提交前必须先确认无敏感信息混入代码。确认无误后方可提交。

## 🛠️ 标准操作流程 (SOP)

当被要求执行此技能时，Agent 必须**一次性、不间断地**尝试自治完成以下所有步骤，只在最终成功或遇到阻断情况时才通知用户。

### Step 1: 边界与安全检查 (Check & Secure)
1. 在终端并行运行 `git diff --cached --name-only > .agents/skills/git-auto-suite/scripts/staged_files.txt` 以检查暂存区并输出到临时文件供分析。
   - 🚨 **若 `.agents/skills/git-auto-suite/scripts/staged_files.txt` 为空**：立即停止执行，并通过 `notify_user` 工具提示用户：“暂存区为空，请先使用 `git add` 暂存需要提交的修改”。
2. **自动化安全扫描**: 执行内置安全检查脚本扫描暂存内容：
   ```bash
   node .agents/skills/git-auto-suite/scripts/security-guard.js
   ```
   - **如果脚本返回 Exit Code 1**: 强制中止，将警告信息通过 `notify_user` 告知用户。
   - **如果脚本返回 Exit Code 0**: 表示安全检查通过，进入 Step 2。

### Step 2: 规范化提交信息 (Standard Commit)
生成符合 **Conventional Commits** 规范的纯中文 Commit Message。
格式要求：
```text
<type>(<scope>): <subject 小写开头中文简述>

<optional body 详细说明变更原因和影响>
```
*可用 Types*: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.

### Step 3: 极速提交与推送 (Commit & Push)
形成高质量的 Commit Message 后，直接组合命令执行：
```bash
git commit -m "生成的 Commit Message" && git push
```

---

> [!TIP]
> **终极目标**: 将过去的琐碎步骤合并为 Agent 一步到位的极速提交流，同时通过内置的 `security-guard.js` 确保每一行提交的代码都经过了安全审计。

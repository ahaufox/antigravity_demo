---
description: UI 设计理性工作流 - 专注于逻辑架构、数据流与组件结构
role: Information Architect / Systems Engineer
---

# 理性设计工作流

> **核心隐喻**: "骨架" (The Skeleton)
> **目标**: 确保系统功能完备、逻辑自洽、结构清晰、数据流转顺畅。
> **输出**: 高保真线框图代码 (Skeleton Code), 定义清晰的 Props 接口, 无样式的布局结构。

---

## 步骤 1: 需求与数据建模 (Model)

在编写任何 UI 代码之前，必须先明确数据结构与业务逻辑。

1. **输入分析**:
   - 用户需要输入什么？(Form Schema)
   - 系统需要展示什么？(View Schema)
   - 数据来源是静态 (Astro) 还是动态 (React Client)？

2. **数据定义 (TypeScript Interfaces)**:
   - 定义组件的 `Props` 接口。
   - 定义核心业务对象 (Domain Objects)。
   - **MindSeed 规范**:
     - 严格区分 `*.astro` (静态) 与 `*.tsx` (交互) 组件。
     - 交互组件需定义清晰的 Event Handlers (如 `onSave`, `onChange`).

   ```typescript
   // 示例: 核心数据接口
   interface ParentingStrategy {
     id: string;
     title: string; // 标题
     steps: string[]; // 步骤列表
     isLocked: boolean; // 权限状态
   }
   ```

## 步骤 2: 组件架构 (Architecture)

根据 "Islands Architecture" (岛屿架构) 拆分 UI。

1. **原子拆分**:
   - 识别可复用的原子组件 (Atoms): 按钮, 输入框, 标签。
   - 识别业务组件 (Molecules): 搜索栏, 卡片, 表单组。
   - 识别页面区块 (Organisms): 侧边栏, 内容区, 支付弹窗。

2. **状态归属判断**:
   - **Local State**: 仅组件内部使用 (如：展开/收起, 输入框临时值)。
     * *注意*: 数值输入框需使用 string state 处理中间态 (如 "0.")。
   - **Lifted State**: 父组件需要感知的状态 (如：表单提交数据)。
   - **Global State**: 跨页面共享 (尽量避免, 优先使用 URL 参数或 Nano Stores)。

## 步骤 3: 结构与布局 (Structure)

编写 "无样式" 或 "仅布局" 的 HTML/JSX 结构。

1. **语义化 HTML**:
   - 使用 `<header>`, `<main>`, `<article>`, `<section>`, `<aside>`, `<footer>`。
   - 按钮必须是 `<button>`, 链接必须是 `<a>`。

2. **布局框架 (Layout Skeleton)**:
   - 仅使用布局相关的 Tailwind 类 (Layout & Flexbox/Grid)。
   - **禁止** 使用颜色、阴影、圆角等装饰性样式。

   ```tsx
   // ✅ 理性阶段代码示例
   <section className="flex flex-col gap-4 w-full max-w-2xl">
     <header className="flex justify-between items-center">
       <h2>{title}</h2>
       {/* 仅布局占位 */}
       <div className="w-8 h-8" />
     </header>
     <main className="grid grid-cols-1 md:grid-cols-2 gap-6">
       {children}
     </main>
   </section>
   ```

## 步骤 4: 逻辑实现 (Logic)

1. **Hooks 封装**:
   - 将复杂逻辑抽离为 Custom Hooks (如 `usePaymentStatus`).
   - 保持 UI 组件纯净 (Presentational Component)。

2. **边界情况处理**:
   - **Loading**: 加载中状态 (Skeleton Screen 占位符)。
   - **Error**: 错误提示与重试机制。
   - **Empty**: 空数据状态 (Empty State)。

3. **交互验证**:
   - 确保点击事件、表单提交都能触发预期的 `console.log` 或 API 调用。
   - 验证数据流向是否正确 (Child -> Parent -> Server/API)。

## 步骤 5: 可访问性检查 (Accessibility)

1. **ARIA 属性**:
   - 为非标准控件添加 `role`, `aria-label`, `aria-expanded` 等。
2. **键盘导航**:
   - 确保 `Tab` 键顺序符合逻辑。
   - 确保所有交互元素均可通过键盘触发 (Enter/Space)。

---

## ✅ 理性阶段验收标准

- [ ] 类型定义 (TypeScript Interfaces) 完整且无 `any`。
- [ ] 组件结构符合 Atomic Design。
- [ ] 布局在不同断点 (Mobile/Desktop) 下逻辑正确 (不考虑美观)。
- [ ] 所有交互逻辑 (点击、输入) 已连通并测试通过。
- [ ] 包含 Loading / Error / Empty 三种状态的逻辑分支。
- [ ] 语义化标签使用正确，通过初步 A11y 检查。

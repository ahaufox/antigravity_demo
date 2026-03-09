---
description: UI 设计感性工作流 - 专注于视觉美学、情感共鸣与动态交互
role: Visual Designer / UI Artist
---

# 感性设计工作流

> **核心隐喻**: "皮肤与灵魂" (The Skin & Soul)
> **目标**: 赋予结构美感、情感张力、品牌识别度与细腻的交互体验。
> **输入**: 已完成逻辑验证的 "理性结构代码" (Rational Skeleton)。
> **输出**: 视觉完成度极高、带有微交互动画的最终 UI 组件。

---

## 步骤 1: 视觉基调确立 (Tone & Atmosphere)

根据内容属性确定情感基调。

1. **主题应用**:
   - **MindSeed 经典**: 使用 `bg-paper` (#F9F7F2) + `text-ink` (#1A1C1E) + `accent-red` (#A34E36)。
   - **Golden Dark (Topic 7)**: 使用 `bg-[#2C2C2E]` + `text-white/90` + `border-white/10`。
   - **Deep Decoding (深度解码)**: 使用半透明毛玻璃 (`backdrop-blur-lg`) 与渐变光晕。

2. **字体排印 (Typography)**:
   - **中文字体**: 优先使用 `PingFang SC` (苹方), `system-ui` 回退。
   - **层级 (Hierarchy)**:
     - 标题: `font-bold tracking-tight text-3xl` (紧凑字间距增加力量感)。
     - 正文: `leading-relaxed text-base` (宽松行高增加阅读舒适度)。
     - 说明: `text-sm text-muted-foreground` (弱化视觉干扰)。

## 步骤 2: 色彩注入 (Color Injection)

使用 Tailwind 工具类与 CSS 变量进行 "上色"。

1. **功能色 (Semantic Colors)**:
   - 使用 Shadcn 变量: `bg-primary`, `text-destructive`, `border-input`。
   - **禁止** 直接使用 Hex 颜色 (特殊设计稿除外)，确保 Dark Mode 自动适配。

2. **情感色 (Emotional Colors)**:
   - **Warmth (温暖)**: `amber-50`, `orange-100` (用于提示框、成功态)。
   - **Danger (警示)**: `red-50`, `rose-600` (用于错误、删除)。
   - **Magic (魔法/AI)**: `indigo-500`, `purple-600` (用于 AI 生成内容)。

## 步骤 3: 质感与细节 (Texture & Detail)

消除 "塑料感"，增加 "实体感"。

1. **阴影与深度 (Shadow & Depth)**:
   - 使用 `shadow-sm`, `shadow-md`, `shadow-lg` 构建层级。
   - 悬浮态: `hover:shadow-xl hover:-translate-y-1 transition-all duration-300` (经典的 "浮起" 效果)。

2. **圆角与边框 (Radius & Border)**:
   - 统一使用 `rounded-lg` 或 `var(--radius)`。
   - 微妙边框: `border border-slate-200/60` (增加精致感)。

3. **背景纹理**:
   - 在 `bg-paper` 上叠加噪点纹理 (Noise Texture) 或轻微渐变，避免纯色死板。
   - **标准应用**: 查阅 [审美增强规范](../../heuristics/aesthetic-toolkit.md) 获取标准的自然颗粒与有机纤维混合代码。

## 步骤 4: 动态交互 (Motion & Life)

让界面 "活" 起来。

1. **微交互 (Micro-interactions)**:
   - **按钮**: `active:scale-95` (按压回弹)。
   - **链接**: `hover:underline underline-offset-4 decoration-2`。
   - **卡片**: `group-hover:opacity-100` (渐显操作按钮)。

2. **转场动画 (Transitions)**:
   - 使用 `Animate.css` 或 `Framer Motion` (仅在 React 组件中)。
   - 简单过渡: `transition-colors duration-200 ease-in-out`。

3. **加载态优化**:
   - 使用 `animate-pulse` 制作骨架屏 (Skeleton)。
   - 避免生硬的 "闪烁" (Layout Shift)。

## 步骤 5: 文案润色 (Copywriting Soul)

1. **修复话术 (Connection Scripts)**:
   - 错误提示: 避免 "Invalid Input"，使用 "似乎有点小问题，请检查一下..."。
   - 空状态: 避免 "No Data"，使用 "这里空空如也，也许可以开始第一次..."。

2. **微文案 (Micro-copy)**:
   - 按钮文案: 避免 "Submit"，使用 "开始探索" / "确认发送"。

---

## ✅ 感性阶段验收标准

- [ ] 视觉层级清晰，重点突出 (通过 "眯眼测试")。
- [ ] 配色符合 MindSeed 品牌或特定 Topic 规范。
- [ ] Dark Mode 下无刺眼对比或不可读文字。
- [ ] 所有可交互元素均有 Hover/Focus/Active 状态。
- [ ] 动画流畅 (60fps)，无卡顿，且不过度干扰。
- [ ] 文案具有 "人味"，符合 "MindSeed 精神高潮" 调性。

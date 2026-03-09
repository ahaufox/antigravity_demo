---
description: UI 设计整合工作流 - 专注于理性与感性的融合、冲突解决与最终交付
role: Product Owner / QA Engineer
---

# 整合工作流

> **核心隐喻**: "赋予生命" (Bring to Life)
> **目标**: 将 "骨架" (Rational) 与 "皮囊" (Emotional) 完美融合，解决冲突，确保交付质量。
> **输入**: "理性结构代码" + "感性视觉样式"。
> **输出**: 已通过测试、性能优异、可发布的生产级代码。

---

## 步骤 1: 代码融合 (Merge & Integrate)

将两个独立开发的流合并。

1. **结构调整**:
   - 将 Tailwind 工具类 (Emotional) 应用到 HTML 标签 (Rational)。
   - 使用 `cn()` (clsx + tailwind-merge) 处理动态样式冲突。
   - **检查点**: 确保样式类名不会覆盖原有的布局逻辑 (如 `flex` 方向错乱)。

2. **逻辑回填**:
   - 将 React Hooks (Rational) 挂载到已美化的组件上。
   - 绑定事件处理函数 (`onClick`, `onChange`)。
   - **检查点**: 确保美化后的按钮仍然能够触发点击事件 (没有被绝对定位元素遮挡)。

## 步骤 2: 冲突解决 (Conflict Resolution)

解决 "理性" 与 "感性" 的矛盾。

1. **可用性 vs 美观**:
   - **问题**: 文字颜色太淡 (美观) 导致难以阅读 (不可用)。
   - **解决**: 调整对比度，或增加背景遮罩。优先保证可读性。

2. **性能 vs 动效**:
   - **问题**: 过多的 CSS 阴影或 Blur 导致页面卡顿。
   - **解决**: 简化效果，或使用 `will-change` 优化，或在低性能设备上降级。

3. **布局 vs 内容**:
   - **问题**: 真实数据 (长标题) 撑破了设计好的卡片高度。
   - **解决**: 使用 `line-clamp` 截断，或调整 Flex/Grid 布局自适应。

## 步骤 3: 全面验证 (Verification)

像 "体检" 一样检查整合后的系统。

1. **响应式检查 (Mobile First)**:
   - 在 Chrome DevTools 中模拟 iPhone SE, iPhone 14 Pro, iPad, Desktop。
   - **重点**: 确保移动端无横向滚动条，点击区域足够大 (44px+)。

2. **自动化测试 (Playwright)**:
   - 编写 E2E 测试脚本，模拟用户完整操作路径。
   - 截图比对 (Visual Regression Testing) 确保样式无意外变更。

   ```typescript
   // tests/ui/mindseed-card.spec.ts
   test('Card should display content and react to hover', async ({ page }) => {
     await page.goto('/prototype/card');
     const card = page.locator('.mindseed-card');
     await expect(card).toBeVisible();
     await card.hover();
     await expect(card).toHaveCSS('transform', /matrix/); // 检查动画
   });
   ```

3. **性能基准 (Lighthouse)**:
   - 运行 Lighthouse 检查。
   - 目标: Performance > 90, Accessibility > 95。

## 步骤 4: 最终打磨 (Final Polish)

1. **一致性检查**:
   - 检查 Margins/Paddings 是否遵循 4px/8px 网格系统。
   - 检查字体大小是否统一。

2. **代码清理**:
   - 移除 `console.log` 和调试用的边框 (`border-red-500`)。
   - 提取重复的样式为 Tailwind Components (`@apply`) 或 React 组件。

---

## ✅ 最终交付标准

- [ ] 所有功能逻辑正常 (Rational Pass)。
- [ ] 视觉效果符合设计预期 (Emotional Pass)。
- [ ] 移动端与桌面端均适配完美。
- [ ] Lighthouse 评分达标 (90+)。
- [ ] 代码通过 ESLint / Prettier 检查。
- [ ] 无明显的控制台报错 (Console Errors)。

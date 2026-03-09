---
description: 小红书爆款笔记生成工作流。基于调研报告或关键词，生成符合小红书调性（封面、标题党、情绪价值）的脚本。
---

# 📕 小红书笔记生成工作流

**目标**: 产出“直接可拍/可发”的小红书笔记脚本。

## 1. 上下文获取
- 如果用户指定了某个文件（如 `02-Market-Reviews/xxx.md`），先用 `view_file` 读取。
- 如果没有，询问核心主题和目标人群。

## 2. 爆款策略构思
- **Heuristic Check**: 调用 [Creative Paradox](../../heuristics/creative_paradox.md) 进行审美审视。
    - *Check*: 标题是否包含悖论？(e.g. "Price vs Value")
    - *Check*: 是否通过"面具"说真话？

- **Heuristic Check**: 调用 [Maker Philosophy](../../heuristics/maker_philosophy.md) (Paul Graham)
    - *Check*: 这篇内容是否属于 "Do things that don't scale" (手动深度连接用户)？
    - *Check*: 是否在解决"未来缺失"的问题？

- **封面策略**: 设计 3 个不同风格的封面文案（痛点直击型 / 结果展示型 / 悬念猎奇型）。
- **标题策略**: 必须包含情绪词、关键词、并在 20 字以内。提供 5 个备选。
- **正文结构**: 
    - **Hook (前 3 秒)**: 也就是“黄金 3 秒”，必须甚至反直觉或强共鸣。
    - **Body (干货/情绪)**: 
        - 这种时候不要说教，要说“我发现...”或者“血泪教训...”。
        - 多用 Emoji 🌈✨💡。
        - 也就是“口语化”重写。
    - **CTA (互动)**: 骗赞、骗收藏、骗评论。

## 3. 产出脚本
在 `03-Channel-Strategy/` 下创建一个新的 markdown 文件。
- **命名规范**: `YYYYMMDD-{Topic}-xhs-script.md`
- **内容模板**:

```markdown
# 📕 小红书脚本：{Topic}

## 🎨 视觉方案 (CoverOptions)
1. **场景版**: (描述画面) + 文案：“...”
2. **文字版**: 纯底色 + 粗大字体：“...”
3. **对比版**: Before/After + 文案：“...”

## 🏆 标题备选 (TitleOptions)
1. ...
2. ...
3. ...
4. ...
5. ...

## 📝 正文脚本 (Copywriting)

(Hook)
...

(Body)
...
...

(CTA)
...

## 🏷 Tags
#... #...
```

## 4. 总结
- 询问用户是否生成图片素材（如果需要，可以调用 `generate_image` 工具）。

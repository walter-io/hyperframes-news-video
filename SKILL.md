---
name: hyperframes-news-video
description: 用 HyperFrames 把带旁白的视频做成科技新闻风格动画，或反推现有视频的动效设计并复用到新视频。适用于“把某段视频做成动效版”“反推视频的 HyperFrames 动效设计”“按反推结果给新视频做动画”“先出 HTML 预览图确认后再渲染 MP4”这类需求。
---

# HyperFrames 新闻视频动效

把带旁白的视频做成干净、编辑感的“科技新闻”动画；或者反推现有视频的动效设计并复用。流程固定为：先出 HTML 预览图，等用户确认，再渲染视频。

## 一句话流程

检查视频 → 提取音频 → 转写（带时间戳）→ 生成字幕/文案时间轴 → 编写动画 → 校验 → 交付预览图 → 用户确认 → 渲染视频

可选前置步骤：有参考视频时先反推；写动画前先确认输出模式。

## 什么时候用

- 反推参考视频的 HyperFrames 动效设计。
- 把带旁白的视频做成动画讲解。
- 用已反推的设计给新视频做动效。
- 先看 HTML 预览图，确认后再渲染 MP4。

## 输出模式

开工前确认用哪一种，默认动效解说版：

- 动效解说版：画面全是动画，只保留旁白。
- 视频背景 + 新闻叠加版：保留原视频，叠加新闻风 UI。
- 混合版：原视频与动画场景穿插。

完整说明见 [references/output-modes.md](references/output-modes.md)。

## 主流程

1. 检查素材：`ffprobe` 看分辨率/帧率/时长；中文路径先复制到纯英文路径。
2. 确认输出模式。
3. 转写旁白：得到带时间戳的逐句文本，旁白就是场景时间轴。
4. 有参考视频时先反推，产出 `reverse-design.md`。
5. 写 HTML 前先写 `DESIGN.md`。
6. 初始化工程并编写 `index.html`。
7. 校验：`lint` 0 错误、`inspect` 0 问题。
8. 预览门禁：用 `snapshot` 出预览图，用户确认前不渲染。
9. 迭代：布局问题用像素/OCR 量化修复，重新出预览。
10. 渲染：`render` 出 MP4，再用 `ffprobe` 和抽帧 OCR 复核。

每一步的具体命令和规范见 [references/hyperframes-workflow.md](references/hyperframes-workflow.md)。

## 硬性规则

- 不硬切：场景转场必须经过短暂空画布。
- 每个元素都要入场动画，不允许完整直接出现。
- 最后一个场景之前不允许退场，转场负责退场。
- 禁止无限循环动画和异步时间线。
- 先预览，后渲染，不能跳过确认门禁。

## 参考文档

- [output-modes.md](references/output-modes.md)：三种输出模式及实现方式。
- [design-system.md](references/design-system.md)：配色、字体、版式、动效、转场。
- [hyperframes-workflow.md](references/hyperframes-workflow.md)：CLI 命令、合成规范、校验与渲染。
- [reverse-engineering.md](references/reverse-engineering.md)：帧、OCR、颜色、运动分析步骤。
- [assets/template/index.html](assets/template/index.html)：可直接改写的起步模板。

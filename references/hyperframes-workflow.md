# HyperFrames 工作流

## CLI 命令

推荐用法：

```bash
npx hyperframes init <project> --example blank --audio narration.wav --skip-transcribe --non-interactive --resolution landscape
npx hyperframes lint
npx hyperframes inspect --json --samples 15
npx hyperframes snapshot --output previews --at 2.5,7.5,16,23 --no-end
npx hyperframes render --quality standard --output renders/final.mp4
```

如果 `npx` 卡住，直接用已安装包入口：

```bash
node "<npm-cache>/_npx/<hash>/node_modules/hyperframes/dist/cli.js" <命令>
```

自动化运行时可设置 `HYPERFRAMES_SKIP_SKILLS=1`。

## 工程结构

```
project/
  index.html          # 根合成
  DESIGN.md           # 写代码前必须先有
  source_audio.wav    # 旁白
  hyperframes.json
  renders/
  previews/
```

## 合成规范

- 根节点要有 `data-composition-id`、`data-start="0"`、`data-duration`、`data-width`、`data-height`。
- 第 2 个及以后的场景初始 `opacity: 0`，由 GSAP 显示。
- 只用一条时间线：`const tl = gsap.timeline({ paused: true }); window.__timelines["<id>"] = tl;`。
- 音频是独立的 `<audio data-start="0" data-duration="..." data-track-index="..." src="...">`。
- 按时出现的覆盖层（字幕等）需要 `class="clip"`，并带 `data-start`、`data-duration`、`data-track-index`。
- 场景淡出后要加 `tl.set(场景, { visibility: "hidden" }, 结束时间)`。

## 校验门禁

- `lint`：错误数必须为 0。常见修复：加 `clip` 类、加 `@font-face src: local(...)`、加 visibility 清理、去掉 `repeat:-1`、改用 `Math.floor`。
- `inspect`：预览前必须 0 问题，它负责查文字溢出和重叠。
- `snapshot`：生成 PNG 接触表给用户。**用户确认前不要渲染视频。**

## 渲染

- 迭代用 `--quality draft`，评审用 `standard`，交付用 `high`。
- 默认输出 `renders/<name>_<timestamp>.mp4`；用 `--output` 指定稳定文件名。
- 渲染后用 `ffprobe` 验证，并抽 2-3 帧 OCR 复核。

## 用测量代替猜

用户说间距不对时，量化检查：

- 用连通域找白色卡片矩形。
- 用 OCR 文本框确定元素边界。
- 采样面板/字幕区域像素，确认不该存在的地方是空的。

不要在没有证据的情况下回答“看起来没问题”。

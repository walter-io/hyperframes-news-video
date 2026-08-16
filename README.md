# HyperFrames 新闻视频动效 Skill

这是一个开源 Codex skill：把带旁白的视频做成干净、编辑感的“科技新闻”动效视频，也可以反推某个视频的 HyperFrames 动效设计并复用到新视频。

核心规则：**先出 HTML 预览图，等你确认，再渲染 MP4**。

## 三种输出模式

- **动效解说版**：画面全是动画，只保留旁白。
- **视频背景 + 新闻叠加版**：保留原视频画面，叠加眉题、标题卡、数字卡等新闻风 UI。
- **混合版**：演示/实拍保留原视频，定义/数据/总结用动画。

详细说明见 [references/output-modes.md](references/output-modes.md)。

## 安装

### 1. 安装 skill

把整个 `hyperframes-news-video` 文件夹复制到：

```text
~/.codex/skills/hyperframes-news-video
```

Windows 通常是：

```text
C:\Users\<你的用户名>\.codex\skills\hyperframes-news-video
```

### 2. 安装依赖

需要 Node.js >= 22、FFmpeg 和以下 Python 包：

```bash
pip install numpy Pillow opencv-python-headless rapidocr-onnxruntime faster-whisper
```

## 首次使用提醒

第一次运行会比较慢，因为要下载依赖和模型，不是卡死：

- 首次运行 `npx hyperframes` 会下载 HyperFrames 工具包，可能需要几分钟。
- 首次转写旁白会下载 Whisper 语音模型。
- 首次做 OCR 会下载 RapidOCR 模型。
- 首次 `snapshot` / `render` 会初始化 Chrome 和字体缓存。
- 网络较慢时耗时更明显，请耐心等待。

如果长时间没有进度，先检查环境：

```bash
npx hyperframes doctor
```

之后再次使用会走缓存，速度会明显变快。

## 怎么用

### 方式一：让 Codex 帮你做（推荐）

准备一个带旁白的视频，然后直接对 Codex 说需求。下面三条是最常用的说法：

```text
把 视频.mp4 做成动效解说版，先出预览图
```

```text
把 视频.mp4 做成视频背景 + 新闻叠加版，先出预览图
```

```text
把 视频.mp4 做成混合版：录屏和实拍保留原视频，定义和数据部分用动画
```

Codex 会按这个流程走：

1. 检查视频文件，提取音频，转写带时间戳的旁白。
2. 生成设计文档和动画工程。
3. 跑校验，输出 HTML 预览图给你确认。
4. 你确认后，再渲染最终 MP4。

### 方式二：手动跑命令

如果你不用 Codex，也可以按下面的命令自己跑。

先分析源视频：

```bash
python scripts/analyze_source.py 视频.mp4 analysis --language zh
```

然后初始化 HyperFrames 工程：

```bash
npx hyperframes init my-video \
  --example blank \
  --audio analysis/audio.wav \
  --skip-transcribe \
  --non-interactive \
  --resolution landscape
```

把 [assets/template/index.html](assets/template/index.html) 的内容改成你的场景，再校验：

```bash
npx hyperframes lint
npx hyperframes inspect --json --samples 15
```

出预览图（这一步之后要停下来确认）：

```bash
npx hyperframes snapshot --output previews --at 2.5,7.5,16,23 --no-end
```

确认预览没问题后渲染视频：

```bash
npx hyperframes render --quality standard --output renders/final.mp4
```

## 示例视频

`示例.mp4` 是本 skill 自带的示例素材：23.8 秒、1920x1080、30fps，带旁白，可以直接用来测试整套流程。

发布到 GitHub 后，可以在仓库页直接播放：

![示例视频](https://raw.githubusercontent.com/walter-io/hyperframes-news-video/main/示例.mp4)

如果上方无法播放，请把 `示例.mp4` 下载到本地后使用。

试用反推分析：

```bash
python scripts/analyze_source.py 示例.mp4 analysis --language zh
```

也可以直接对 Codex 说：

```text
用 示例.mp4 做一版动效解说版，先出预览图
```

## 目录结构

```
SKILL.md                      # 给 Codex 看的主流程
agents/openai.yaml            # UI 元数据
references/                   # 模式、设计系统、反推、CLI 工作流
scripts/analyze_source.py     # 视频自动分析脚本
assets/template/              # 可复用的 HyperFrames 起步模板
示例.mp4                      # 示例素材
微信二维码.jpg                 # 联系方式
```

## 联系我

对 skill 有想法、遇到问题，或者想一起做视频，都可以加我微信：

<img src="微信二维码.jpg" alt="微信二维码" width="200" />

## 许可证

MIT

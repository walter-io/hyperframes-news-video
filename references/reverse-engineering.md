# 反推 HyperFrames 视频动效

目标：产出一份设计规格（`reverse-design.md`），让另一个 agent 能照着重建。

## 1. 媒体信息

```bash
ffprobe -v error -show_entries format=duration,size,bit_rate \
  -show_entries stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_frames \
  -of default=noprint_wrappers=1 input.mp4
```

记录分辨率、帧率、时长、编码。路径含非 ASCII 字符时，先把文件复制到纯英文路径；有些工具会因编码问题打不开。

## 2. 转写旁白

抽音频：

```bash
ffmpeg -y -loglevel error -i input.mp4 -vn -ac 1 -ar 16000 audio.wav
```

带时间戳转写：

```python
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("audio.wav", language="zh", vad_filter=True)
for s in segments:
    print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text}")
```

旁白就是场景时间轴，每个叙事节拍对应一个场景或一个元素入场。

## 3. 抽帧和 OCR

每秒抽一帧：

```bash
ffmpeg -y -loglevel error -i input.mp4 -vf "fps=1,scale=640:-2" frames/f_%03d.png
```

用 RapidOCR 逐帧识别文字和位置：

```python
from rapidocr_onnxruntime import RapidOCR
engine = RapidOCR()
result, _ = engine("frames/f_001.png")
for box, text, score in result:
    print(score, text, box)
```

跟踪文字框随时间的位置变化，可以判断入场方式（淡入/上滑/缩放）、字幕和场景切换。

## 4. 颜色和版式

- 直接采样背景、正文、面板、强调色的像素。
- 检测高饱和强调色（例如橙色 `r>210, 90<g<200, b<90`），每秒输出包围盒。这能看出哪些词被高亮。
- 用 `cv2.connectedComponentsWithStats` 找出白色卡片矩形，量出卡片之间的间距。

## 5. 动效和转场

- 按 30fps 计算相邻帧平均绝对差：接近 0 的区间表示静止场景，跳变代表转场或字幕切换。
- 在场景边界按 10fps 采样，和旧/新场景稳定帧做相关性对比，判断是否交叉淡化。
- 按 5fps 跟踪深色文字块，测量元素速度与方向。

## 6. 输出规格

`reverse-design.md` 需要包含：

- 画布/帧率/时长。
- 配色（采样色值和角色）。
- 字体和字号。
- 固定层（品牌、侧图、字幕、水印）以及是否动效。
- 逐场景时间轴：开始/结束、眉题、标题、元素、入场时间。
- 每个边界的转场类型和时长。
- 字幕系统与逐句时间。
- 动效规则和强调色规则。

之后按 `SKILL.md` 的主流程重建。

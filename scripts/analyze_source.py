"""分析带旁白的视频，供 HyperFrames 反推使用。

用法：
    python analyze_source.py input.mp4 [output_dir] [--language zh]

输出到 output_dir：
    transcript.json         # 逐句旁白时间轴
    ocr.json                # 每秒 OCR 文本和位置
    colors.json             # 每秒强调色信息
    motion.json             # 帧差时间线和转场候选
    reverse-design.md       # 给 agent 扩展的设计初稿
"""

import argparse
import json
import os
import subprocess
import sys

try:
    import cv2
    import numpy as np
    from PIL import Image
    from rapidocr_onnxruntime import RapidOCR
    from faster_whisper import WhisperModel
except ImportError as exc:  # pragma: no cover
    sys.exit(
        "Missing dependency. Install with: "
        "pip install opencv-python-headless pillow numpy rapidocr-onnxruntime faster-whisper"
    )


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, check=False, **kwargs)


def probe(path):
    p = run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size,bit_rate",
            "-show_entries", "stream=index,codec_name,codec_type,width,height,r_frame_rate,nb_frames",
            "-of", "json", path,
        ]
    )
    return json.loads(p.stdout.decode("utf-8", "replace"))


def extract_audio(path, out_wav):
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vn", "-ac", "1", "-ar", "16000", out_wav])


def transcribe(wav, language):
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, info = model.transcribe(wav, language=language, vad_filter=True)
    rows = []
    for seg in segments:
        rows.append({"start": round(float(seg.start), 2), "end": round(float(seg.end), 2), "text": seg.text.strip()})
    return info.language, info.duration, rows


def extract_frames(path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-vf", "fps=1,scale=640:-2", os.path.join(out_dir, "f_%03d.png")])
    return sorted(f for f in os.listdir(out_dir) if f.endswith(".png"))


def analyze_frames(frames, out_dir):
    engine = RapidOCR()
    ocr = {}
    colors = {}
    prev = None
    motion = []
    for i, fn in enumerate(frames):
        t = i
        img_path = os.path.join(out_dir, fn)
        im = np.asarray(Image.open(img_path).convert("RGB")).astype(int)
        gray = np.asarray(Image.open(img_path).convert("L")).astype(np.float32)

        if prev is not None:
            motion.append({"t": t, "frame_diff": round(float(np.abs(gray - prev).mean()), 2)})
        prev = gray

        res, _ = engine(img_path)
        items = []
        if res:
            for box, text, score in res:
                xs = [p[0] for p in box]
                ys = [p[1] for p in box]
                items.append({
                    "text": text,
                    "score": round(float(score), 3),
                    "box": [int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))],
                })
        ocr[str(t)] = items

        r, g, b = im[..., 0], im[..., 1], im[..., 2]
        accent = (r > 210) & (g > 90) & (g < 200) & (b < 90)
        if accent.sum() > 100:
            ys, xs = np.nonzero(accent)
            colors[str(t)] = {
                "accent_box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                "accent_pixels": int(accent.sum()),
            }
        else:
            colors[str(t)] = {"accent_box": None, "accent_pixels": 0}

    return ocr, colors, motion


def write_seed(meta, transcript, motion, out_md):
    lines = [
        "# 反推设计初稿",
        "",
        "## 媒体信息",
        f"- 分辨率/帧率/时长：{meta.get('canvas', '未知')}",
        "",
        "## 旁白时间轴",
        "",
        "| 开始 | 结束 | 文本 |",
        "| --- | --- | --- |",
    ]
    for row in transcript:
        lines.append(f"| {row['start']:.2f} | {row['end']:.2f} | {row['text']} |")
    peaks = sorted(motion, key=lambda x: -x["frame_diff"])[:8]
    lines += ["", "## 帧变化较大的时间点（转场/字幕候选）", ""]
    for p in peaks:
        lines.append(f"- 第 {p['t']} 秒，帧差 {p['frame_diff']}")
    lines += [
        "",
        "## 下一步",
        "",
        "- 查看 `ocr.json`，梳理场景和文字位置。",
        "- 查看 `colors.json`，确认强调色规则。",
        "- 用像素分析量卡片间距和转场。",
        "- 补全完整的 `reverse-design.md` 设计规格。",
    ]
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output", nargs="?", default="analysis")
    parser.add_argument("--language", default="zh")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    meta = probe(args.input)
    streams = meta.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    meta["canvas"] = f"{video.get('width')}x{video.get('height')} @ {video.get('r_frame_rate')}"

    wav = os.path.join(args.output, "audio.wav")
    extract_audio(args.input, wav)
    lang, duration, transcript = transcribe(wav, args.language)
    with open(os.path.join(args.output, "transcript.json"), "w", encoding="utf-8") as f:
        json.dump({"language": lang, "duration": duration, "segments": transcript}, f, ensure_ascii=False, indent=1)

    frames = extract_frames(args.input, os.path.join(args.output, "frames"))
    ocr, colors, motion = analyze_frames(frames, os.path.join(args.output, "frames"))
    with open(os.path.join(args.output, "ocr.json"), "w", encoding="utf-8") as f:
        json.dump(ocr, f, ensure_ascii=False)
    with open(os.path.join(args.output, "colors.json"), "w", encoding="utf-8") as f:
        json.dump(colors, f, ensure_ascii=False)
    with open(os.path.join(args.output, "motion.json"), "w", encoding="utf-8") as f:
        json.dump(motion, f, ensure_ascii=False)

    write_seed(meta, transcript, motion, os.path.join(args.output, "reverse-design.md"))
    print(f"已分析 {len(frames)} 帧。设计初稿：{os.path.join(args.output, 'reverse-design.md')}")


if __name__ == "__main__":
    main()

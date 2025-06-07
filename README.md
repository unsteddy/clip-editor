# 🎮 Clip Editor

**Clip Editor** is a microservice in the automated **clip farm** pipeline. It transforms raw downloaded clips into
polished, platform-ready vertical videos for YouTube Shorts, TikTok, and similar platforms.

This includes smart layout formatting, streamer-focused subtitle rendering, and AI-powered Chinese subtitle translation
and replacement for TikTok content.

---

## ✨ Features

* ✅ Converts any input clip to **vertical 1080x1920 format**
* 🎥 Preserves aspect ratio with centered top/bottom padding
* 🡩‍💬 Dual-layer subtitle rendering:

    * Bottom: **Streamer speech**
    * Top: **Other speakers**
* 🇨🇳➜🇺🇸 Chinese subtitle translation pipeline (TikTok):

    * Detects Chinese text frame-by-frame
    * Tracks subtitle regions over time
    * Blurs original subtitles using AI
    * Overlays translated English text in matching style
* 🧠 Frame-level subtitle caching to reduce OCR noise and boost speed
* ⚙️ Modular and composable: plug in editing, detection, and overlay components
* 🖼️ Optional Twitch logo overlay (configurable)
* ✨ Powered by `ffmpeg`, PaddleOCR, OpenCV, and custom pipelines

---

## 🧠 Pipeline Overview

### Twitch & Shorts Workflow

1. Resize input to 1080px width, preserve aspect ratio
2. Pad top and bottom to fill 1920px height
3. Render subtitles (`.srt`) by speaker role:

    * Bottom for streamer
    * Top for others
4. Export with `libx264` codec

### TikTok Workflow

1. Detect Chinese subtitles in each frame (OCR + region tracking)
2. Blur detected subtitle areas (AI inpainting)
3. Translate Chinese to English (WIP)
4. Overlay new English subtitles in same position, matching visual style
5. Export final vertical video

---

## 🧪 Example Usage

### 🔧 Setup

1. Install system dependencies:

    * [`ffmpeg`](https://ffmpeg.org/)
    * [`tesseract-ocr`](https://github.com/tesseract-ocr/tesseract) with `chi_sim` language pack

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Download model weights or OCR configs:

```bash
python setup_models.py
```

---

### 🧵 Basic Editing Example

```python
from editor.ffmpeg_wrapper import FFmpegStacker

editor = FFmpegStacker(
    input_path="assets/sample_clip.mp4",
    output_path="output/vertical_clip.mp4",
    streamer_name="example_streamer"
)

editor.add_subtitle_layers("output/streamer.srt", "output/others.srt")
editor.run()
```

---

### 🌏 TikTok Subtitle Processor

```bash
python main.py
```

This will:

* Format the video to Shorts dimensions
* Detect + track Chinese subtitle regions
* Blur original subtitles
* (WIP) Translate to English and overlay in place
* Save output to `assets/sample_output.mp4`

---

## 📁 Project Structure

```
clip-editor/
│
├── main.py                          # Entry point for TikTok subtitle pipeline
├── subtitle_processing/
│   ├── subtitle_detector.py        # OCR-based detection of Chinese text
│   ├── subtitle_tracker.py         # Tracks subtitles across frames for caching
│   └── subtitle_pipeline.py        # Orchestrates frame-by-frame logic
│
├── editor/
│   ├── ffmpeg_wrapper.py           # Core layout + subtitle rendering
│   ├── blur.py                     # AI blurring of detected regions
│   ├── overlay.py                  # Overlays translated subtitles
│   └── editor_pipeline.py          # (Legacy) Combined editing pipeline
│
├── assets/
│   └── twitch_logo_40px.png        # Optional Twitch logo
├── output/                         # Output folder for rendered videos
├── examples/
│   └── run_clip_edit.py            # Minimal usage example
```

---

## 📦 Dependencies

**Core:**

* `ffmpeg` (system)
* Python 3.8+
* `opencv-python`
* `pytesseract` + Tesseract (`chi_sim`)
* `paddleocr` (planned)
* `whisper`, `resemblyzer` (for speaker diarization)

**Python packages:**

```txt
python-dotenv
requests
streamlink
sqlalchemy
pillow
whisper
resemblyzer
opencv-python
pytesseract
```

---

## 🧽 Roadmap

* [ ] Background blur instead of black bars
* [ ] Style-mimicking English subtitles for TikTok
* [ ] Speaker diarization for automatic subtitle separation
* [ ] Facecam detection for layout-aware subtitle positioning
* [ ] Watermarking, branding, and overlay logo config
* [ ] Full batch mode for folder-based clip processing

---

## 🦼️ License

MIT

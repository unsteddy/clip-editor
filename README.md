# Clip Editor

This microservice is part of the automated clip farm project. It takes a downloaded clip and processes it for vertical
video platforms like YouTube Shorts or TikTok, applying optional subtitle layers and formatting the video to the correct
dimensions (1080x1920) while preserving the original aspect ratio.

---

## ✨ Features

* Converts any input clip to vertical format (1080x1920)
* Preserves the original aspect ratio by fitting to width
* Adds top and bottom padding (centered vertically)
* Supports dual-layer subtitle rendering:

    * Streamer's subtitles (bottom)
    * Others' subtitles (top)
* Configurable Twitch logo overlay (future use)
* Uses `ffmpeg` under the hood

---

## 🧠 How It Works

1. Input video is resized to fit width 1080px while preserving aspect ratio.
2. The resized video is padded to fit the full 1920px height.
3. Optional `.srt` subtitle files are rendered:

    * Streamer's subtitles are bottom-aligned.
    * Others' subtitles are top-aligned.
4. Final output is encoded using `libx264`.

---

## 📁 File Structure

```
editor/
│
├── ffmpeg_wrapper.py          # Core processing logic using FFmpeg
├── editor_pipeline.py         # Pipeline orchestration
├── examples/
│   └── run_clip_edit.py       # Example usage script
├── output/                    # Default output directory
├── assets/
│   └── twitch_logo_40px.png   # Logo (optional)
```

---

## 🧪 Example Usage

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

This will:

* Render both subtitle tracks
* Format the video to YouTube Shorts dimensions
* Output to `output/vertical_clip.mp4`

---

## 🔧 Dependencies

* Python 3.8+
* `ffmpeg` (must be installed and available on PATH)
* `subprocess` (standard lib)
* `python-dotenv`
* `requests`
* `streamlink`
* `sqlalchemy`
* `pillow`
* `whisper`
* `resemblyzer`
* `opencv-python`

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## 🚧 Future Plans

* Background blur instead of black padding
* Automatic logo and text overlays
* Subtitle translation and styling
* Watermarking and final branding

---

## 🦼️ License

MIT

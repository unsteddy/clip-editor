# 🎞️ Clip Editor

A Python microservice that performs automated video editing on downloaded clips for short-form platforms like YouTube
Shorts, TikTok, and Instagram Reels.

## Features (Implemented)

* Vertical conversion (9:16) from horizontal source
* Crops and stacks main content above reaction cam
* Maintains clean aspect ratios (no distortion)
* Tuned for 1920x1080 input resolution

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Make sure `ffmpeg` is installed system-wide:

```bash
ffmpeg -version
```

If not installed:

* macOS: `brew install ffmpeg`
* Ubuntu: `sudo apt install ffmpeg`
* Windows: download from [https://ffmpeg.org/](https://ffmpeg.org/)

## Example Workflow

To create a vertical 1080x1920 video from a 1920x1080 clip:

* The **top section** is a zoomed-out center crop of the main subject (wide frame)
* The **bottom section** is the bottom 300px of the video (reaction cam), zoomed to full width

### Python API Usage:

```python
from editor.ffmpeg_wrapper import stack_main_and_reaction

stack_main_and_reaction(
    input_path="assets/sample_clip.mp4",
    output_path="output/vertical_clip.mp4"
)
```

This will:

* Crop the top at `(x=448, width=1024)` to reveal more of the scene
* Crop the bottom at `(x=0, y=780, height=300)` for the facecam
* Zoom both sections to fit cleanly into a 1080x1920 vertical layout

## 🔧 Example Script

To test your pipeline, run:

```bash
python -m examples.run_clip_edit
```

This uses a sample input clip and writes the final result to `output/vertical_clip.mp4`. You can adjust coordinates
inside `ffmpeg_wrapper.py` for different crops.

---

## Output

Final output is a clean, high-quality vertical short clip with a full-width zoomed facecam and zoomed-out top frame,
ready for upload to Shorts, TikTok, or Reels.

---

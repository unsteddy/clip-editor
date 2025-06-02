# 🎞️ Clip Editor

A Python microservice that performs automated video editing on downloaded clips for short-form platforms like YouTube
Shorts, TikTok, and Instagram Reels.

## Features (Implemented)

* Vertical conversion (9:16) from horizontal source
* Crops and stacks main content above reaction cam
* Maintains clean aspect ratios (no distortion)
* Adds a minimal border and streamer name overlay to the reaction cam
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

* The **top section** is a cropped center portion of the main content, zoomed out slightly to show more context and
  scaled to 1080x1632
* The **bottom section** is the bottom 350px of the video (reaction cam), zoomed to full width while maintaining aspect
  ratio
* A white border is added around the reaction cam and the streamer's name is displayed in the bottom right corner

### Python API Usage:

```python
from editor.ffmpeg_wrapper import stack_main_and_reaction

stack_main_and_reaction(
    input_path="assets/sample_clip.mp4",
    output_path="output/vertical_clip.mp4",
    streamer_name="T1 Faker"
)
```

This will:

* Crop the top at `(x=448, width=1024)` to reveal more of the scene
* Crop the bottom at `(x=0, y=730, height=350)` for the facecam
* Zoom both sections to fit cleanly into a 1080x1920 vertical layout
* Add a labeled border to the facecam with the streamer's name

## 🔧 Example Script

To test your pipeline, run:

```bash
python examples/run_clip_edit.py
```

This uses a sample input clip and writes the final result to `output/vertical_clip.mp4`. You can adjust coordinates and
the streamer's name inside `ffmpeg_wrapper.py`.

---

## Output

Final output is a clean, high-quality vertical short clip with a full-width zoomed facecam, zoomed-out top frame, and
styled reaction box, ready for upload to Shorts, TikTok, or Reels.

---

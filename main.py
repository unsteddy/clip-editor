import cv2
import os
import logging
from subtitle_processing.subtitle_detector import detect_chinese_subtitles
from subtitle_processing.subtitle_tracker import SubtitleTracker
from editor.blur import blur_regions
from editor.overlay import overlay_translations
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Example placeholder translation map
translation_map = {
    "你好": "Hello",
    "谢谢": "Thank you",
    # Add more mappings as needed
}


def process_video(input_path, output_path):
    logger.info(f"Opening video: {input_path}")
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    tracker = SubtitleTracker()
    frame_count = 0

    with tqdm(total=total_frames, desc="Processing Frames", unit="frame") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            regions = detect_chinese_subtitles(frame)
            tracked_regions = tracker.update(regions)
            blurred = blur_regions(frame, tracked_regions)
            final = overlay_translations(blurred, tracked_regions, translation_map)

            out.write(final)
            pbar.update(1)

    cap.release()
    out.release()
    logger.info(f"Saved processed video to {output_path}")


if __name__ == "__main__":
    sample_input = os.path.join("assets", "sample_clip.mp4")
    sample_output = os.path.join("assets", "sample_output.mp4")
    process_video(sample_input, sample_output)

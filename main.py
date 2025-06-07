import cv2
from subtitle_processing.subtitle_pipeline import SubtitlePipeline
import time


def main():
    video_path = "assets/sample_clip.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("❌ Error: Could not open video.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"🎞 Total frames: {total_frames}")

    pipeline = SubtitlePipeline()
    frame_idx = 0
    start_time = time.time()

    while cap.isOpened():
        if frame_idx == 10:
            break

        ret, frame = cap.read()
        if not ret:
            break

        tracked_subtitles = pipeline.process_frame(frame)

        print(f"🧠 Frame {frame_idx} subtitles:")
        for sub in tracked_subtitles:
            text = sub['text']
            bbox = sub['bbox']
            sid = sub['id']
            print(f"  ▶ ID {sid}: '{text}' at {bbox}")

            # Optional: Draw box
            x, y, w, h = bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
            cv2.putText(frame, f"ID {sid}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 255), 1, cv2.LINE_AA)

        frame_idx += 1

    elapsed = time.time() - start_time
    print(f"✅ Done. Processed {frame_idx} frames in {elapsed:.2f}s ({frame_idx / elapsed:.2f} FPS)")

    cap.release()


if __name__ == "__main__":
    main()

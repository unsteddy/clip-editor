import cv2
from subtitle_processing.subtitle_detector import SubtitleDetector
from subtitle_processing.subtitle_tracker import SubtitleTracker


def main():
    video_path = "assets/sample_clip.mp4"
    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to read the first frame of the video.")
        return

    detector = SubtitleDetector()
    tracker = SubtitleTracker()

    # Detect subtitles in first frame
    detected_subs = detector.detect(frame)
    print("🔍 Detected subtitles:", detected_subs)

    # Track detected subtitles
    tracked_subs = tracker.update(detected_subs)
    print("📌 Tracked subtitles:", tracked_subs)

    # Draw tracked subtitles
    for sub in tracked_subs:
        x, y, w, h = sub["bbox"]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"#{sub['id']}: {sub['text']}", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Save the frame instead of displaying it
    cv2.imwrite("tracked_subtitles_first_frame.png", frame)
    print("✅ Frame saved as 'tracked_subtitles_first_frame.png'")


if __name__ == "__main__":
    main()

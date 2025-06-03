import cv2
import numpy as np
from collections import defaultdict
from editor.facecam_detector import detect_facecam_region


def detect_streamer_speaker(video_path: str, diarized_segments: list) -> str:
    facecam_box = detect_facecam_region(video_path)
    if not facecam_box:
        print("[WARN] No facecam box detected, cannot match streamer.")
        return None

    x, y, w, h = facecam_box
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Build per-second presence timeline of face activity
    face_presence = defaultdict(int)
    frame_idx = 0

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = frame_idx / fps
        frame_idx += 1

        facecam_region = frame[int(y):int(y + h), int(x):int(x + w)]
        gray = cv2.cvtColor(facecam_region, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 3)

        if len(faces) > 0:
            sec = int(timestamp)
            face_presence[sec] += 1

    cap.release()

    # Match to diarized speaker segments
    speaker_scores = defaultdict(int)
    for seg in diarized_segments:
        speaker = seg["speaker"]
        for sec in range(int(seg["start"]), int(seg["end"]) + 1):
            if face_presence[sec] > 0:
                speaker_scores[speaker] += face_presence[sec]

    if not speaker_scores:
        print("[WARN] No speaker matched with face activity.")
        return None

    # Return speaker with most visual overlap
    best_speaker = max(speaker_scores, key=speaker_scores.get)
    print(f"[INFO] Streamer matched to speaker: {best_speaker}")
    return best_speaker

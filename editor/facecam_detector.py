import cv2
import mediapipe as mp
import numpy as np

mp_face_detection = mp.solutions.face_detection


def detect_facecam_region(video_path, frame_sample_idx=0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_sample_idx)
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Could not read frame")

    h, w = frame.shape[:2]
    corner_size = int(min(h, w) * 0.3)
    corners = {
        "top_left": frame[0:corner_size, 0:corner_size],
        "top_right": frame[0:corner_size, w - corner_size:w],
        "bottom_left": frame[h - corner_size:h, 0:corner_size],
        "bottom_right": frame[h - corner_size:h, w - corner_size:w],
    }

    offset_coords = {
        "top_left": (0, 0),
        "top_right": (w - corner_size, 0),
        "bottom_left": (0, h - corner_size),
        "bottom_right": (w - corner_size, h - corner_size),
    }

    for key, region in corners.items():
        offset_x, offset_y = offset_coords[key]
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detector:
            results = face_detector.process(cv2.cvtColor(region, cv2.COLOR_BGR2RGB))
            if results.detections:
                for det in results.detections:
                    bbox = det.location_data.relative_bounding_box
                    x = int(bbox.xmin * region.shape[1])
                    y = int(bbox.ymin * region.shape[0])
                    w_box = int(bbox.width * region.shape[1])
                    h_box = int(bbox.height * region.shape[0])

                    # Use center of face box as seed
                    cx = x + w_box // 2
                    cy = y + h_box // 2

                    # Edge detection
                    edges = cv2.Canny(gray, 100, 200)

                    # Expand box around center using edge falloff
                    max_radius = min(region.shape[0], region.shape[1]) // 2
                    for r in range(20, max_radius, 5):
                        x1 = max(0, cx - r)
                        y1 = max(0, cy - r)
                        x2 = min(region.shape[1], cx + r)
                        y2 = min(region.shape[0], cy + r)
                        roi = edges[y1:y2, x1:x2]
                        edge_density = np.sum(roi > 0) / roi.size
                        if edge_density > 0.15:
                            break  # too many edges = boundary likely hit
                    else:
                        r = max_radius

                    fx1 = max(0, cx - r) + offset_x
                    fy1 = max(0, cy - r) + offset_y
                    fx2 = min(frame.shape[1], cx + r) + offset_x
                    fy2 = min(frame.shape[0], cy + r) + offset_y

                    cap.release()
                    return (fx1, fy1, fx2, fy2)

    cap.release()
    return None

import cv2
import numpy as np
import pytesseract
import re
from typing import List, Dict, Tuple

# Configuration
MIN_TEXT_LENGTH = 3
CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff]')
CONFIDENCE_THRESHOLD = 0.8
OCR_INTERVAL = 5  # Run OCR every N frames
IOU_REUSE_THRESHOLD = 0.9  # IOU threshold for fuzzy match reuse


class SubtitleDetector:
    def __init__(self):
        self.east_model_path = 'models/frozen_east_text_detection.pb'
        self.net = cv2.dnn.readNet(self.east_model_path)
        self.prev_subtitles: Dict[str, Tuple[int, Tuple[int, int, int, int]]] = {}
        self.frame_index = -1
        self.last_frame_result: List[Dict] = []
        self.last_frame_bboxes: List[Tuple[int, int, int, int]] = []

    def detect(self, frame: np.ndarray) -> List[Dict]:
        self.frame_index += 1

        text_regions = self._detect_text_regions(frame)
        grouped_regions = self._group_text_boxes(text_regions)

        # Reuse logic based on hash or IOU fuzzy match
        if self._should_reuse_previous(grouped_regions):
            print("♻️ Reusing previous OCR results (boxes match or very similar)")
            return self.last_frame_result

        ocr_results = []
        for (x, y, w, h) in grouped_regions:
            roi = frame[y:y + h, x:x + w]
            if roi.size == 0:
                continue
            config = '--psm 6'
            text = pytesseract.image_to_string(roi, config=config, lang='chi_sim').strip()

            print(f"🧪 OCR [{x}, {y}, {w}, {h}]:", repr(text))

            if len(text) >= MIN_TEXT_LENGTH and CHINESE_CHAR_PATTERN.search(text):
                self.prev_subtitles[text] = (self.frame_index, (x, y, w, h))
                ocr_results.append({"text": text, "bbox": (x, y, w, h)})

        # Update cache
        self.last_frame_result = ocr_results
        self.last_frame_bboxes = grouped_regions

        if self.frame_index == 0:
            for result in ocr_results:
                self._draw_box(frame, *result["bbox"], color=(0, 255, 0))
            cv2.imwrite("debug_regions_filtered.jpg", frame)

        return ocr_results

    def _should_reuse_previous(self, new_bboxes: List[Tuple[int, int, int, int]]) -> bool:
        if not self.last_frame_bboxes or len(new_bboxes) != len(self.last_frame_bboxes):
            return False

        for new_box, old_box in zip(new_bboxes, self.last_frame_bboxes):
            if self._bbox_hash(new_box) == self._bbox_hash(old_box):
                continue
            if self._bbox_iou(new_box, old_box) >= IOU_REUSE_THRESHOLD:
                continue
            return False

        return True

    def _bbox_hash(self, bbox: Tuple[int, int, int, int]) -> int:
        # Round to nearest 10 pixels to make comparison more forgiving
        return hash((round(bbox[0] / 10), round(bbox[1] / 10), round(bbox[2] / 10), round(bbox[3] / 10)))

    def _bbox_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]
        return interArea / float(boxAArea + boxBArea - interArea)

    def _reuse_previous_subtitles(self) -> List[Dict]:
        results = []
        for text, (last_seen, (x, y, w, h)) in self.prev_subtitles.items():
            if self.frame_index - last_seen < OCR_INTERVAL * 3:
                results.append({"text": text, "bbox": (x, y, w, h)})
        return results

    def _detect_text_regions(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        orig_h, orig_w = frame.shape[:2]
        new_w, new_h = 640, 640
        rW = orig_w / float(new_w)
        rH = orig_h / float(new_h)

        blob = cv2.dnn.blobFromImage(frame, 1.0, (new_w, new_h),
                                     (123.68, 116.78, 103.94), True, False)
        self.net.setInput(blob)
        (scores, geometry) = self.net.forward(['feature_fusion/Conv_7/Sigmoid',
                                               'feature_fusion/concat_3'])

        rects, confidences = self._decode_predictions(scores, geometry)
        boxes = cv2.dnn.NMSBoxes(rects, confidences, CONFIDENCE_THRESHOLD, 0.4)

        results = []
        for i in boxes.flatten():
            (x, y, w, h) = rects[i]
            results.append((int(x * rW), int(y * rH), int(w * rW), int(h * rH)))
        print("📦 Detected regions:", len(results))
        return results

    def _decode_predictions(self, scores, geometry):
        (num_rows, num_cols) = scores.shape[2:4]
        rects = []
        confidences = []

        for y in range(num_rows):
            scores_data = scores[0, 0, y]
            x0_data = geometry[0, 0, y]
            x1_data = geometry[0, 1, y]
            x2_data = geometry[0, 2, y]
            x3_data = geometry[0, 3, y]
            angles_data = geometry[0, 4, y]

            for x in range(num_cols):
                if scores_data[x] < CONFIDENCE_THRESHOLD:
                    continue

                angle = angles_data[x]
                cos = np.cos(angle)
                sin = np.sin(angle)

                h = x0_data[x] + x2_data[x]
                w = x1_data[x] + x3_data[x]
                end_x = int(x * 4.0 + cos * x1_data[x] + sin * x2_data[x])
                end_y = int(y * 4.0 - sin * x1_data[x] + cos * x2_data[x])
                start_x = int(end_x - w)
                start_y = int(end_y - h)

                rects.append((start_x, start_y, w, h))
                confidences.append(float(scores_data[x]))

        return rects, confidences

    def _group_text_boxes(self, boxes: List[Tuple[int, int, int, int]], y_thresh: int = 10, x_thresh: int = 30) -> List[
        Tuple[int, int, int, int]]:
        if not boxes:
            return []

        boxes = sorted(boxes, key=lambda b: (b[1], b[0]))
        groups = []
        current_group = [boxes[0]]

        for box in boxes[1:]:
            _, y, _, h = box
            last_y = current_group[-1][1]
            if abs(y - last_y) <= y_thresh:
                current_group.append(box)
            else:
                groups.append(current_group)
                current_group = [box]

        groups.append(current_group)

        merged_boxes = []
        for group in groups:
            x0 = min(b[0] for b in group)
            y0 = min(b[1] for b in group)
            x1 = max(b[0] + b[2] for b in group)
            y1 = max(b[1] + b[3] for b in group)
            merged_boxes.append((x0, y0, x1 - x0, y1 - y0))

        return merged_boxes

    def _draw_box(self, frame: np.ndarray, x: int, y: int, w: int, h: int, color=(0, 255, 0)):
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

import cv2
import numpy as np
import re
from paddleocr import PaddleOCR
from typing import List, Dict, Tuple

# Configuration
MIN_TEXT_LENGTH = 3
CHINESE_CHAR_PATTERN = re.compile(r'[\u4e00-\u9fff]')
OCR_INTERVAL = 5  # Run OCR every N frames


class SubtitleDetector:
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
        self.prev_subtitles: Dict[str, Tuple[int, Tuple[int, int, int, int]]] = {}
        self.frame_index = -1
        self.last_frame_result: List[Dict] = []
        self.last_frame_bboxes: List[Tuple[int, int, int, int]] = []

    def detect(self, frame: np.ndarray) -> List[Dict]:
        self.frame_index += 1

        result = self.ocr.ocr(frame, cls=True)
        ocr_results = []

        for line in result[0]:
            box_points = line[0]  # list of 4 points
            text = line[1][0].strip()
            confidence = line[1][1]

            if len(text) >= MIN_TEXT_LENGTH and CHINESE_CHAR_PATTERN.search(text):
                # Convert box_points to x, y, w, h
                x_coords = [pt[0] for pt in box_points]
                y_coords = [pt[1] for pt in box_points]
                x, y = int(min(x_coords)), int(min(y_coords))
                w, h = int(max(x_coords)) - x, int(max(y_coords)) - y

                self.prev_subtitles[text] = (self.frame_index, (x, y, w, h))
                ocr_results.append({"text": text, "bbox": (x, y, w, h)})

        self.last_frame_result = ocr_results
        self.last_frame_bboxes = [r["bbox"] for r in ocr_results]

        for result in ocr_results:
            self._draw_box(frame, *result["bbox"], color=(0, 255, 0))
        cv2.imwrite(f"debug_frames/debug_regions_filtered_{self.frame_index:04d}.jpg", frame)

        return ocr_results

    def _draw_box(self, frame: np.ndarray, x: int, y: int, w: int, h: int, color=(0, 255, 0)):
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    def _reuse_previous_subtitles(self) -> List[Dict]:
        results = []
        for text, (last_seen, (x, y, w, h)) in self.prev_subtitles.items():
            if self.frame_index - last_seen < OCR_INTERVAL * 3:
                results.append({"text": text, "bbox": (x, y, w, h)})
        return results

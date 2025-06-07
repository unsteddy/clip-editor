from subtitle_processing.subtitle_detector import SubtitleDetector
from subtitle_processing.subtitle_tracker import SubtitleTracker
import numpy as np


class SubtitlePipeline:
    def __init__(self):
        self.detector = SubtitleDetector()
        self.tracker = SubtitleTracker()

    def process_frame(self, frame: np.ndarray):
        # Detect subtitles in this frame
        detections = self.detector.detect(frame)

        # Assign tracking IDs to detected subtitles
        tracked = self.tracker.update(detections)

        return tracked

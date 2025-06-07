from typing import List, Dict, Tuple
import numpy as np


class SubtitleTracker:
    def __init__(self, max_age=10, iou_threshold=0.5):
        self.max_age = max_age
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Dict] = {}
        self.next_id = 0

    def update(self, detections: List[Dict]) -> List[Dict]:
        updated_tracks = {}
        assigned_ids = set()

        for det in detections:
            best_iou = 0
            best_track_id = None
            for track_id, track in self.tracks.items():
                iou = self._bbox_iou(track['bbox'], det['bbox'])
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id is not None:
                updated_tracks[best_track_id] = {
                    'text': det['text'],
                    'bbox': det['bbox'],
                    'age': 0
                }
                assigned_ids.add(best_track_id)
            else:
                updated_tracks[self.next_id] = {
                    'text': det['text'],
                    'bbox': det['bbox'],
                    'age': 0
                }
                assigned_ids.add(self.next_id)
                self.next_id += 1

        # Age and keep unmatched tracks
        for track_id, track in self.tracks.items():
            if track_id not in assigned_ids:
                track['age'] += 1
                if track['age'] <= self.max_age:
                    updated_tracks[track_id] = track

        self.tracks = updated_tracks

        return [
            {'id': track_id, 'text': track['text'], 'bbox': track['bbox']}
            for track_id, track in self.tracks.items()
        ]

    def _bbox_iou(self, boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
        yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0

        boxAArea = boxA[2] * boxA[3]
        boxBArea = boxB[2] * boxB[3]

        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou

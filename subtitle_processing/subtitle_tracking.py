import numpy as np


def iou(boxA, boxB):
    # Intersection over Union between two boxes
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[0] + boxA[2], boxB[0] + boxB[2])
    yB = min(boxA[1] + boxA[3], boxB[1] + boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = boxA[2] * boxA[3]
    boxBArea = boxB[2] * boxB[3]

    iou_value = interArea / float(boxAArea + boxBArea - interArea)
    return iou_value


class SubtitleTracker:
    def __init__(self, iou_threshold=0.5):
        self.previous_regions = []
        self.iou_threshold = iou_threshold

    def update(self, current_regions):
        """
        Given current frame regions, return matched regions
        or initialize new ones if no sufficient overlap.
        """
        matched = []
        for region in current_regions:
            best_iou = 0
            best_match = None

            for prev in self.previous_regions:
                score = iou(region['box'], prev['box'])
                if score > best_iou:
                    best_iou = score
                    best_match = prev

            if best_iou > self.iou_threshold:
                matched.append({
                    'box': region['box'],
                    'text': region['text'],
                    'matched_text': best_match['text']  # Optionally retain match
                })
            else:
                matched.append(region)

        self.previous_regions = matched
        return matched

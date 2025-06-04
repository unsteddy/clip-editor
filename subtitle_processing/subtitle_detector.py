import cv2
import pytesseract
from pytesseract import Output


# Ensure Tesseract is configured with Chinese language
# You must have chi_sim installed: `tesseract --list-langs` should include 'chi_sim'


def detect_chinese_subtitles(frame, lang="chi_sim"):
    """
    Detects Chinese text in the frame using Tesseract OCR.
    Returns a list of bounding boxes for detected text regions.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Optional: apply threshold to enhance OCR accuracy
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Run Tesseract OCR
    data = pytesseract.image_to_data(thresh, lang=lang, output_type=Output.DICT)

    regions = []
    for i in range(len(data['text'])):
        text = data['text'][i]
        if text.strip() == "":
            continue

        # Heuristic: Only include Chinese characters (Unicode range)
        if any('\u4e00' <= ch <= '\u9fff' for ch in text):
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            regions.append({
                "text": text,
                "box": (x, y, w, h)
            })

    return regions


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    frame = cv2.imread(sys.argv[1])
    regions = detect_chinese_subtitles(frame)

    for region in regions:
        x, y, w, h = region['box']
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.title("Detected Chinese Subtitles")
    plt.axis("off")
    plt.show()

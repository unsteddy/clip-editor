import cv2


def overlay_translations(frame, regions, translation_map, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1.0,
                         color=(255, 255, 255), thickness=2):
    """
    Draw English translations over blurred subtitle regions.

    :param frame: input frame (BGR)
    :param regions: list of dicts with 'box': (x, y, w, h) and 'text'
    :param translation_map: dict of {chinese: english}
    :param font: cv2 font type
    :param font_scale: scale factor for font
    :param color: text color
    :param thickness: text stroke thickness
    :return: frame with text overlays
    """
    output = frame.copy()

    for region in regions:
        chinese = region['text']
        x, y, w, h = region['box']
        english = translation_map.get(chinese, "[MISSING TRANSLATION]")

        # Center text horizontally in the region
        (text_w, text_h), _ = cv2.getTextSize(english, font, font_scale, thickness)
        text_x = x + (w - text_w) // 2
        text_y = y + (h + text_h) // 2  # center vertically

        cv2.putText(output, english, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

    return output

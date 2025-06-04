import cv2


def blur_regions(frame, regions, ksize=(25, 25)):
    """
    Applies Gaussian blur to specified rectangular regions in the frame.

    :param frame: input image (BGR)
    :param regions: list of dicts with 'box': (x, y, w, h)
    :param ksize: blur kernel size
    :return: blurred frame
    """
    output = frame.copy()

    for region in regions:
        x, y, w, h = region['box']
        sub_img = output[y:y + h, x:x + w]
        blurred = cv2.GaussianBlur(sub_img, ksize, 0)
        output[y:y + h, x:x + w] = blurred

    return output

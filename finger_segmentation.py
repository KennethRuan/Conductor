import imutils
import cv2
import numpy as np


def intersect(x1, y1, x2, y2, palm_line):
    # (x1, y1) is finger, (x2, y2) is palm
    width = x2 - x1
    height = y1 - y2
    return (y1 - palm_line) * width / height


def count_segments(image, row):
    return len(np.unique(cv2.connectedComponents(image[row])))


def identify_fingers(image, finger_components, x, y):
    # assumes that hand is upright and that the thumb is removed
    # x, y -> palm center
    height, width = image.shape
    palm_line = height
    start, end = -1, -1
    for i in range(height - 1, -1, -1):
        components = cv2.connectedComponents(image[i])
        if len(np.unique(components)) >= 2:
            palm_line = i
            for j in range(len(components)):
                if components[j] != 0:
                    if start == -1:
                        start = j
                    end = j
            break
    finger_components = cv2.connectedComponents(finger_components)

    low = [-1] * 5
    high = [-1] * 5
    ret = []

    for i in range(height - 1, -1, -1):
        finger_ids = np.unique(finger_components[i])
        for j in finger_ids:
            if low[j] == -1:
                low[j] = i
            high[j] = i

    len_palm = end - start

    for i in range(5):
        if low[i] != -1:
            x_val = image[low[i]].index(i)
            y_val = low[i]
            finger_type = intersect(x_val, y_val, x, y, palm_line) * 4 // len_palm
            ret.append([image[high[i]].index(i), high[i], finger_type])

    return ret
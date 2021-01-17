import imutils
import cv2
import numpy as np


def first_occ(arr, val):
    for i in range(len(arr)):
        if arr[i] == val:
            return i
    return -1


def intersect(x1, y1, x2, y2, palm_line):
    # (x1, y1) is finger, (x2, y2) is palm
    width = x2 - x1
    height = y1 - y2
    return x1 + (y1 - palm_line) * width // height


def count_segments(image, row):
    return len(np.unique(cv2.connectedComponents(image[row])))


def identify_fingers(image, finger_components, x, y):
    # assumes that hand is upright and that the thumb is removed
    # x, y -> palm center
    # assumes that thumb is on the left
    # returns an array in the format: [[fingertip1x, fingertip1y, fingertip1type],[finger2tip...]]
    # finger tip type: 0 = index, 1 = middle, 2 = ring, 3 = pinky
    height, width = image.shape
    palm_line = height
    start, end = -1, -1
    for i in range(height - 1, -1, -1):
        garbage, components = cv2.connectedComponents(image[i])

        if len(np.unique(components)) >= 3:
            palm_line = i
            for j in range(len(components)):
                if components[j][0] != 0:
                    if start == -1:
                        start = j
                    end = j
            break
    cnt, finger_components = cv2.connectedComponents(finger_components)

    low = [-1] * 5
    high = [-1] * 5
    ret = []

    for i in range(palm_line - 1, -1, -1):
        finger_ids = np.unique(finger_components[i])
        for cnt, j in enumerate(finger_ids):
            if cnt > 4:
                break
            if low[j] == -1:
                low[j] = i
            high[j] = i

    len_palm = end - start

    for i in range(1, 5):
        if low[i] != -1:
            x_val = first_occ(finger_components[low[i]], i)
            y_val = low[i]
            finger_type = (intersect(x_val, y_val, x, y, palm_line) - start) * 4 // len_palm

            args = [first_occ(finger_components[high[i]], i), high[i], finger_type]
            ret.append(args)

    ret.sort(key = lambda val: val[0])
    print("Before",ret)
    finger_count = len(ret)

    for i in range(len(ret)):
        if ret[i][2] < 0:
            ret[i][2] = 0

        if ret[i][2] > 3:
            ret[i][2] = 3

        if ret[i][2] > i - finger_count + 4:
            ret[i][2] = i - finger_count + 4  # max ID such that there are no overlaps (hard code case)

        if i != 0 and ret[i][2] == ret[i - 1][2]:
            ret[i][2] = ret[i - 1][2] + 1

    return ret
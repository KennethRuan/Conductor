import imutils
import cv2
import time

def crop_wrist(image):
    # assume that image is oriented vertically
    # height > width
    height, width = image.shape
    if width > height:
        image = imutils.rotate_bound(image, -90)
        height, width = width, height
    # print(image.shape)
    # pre = time.clock()
    sweep = [0] * height
    for i in range(height):
        sweep[i] = cv2.countNonZero(image[i])
    b = int(height * 0.7)
    # post = time.clock()
    # print("Exec time:", post-pre)

    peak_left, peak_l_idx = 0, b
    peak_right, peak_r_idx = 0, b + 1

    for i in range(b, -1, -1):
        if sweep[i] > peak_left:
            peak_left = sweep[i]
            peak_l_idx = i

    for i in range(b + 1, height):
        if sweep[i] > peak_right:
            peak_right = sweep[i]
            peak_r_idx = i

    valley, v_idx = 0, b
    for i in range(peak_l_idx, peak_r_idx + 1):
        if sweep[i] < valley:
            valley = sweep[i]
            v_idx = i

    a = max((v_idx - peak_l_idx), 1)
    b = max((peak_r_idx - v_idx), 1)
    slope_l = (peak_left - valley) / a
    slope_r = (peak_right - valley) / b

    if slope_l < slope_r:
        return image[:v_idx]
    else:
        res = image[v_idx:]
        res = imutils.rotate_bound(res, 180)
        return res

import imutils


def crop_wrist(image):
    # assume that image is oriented vertically
    # height > width
    height, width = image.shape
    if width > height:
        imutils.rotate_bound(image, -90)
    height, width = width, height

    sweep = [0] * height
    for i in range(height):
        for j in range(width):
            sweep[i] += image[i][j] != 0
    b = height // 2

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

    slope_l = (peak_left - valley) / (v_idx - peak_l_idx)
    slope_r = (peak_right - valley) / (peak_r_idx - v_idx)

    if slope_l > slope_r:
        return image[:v_idx]
    else:
        return image[v_idx:]

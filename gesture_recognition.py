import cv2
import numpy as np
import imutils

# Parameters
binThreshold = 60
bgSubThreshold = 30
xBound = 0.6
yBound = 0.9
gBlur = 21

# Global Variables
bgSubtractor = None
bgCaptured = False


def removeBackground(frame):
    fgMask = bgSubtractor.apply(frame, learningRate=0)
    kernel = np.ones((2, 2), np.uint8)
    fgMask = cv2.erode(fgMask, kernel, iterations=3)
    res = cv2.bitwise_and(frame, frame, mask=fgMask)
    return res


def bwdist(img, metric=cv2.DIST_C, maskSize = cv2.DIST_MASK_3, labelType = cv2.DIST_LABEL_PIXEL):
    flip = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV)[1]
    dist, btw = cv2.distanceTransformWithLabels(img, metric, maskSize, labelType=labelType)
    _, wtb = cv2.distanceTransformWithLabels(flip, metric, maskSize, labelType=labelType)
    return dist, wtb, btw


def minPalmBound(img, center):
    ox, oy = center[1], center[0]  # Origin
    nc = ((1, 0), (1, -1),(0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1))  # Neighbour Coords

    numSamplePoints = 48
    mask = [[] for _ in range(numSamplePoints)]
    sampleFound = False
    r = 0
    inner = 0

    while not sampleFound:
        r += 1
        for idx in range(numSamplePoints):
            a = 360/numSamplePoints * idx
            x = int(np.cos(a * np.pi/180) * r + ox)
            y = int(np.sin(a * np.pi/180) * r + oy)

            if not (0 <= x < img.shape[1] and 0 <= y < img.shape[0]):
                continue

            if img[y, x] == 0:
                flag = True
                for elem in nc:
                    nx = x + elem[0]
                    ny = y + elem[1]
                    if 0 <= nx < img.shape[1] and 0 <= ny < img.shape[0] and img[ny, nx] == 255:
                        flag = False
                if flag:
                    sampleFound = True
                    break

        inner = r

        if sampleFound:
            r *= 1.2
            for idx in range(numSamplePoints):
                a = 360 / numSamplePoints * idx
                x = int(np.cos(a * np.pi / 180) * r + ox)
                y = int(np.sin(a * np.pi / 180) * r + oy)
                x = max(0, min(x, img.shape[1] - 1))
                y = max(0, min(y, img.shape[0] - 1))
                if len(mask[idx]) == 0:
                    mask[idx] = [x, y]

    return mask, inner


camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera.set(10, 200)

while camera.isOpened():
    ret, frame = camera.read()
    frame = cv2.flip(frame, 1)  # Flip frame horizontally

    if bgCaptured:
        # Crop the image in the bounding box
        img = removeBackground(frame)
        img = img[:int(yBound * frame.shape[0]),
              int((1 - xBound) * frame.shape[1]):]

        cv2.imshow('filtered', img)

        # Grayscale and blurring
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (gBlur, gBlur), 0)

        # Using a threshold to determine how 'blurry' an edge can be and included
        ret, thresh = cv2.threshold(blur, binThreshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        invertedThresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY_INV)[1]

        # Find the largest contour to avoid noise, may be removed depending on performance cost, as most noise can be
        # removed using a clean background
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            contours = sorted(contours, key=lambda x: cv2.contourArea(x))
            for contour in contours[:-1]:
                cv2.drawContours(thresh, [contour], -1, (0, 0, 0), -1)

            c = contours[-1]
            (x, y, w, h) = cv2.boundingRect(c)
            mask = np.zeros(gray.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            imageROI = thresh[y:y + h, x:x + w]
            maskROI = mask[y:y + h, x:x + w]
            imageROI = cv2.bitwise_and(imageROI, imageROI,
                                       mask=maskROI)

            idealAngle = 0
            minArea = float("inf")
            for angle in np.arange(15, 375, 15):
                if angle in [90, 180, 270]:
                    continue
                rotated = imutils.rotate_bound(maskROI, angle)
                roicontours, hierarchy = cv2.findContours(rotated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if len(roicontours) > 0:
                    roicontours = sorted(roicontours, key=lambda x: cv2.contourArea(x))
                    (mbbx, mbby, mbbw, mbbh) = cv2.boundingRect(roicontours[-1])
                    if mbbw * mbbh < minArea:
                        minArea = mbbw * mbbh
                        idealAngle = angle

            mbb = imutils.rotate_bound(imageROI, idealAngle)
            mbbcontours, hierarchy = cv2.findContours(mbb, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            mbbcontours = sorted(mbbcontours, key=lambda x: cv2.contourArea(x))
            (x, y, w, h) = cv2.boundingRect(mbbcontours[-1])
            mbb = mbb[y:y + h, x:x + w]
            cv2.imshow("ROI", mbb)

            # Ben's Method
            # Returns cropped hand and the position of the found bounding box to remap the transforms
            # Also returns wrist line

        # Distance transform creates a map where the pixels furthest away from an edge have a larger value
        dt, labelsw, labelsb = bwdist(thresh, cv2.DIST_C, cv2.DIST_MASK_3)  # wtb, btw
        cv2.normalize(dt, dt, 0, 1.0, cv2.NORM_MINMAX)

        # Select the furthest pixel as the center of the palm
        palmCenter = np.unravel_index(dt.argmax(), dt.shape)
        drawnImg = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        cv2.circle(drawnImg, (palmCenter[1], palmCenter[0]), 5, (255, 0, 0), -1)

        # Calculating palm mask
        # Begin by finding the minimal bound of the palm
        minBoundPoints, radius = minPalmBound(thresh, palmCenter)

        maskPoints = []

        for mx, my in minBoundPoints:
            if thresh[my, mx] == 0:
                l = labelsw[my][mx]
                mask = labelsw == l
                px = np.dstack(np.where(thresh * mask))
                if px.size == 0:
                    continue
            else:
                l = labelsb[my][mx]
                mask = labelsb == l
                px = np.dstack(np.where(invertedThresh * mask))
                if px.size == 0:
                    continue
            maskPoints.append(px[0][0])

        palmContour = []
        for i, point in enumerate(maskPoints):
            palmContour.append([point[1], point[0]])

        if len(maskPoints) > 0:
            cv2.drawContours(drawnImg, [np.array(palmContour)], 0, (255, 0, 0), 2)
        cv2.imshow('drawn', drawnImg)

    cv2.rectangle(frame, (int((1 - xBound) * frame.shape[1]), 0),
                  (frame.shape[1], int(yBound * frame.shape[0])), (255, 0, 0), 2)

    # Output video feed
    cv2.imshow("original", frame)

    k = cv2.waitKey(10)
    if k == ord('b'):
        bgSubtractor = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        bgCaptured = True
        print('Background captured')


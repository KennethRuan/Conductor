import cv2
import numpy as np
import imutils

from mouse_interpreter import interpret_finger_state
from wrist_detection import crop_wrist
from finger_segmentation import identify_fingers
import time
from copy import deepcopy

# Parameters
binThreshold = 60
bgSubThreshold = 30
xBound = 0.6
yBound = 0.9
sxBoundL = 0.6
sxBoundR = 0.9
syBound = 0.45
gBlur = 21

# Global Variables
bgSubtractor = None
bgCaptured = False
colours = [(255,0,0), (0,255,0), (0,0,255), (255,0,255), (0,255,255), (0,0,0), (0,0,0), (0,0,0), (0,0,0), (0,0,0)]


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
    outOfBounds = [False for _ in range(numSamplePoints)]
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
                outOfBounds[idx] = True
                if all(outOfBounds):
                    sampleFound = True
                    break
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
            r *= 1.15
            for idx in range(numSamplePoints):
                a = 360 / numSamplePoints * idx
                x = int(np.cos(a * np.pi / 180) * r + ox)
                y = int(np.sin(a * np.pi / 180) * r + oy)
                x = max(0, min(x, img.shape[1] - 1))
                y = max(0, min(y, img.shape[0] - 1))
                if len(mask[idx]) == 0:
                    mask[idx] = [x, y]

    return mask, inner


def euDist(p1, p2):
    p1x, p1y, p2x, p2y = p1[0], p1[1], p2[0], p2[1]
    dist = np.sqrt((p1x-p2x)**2 + (p1y-p2y)**2)
    return dist


def angleCalc(p1, p2):
    y1, x1, y2, x2 = p1[0], p1[1], p2[0], p2[1]
    dx = x1 - x2
    dy = y1 - y2
    if dx == 0:
        dx = 1
    if dy == 0:
        dy = 1
    res = np.arctan(dy/dx)
    return res * 180/np.pi


def rotate_points(bb, h, w, angle):
    cy, cx = h//2, w//2
    new_bb = list(bb)
    for i, coord in enumerate(bb):
        # opencv calculates standard transformation matrix
        M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
        # Grab  the rotation components of the matrix)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        # compute the new bounding dimensions of the image
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        # adjust the rotation matrix to take into account translation
        M[0, 2] += (nW / 2) - cx
        M[1, 2] += (nH / 2) - cy
        # Prepare the vector to be transformed
        v = [coord[0],coord[1],1]
        # Perform the actual rotation and return the image
        calculated = np.dot(M,v)
        new_bb[i] = (int(round(calculated[0])), int(round(calculated[1])))
    return new_bb

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera.set(10, 200)

while camera.isOpened():
    ret, frame = camera.read()
    frame = cv2.flip(frame, 1)  # Flip frame horizontally
    pre = time.clock()
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

        # Find the largest contour to avoid noise, may be removed depending on performance cost, as most noise can be
        # removed using a clean background
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        if len(contours) != 0:
            contours = sorted(contours, key=lambda x: cv2.contourArea(x))
            for contour in contours[:-1]:
                cv2.drawContours(thresh, [contour], -1, (0, 0, 0), -1)

            c = contours[-1]
            (x, y, w, h) = cv2.boundingRect(c)
            # mask = np.zeros(gray.shape, dtype="uint8")
            if y < int(syBound*frame.shape[0]):
                thresh = thresh[:int(syBound*frame.shape[0]+y)]
        invertedThresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY_INV)[1]

        # Distance transform creates a map where the pixels furthest away from an edge have a larger value
        dt, labelsw, labelsb = bwdist(thresh, cv2.DIST_L2, cv2.DIST_MASK_3)  # wtb, btw
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

        wristLine = []
        mxDist = 0
        n = len(maskPoints)
        for i, point in enumerate(maskPoints):
            pDist = euDist(maskPoints[i], maskPoints[(i + 1) % n])
            if pDist > mxDist:
                wristLine = [maskPoints[i], maskPoints[(i + 1) % n]]
                mxDist = pDist

        # Calculate angle of wrist line
        if len(wristLine) > 0:
            # Rotates wrist and cuts off below the wrist line
            wristAngle = -angleCalc(wristLine[0], wristLine[1])
            wristAngle = 5 * round(wristAngle/5)

            # I need to keep track of what happens with this
            rotated = imutils.rotate_bound(thresh, wristAngle)
            wristRotated = rotate_points(wristLine, thresh.shape[1], thresh.shape[0], wristAngle)  # takes y,x outputs y,x
            wristYRotated = wristRotated[0][0]
            cv2.line(rotated, (wristRotated[0][1], wristRotated[0][0]), (wristRotated[1][1],wristRotated[1][0]), 0, 2)
            cv2.rectangle(rotated, (0, wristYRotated), (rotated.shape[1], rotated.shape[0]), 0, -1)

            preMaskPoints = []
            rotatedMaskPoints = rotate_points(maskPoints, thresh.shape[1], thresh.shape[0], wristAngle)
            rotatedPalmCenter = rotate_points([palmCenter], thresh.shape[1], thresh.shape[0], wristAngle)[0]
            for i in range(len(rotatedMaskPoints)):
                preMaskPoints.append([rotatedMaskPoints[i][1], rotatedMaskPoints[i][0]])
            # print(preMaskPoints)
            ctrMask = np.array(preMaskPoints).reshape((-1,1,2)).astype(np.int32)
            cv2.drawContours(rotated, [ctrMask], 0, 0, -1)
            rotatedCopy = deepcopy(rotated)
            blur = cv2.GaussianBlur(rotated, (gBlur, gBlur), 0)
            ret, blurred = cv2.threshold(blur, binThreshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            cv2.drawContours(rotatedCopy, [ctrMask], 0, 255, -1)
            palmBlurred = cv2.GaussianBlur(rotatedCopy, (gBlur, gBlur), 0)
            ret, thumblessMask = cv2.threshold(palmBlurred, binThreshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # cv2.circle(rotated, (rotatedPalmCenter[1], rotatedPalmCenter[0]), 10, (255,255,0), 2)

            #this returns it back to normal?
            handSegmented = imutils.rotate_bound(blurred, -wristAngle)
            thumblessMask = imutils.rotate_bound(thumblessMask, -wristAngle)
            hxs = handSegmented.shape[1] // 2 - thresh.shape[1] // 2
            hxe = handSegmented.shape[1] // 2 + thresh.shape[1] // 2
            hys = handSegmented.shape[0] // 2 - thresh.shape[0] // 2
            hye = handSegmented.shape[0] // 2 + thresh.shape[0] // 2
            handSegmented = handSegmented[hys:hye, hxs:hxe]
            thumblessMask = thumblessMask[hys:hye, hxs:hxe]

            # print(wristAngle)
            fingerContours, hierarchy = cv2.findContours(handSegmented, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            # handSegmented = cv2.cvtColor(handSegmented, cv2.COLOR_GRAY2BGR)
            right = True
            for i,c in enumerate(fingerContours):
                # Simple method for bounding box, does not get the mbb, can update in the future
                if cv2.contourArea(c) <= 600:
                    print("Cut finger",i,"size",cv2.contourArea(c))
                    cv2.drawContours(handSegmented, [c], -1, 0, -1)
                    cv2.drawContours(thumblessMask, [c], -1, 0, -1)
                    continue
                bbx, bby, bbw, bbh = cv2.boundingRect(c)
                M = cv2.moments(c)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                fingerAngle = angleCalc(rotatedPalmCenter,(cY,cX))+wristAngle  # method takes y,x
                if 0 <= fingerAngle < 50:
                    print("Cut finger",i,"angle",fingerAngle)
                    cv2.drawContours(handSegmented, [c], -1, 0, -1)
                    cv2.drawContours(thumblessMask, [c], -1, 0, -1)
                    right = True
                elif 0 >= fingerAngle > 50:
                    print("Cut finger",i,"angle",fingerAngle)
                    cv2.drawContours(handSegmented, [c], -1, 0, -1)
                    cv2.drawContours(thumblessMask, [c], -1, 0, -1)
                    right = False
            fingerMask = deepcopy(handSegmented)
            # cv2.imshow("f", fingerMask)
            # cv2.imshow("tl", thumblessMask)

            blur = cv2.GaussianBlur(fingerMask, (gBlur, gBlur), 0)
            ret, fingerMask = cv2.threshold(blur, binThreshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            blur = cv2.GaussianBlur(thumblessMask, (gBlur, gBlur), 0)
            ret, thumblessMask = cv2.threshold(blur, binThreshold, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # cv2.waitKey(0)
            # handSegmented = cv2.cvtColor(handSegmented, cv2.COLOR_BGR2GRAY)
            # ret, handSegmented = cv2.threshold(handSegmented, 60, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            handContours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            handContours = sorted(handContours, key=lambda x: cv2.contourArea(x))

            if len(handContours) > 0:
                # this should be the key, the output is rotated back to og thresh size at this point
                hcx, hcy, hcw, hch = cv2.boundingRect(handContours[-1])
                fingerROI = fingerMask[hcy:hcy + hch, hcx:hcx + hcw]
                thumblessROI = thumblessMask[hcy:hcy + hch, hcx:hcx + hcw]

                # fingerROI = imutils.rotate_bound(fingerROI, wristAngle)
                # thumblessROI = imutils.rotate_bound(thumblessROI, wristAngle)

                # cv2.imshow("pp", fingerROI)
                # cv2.imshow("pp2", thumblessROI)

                outputY = fingerROI.shape[0]
                outputX = fingerROI.shape[1]

                output = identify_fingers(thumblessROI, fingerROI, palmCenter[1]-hxs, palmCenter[0]-hys)

                # fingerROI = imutils.rotate_bound(fingerROI, -wristAngle)
                # thumblessROI = imutils.rotate_bound(thumblessROI, -wristAngle)

                # cv2.imshow("wonka", fingerROI)
                # cv2.imshow("donka", thumblessROI)

                xs = fingerROI.shape[1] // 2 - hcw // 2
                xe = fingerROI.shape[1] // 2 + hcw // 2
                ys = fingerROI.shape[0] // 2 - hch // 2
                ye = fingerROI.shape[0] // 2 + hch // 2

                fingerROI = fingerROI[ys:ye,xs:xe]
                thumblessROI = thumblessROI[ys:ye,xs:xe]

                for i in range(len(output)):
                    # ryx = rotate_points([yx], outputY, outputX, -wristAngle)[0]
                    # print(ryx[1], ryx[0])
                    output[i] = [output[i][0] + hcx, output[i][1] + hcy, output[i][2]]
                    cv2.circle(drawnImg, (output[i][0], output[i][1]), 4, (0,255,0), 2)

                # for i in range(len(output)):
                #     height, width = drawnImg.shape
                #     output[i][0] = output[i][0] * 1080 // height
                interpret_finger_state(output, drawnImg)
                print(output)

            # cv2.waitKey(0)

        post = time.clock()
        # print("exec", post-pre)
        # Draw wrist line and palm mask
        if len(maskPoints) > 0:
            cv2.drawContours(drawnImg, [np.array(palmContour)], 0, (255, 0, 0), 2)
            cv2.line(drawnImg, (wristLine[0][1], wristLine[0][0]), (wristLine[1][1], wristLine[1][0]), (0, 0, 255), 2)

        cv2.imshow('drawn', drawnImg)

    cv2.rectangle(frame, (int((1 - xBound) * frame.shape[1]), 0),
                  (frame.shape[1], int(yBound * frame.shape[0])), (255, 0, 0), 2)
    cv2.rectangle(frame, (int((1 - sxBoundL) * frame.shape[1]), 0),
                  (int(frame.shape[1] * sxBoundR), int(syBound * frame.shape[0])), (0, 255, 0), 2)

    # Output video feed
    cv2.imshow("original", frame)

    k = cv2.waitKey(10)
    if k == ord('b'):
        bgSubtractor = cv2.createBackgroundSubtractorMOG2(0, bgSubThreshold)
        bgCaptured = True
        print('Background captured')


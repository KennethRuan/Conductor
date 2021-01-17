import cv2

from mouseMovement import mouseMovement

index, middle, ring, pinky = 0, 1, 2, 3


def isHeld(finger):
    return finger[0] != -1 and finger[1] != -1


def interpret_finger_state(table, img, finger_count):
    finger_map = [[-1 for _ in range(2)] for __ in range(5)]

    for x, y, type in table:
        finger_map[type][0] = x
        finger_map[type][1] = y

    finger_count = max(finger_count, len(table))
    print(finger_count)
    command = 'n'
    if finger_count == 2:
        command = 'l'
    if finger_count == 3:
        command = 'd'
    if finger_count == 4:
        command = 'u'

    leftmost = 5
    if finger_count >= 1:
        for i in range(5):
            if isHeld(finger_map[i]):
                leftmost = i
                break

        cv2.circle(img, (finger_map[leftmost][0], finger_map[leftmost][1]), 4, (255, 0, 0), 4)
        mouseMovement(finger_map[leftmost][0], finger_map[leftmost][1], command)

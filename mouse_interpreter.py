from mouseMovement import mouseMovement

index, middle, ring, pinky = 0, 1, 2, 3


def isHeld(finger):
    return finger[0] != -1 and finger[1] != -1


def interpret_finger_state(table):
    finger_map = [[-1 for _ in range(2)] for __ in range(5)]

    for x, y, type in table:
        finger_map[type][0] = x
        finger_map[type][1] = y

    if isHeld(finger_map[index]) == -1:
        return

    command = 'r' if isHeld(finger_map[ring]) else 'l' if isHeld(finger_map[middle]) else 'n'

    mouseMovement(finger_map[index][0], finger_map[index][1], command)

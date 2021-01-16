#orz ronald
import keyboard
import pyautogui
import sys
import numpy

print(pyautogui.size())
prevX = 0
prevY = 0
i = 0
j = 0
count = 0
a = [[100, 200], [10, 30], [11, 34], [11, 35], [11, 36], [11, 37], [11, 38], [11, 39], [11, 40], [11, 41], [11, 42], [11, 43], [11, 44], [11, 45], [11, 46], [11, 47], [11, 48], [11, 49], [11, 50], [11, 51], [11, 52], [300, 600], [601, 100], [1000, 10], [1000, 9]]


def mouseMovement(curX, curY):
    global prevX, prevY, count
    if abs(numpy.sqrt(pow(prevX - curX, 2) + pow(prevY - curY, 2)) > 10):
        pyautogui.moveTo(curX, curY, duration=1)
        print(pyautogui.position())
        count = 0
    if count == 19:
        pyautogui.moveTo(curX, curY, duration=1)
        print(pyautogui.position())
        count = 0
    prevX = curX
    prevY = curY
    count += 1
    return


while True:
    mouseMovement(a[i][0], a[i][1])
    i += 1
    if keyboard.is_pressed('q'):
        print("i got here")
        sys.exit()
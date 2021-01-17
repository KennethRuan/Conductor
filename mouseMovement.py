import keyboard
import pyautogui
import sys
import numpy
import time
import mouse

prevX = 0
prevY = 0
missedX = 0
missedY = 0
cmdCount = 0
prevCmd = ''
prevRegisteredCmd = ''
check = False
print(pyautogui.size())
pyautogui.FAILSAFE = False

def mouseMovement(curX, curY, command):
    global prevX, prevY, missedX, missedY, check, cmdCount, prevCmd, prevRegisteredCmd
    # code to exit when a key pressed (can make better)
    # if (curX<=0 or curY<=0 or curX>=pyautogui.size()[0] or curY>=pyautogui.size()[1])
    #     #do nothing
    pre = time.clock()
    # if keyboard.is_pressed('z'):
    #     print("i got here")
    #     sys.exit()
    # if abs(numpy.sqrt(pow(prevX - curX, 2) + pow(prevY - curY, 2)) > 5):
    #     pyautogui.moveTo(curX, curY)
    #     print(pyautogui.position())
    # elif abs(numpy.sqrt(pow(missedX - curX, 2) + pow(missedY - curY, 2)) > 5) and check == True:
    #     pyautogui.moveTo(curX, curY)
    #     print(pyautogui.position())
    #     check = False
    # else:
    #     check = True
    #     missedX = curX
    #     missedY = curY
    #
    if command == prevCmd:
        cmdCount += 1
    else:
        prevCmd = command
        cmdCount = 0

    if cmdCount == 2:
        mouse.move(curX, curY, absolute=True)
        if command != prevRegisteredCmd:
            if command == 'l':
                mouse.click('left')
            # elif command == 'n':
            #    pyautogui.mouseUp()
        prevRegisteredCmd = command
        cmdCount = 0
    post = time.clock()
    print("exec", post - pre)
    prevX = curX
    prevY = curY
    return

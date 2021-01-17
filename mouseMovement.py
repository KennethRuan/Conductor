import keyboard
import pyautogui
import sys
import numpy

prevX = 0
prevY = 0
missedX = 0
missedY = 0
cmdCount = 0
prevCmd = ''
check = False
print(pyautogui.size())


def mouseMovement(curX, curY, command):
    global prevX, prevY, missedX, missedY, check, cmdCount, prevCmd
    # code to exit when a key pressed (can make better)
    if (curX<=0 or curY<=0 or curX>=pyautogui.size()[0] or curY>=pyautogui.size()[1])
        #do nothing
    elif keyboard.is_pressed('z'):
        print("i got here")
        sys.exit()
    if abs(numpy.sqrt(pow(prevX - curX, 2) + pow(prevY - curY, 2)) > 25):
        pyautogui.moveTo(curX, curY, duration=0.5)
        print(pyautogui.position())
    elif abs(numpy.sqrt(pow(missedX - curX, 2) + pow(missedY - curY, 2)) > 25) and check == True:
        pyautogui.moveTo(curX, curY, duration=0.5)
        print(pyautogui.position())
        check = False
    else:
        check = True
        missedX = curX
        missedY = curY

    if command == prevCmd:
        cmdCount += 1
    else:
        prevCmd = command
        cmdCount = 0

    if cmdCount == 5:
        if command == 'l' and prevCmd != 'l':
            pyautogui.mouseDown(button='left')
        elif command == 'r' and prevCmd !='r':
            pyautogui.mouseDown(button='right')
        elif command == 'n' and prevCmd !='n':
            pyautogui.mouseUp()
        cmdCount = 0

    prevX = curX
    prevY = curY
    return


while True:
    print("command list: \n \'q\' to exit \n \'p\' to get current mouse position")
    print(" \'m\' to enter coordinates to move mouse to")
    command = input("choose a command: \n")
    if command == 'q':
        print("exiting")
        sys.exit()
    if command == 'p':
        print(pyautogui.position())
    if command == 'm':
        command = input(" \'l\' for left click \n \'r\' for right click \n \'n\' for none \n")
        print("enter coordinates to move to (on separate lines pls): \n")
        tryX = int(input())
        tryY = int(input())
        prevX = pyautogui.position()[0]
        prevY = pyautogui.position()[1]
        mouseMovement(tryX, tryY, command)
    print("\n \n")

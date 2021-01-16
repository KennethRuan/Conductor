#orz ronald
import keyboard
import pyautogui
import sys
import numpy

prevX = 0
prevY = 0

count = 0


def mouseMovement(curX, curY, command):
    global prevX, prevY, count
    if abs(numpy.sqrt(pow(prevX - curX, 2) + pow(prevY - curY, 2)) > 10):
        pyautogui.moveTo(curX, curY, duration=0.5)
        print(pyautogui.position())
        count = 0
    if command=='l':
        pyautogui.mouseDown(button='left') 
    elif command=='r':
        pyautogui.mouseDown(button='right') 
    elif command=='n':
        pyautogui.mouseUp()
    
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
        print(mouse.get_position())
    if command == 'm':
        command = input(" \'l\' for left click \n \'r\' for right click \n \'n\' for none \n")
        print("enter coordinates to move to (on separate lines pls): \n")
        tryX = int(input())
        tryY = int(input())
        prevX = mouse.get_position()[0]
        prevY = mouse.get_position()[1]
        mouseMovement(tryX, tryY, command)
    print("\n \n")
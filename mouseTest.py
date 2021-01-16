import mouse
prevX = 0
prevY = 0
def mouseMovement(curX, curY):
    global prevX, prevY
    #if distance between previous frame is too small, don't move
    if (curX-prevX<-10 or curX-prevX>10) or (curY-prevY<-10 or curY-prevY>10):
        mouse.move(curX-prevX, curY-prevY, absolute=False, duration=0.1)
    prevX = curX
    prevY = curY
    return

while True:
    tryX = int(input())
    tryY = int(input())
    prevX = mouse.get_position()[0]
    prevY = mouse.get_position()[1]
    mouseMovement(tryX, tryY)
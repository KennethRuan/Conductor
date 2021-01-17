import tkinter
# import pyHook
import gesture_recognition

#window setup
window = tkinter.Tk(className="Conductor - a touch-free mouse")
window.geometry("800x500")
window.configure(background='orange')
frame = tkinter.Frame(window)
frame.pack(expand=True, fill="both")
frame.configure(background='orange')

#title
title = tkinter.Text(frame, bg = 'orange', font=('Helvetica', 36), height = 1, highlightthickness = 0, borderwidth=0)
title.insert(tkinter.END, "Conductor")
title.place(x=0, y=20, width=800)
title.tag_add("idk how this works", "1.0", "1.20") #now the characters from index 0 to 20 is 'highlighted' under a tag, which is currently called "idk how this works"
title.tag_config("idk how this works", foreground="white", justify='center') #centering and setting the letters to white for the 'highlighted' characters

#start button
def clearScreen():
    global window, frame
    frame.destroy()
    print("frame destroyed")
    frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both")
    frame.configure(background='orange')
def startProgram():
    global window, frame, title
    clearScreen()

    description = tkinter.Text(frame, bg = 'orange', font=('Helvetica', 12), height = 10, width = 28, highlightthickness = 0, borderwidth=0)
    description.insert(tkinter.END, "First, you must take a picture of the background. Move out of the camera and press \'B\'. Once the background is set, move your index finger in front of the camera to see if your finger is within the background taken. If the camera captures the wrong side, press \'S\' to change the camera used.")
    description.place(relx=0.5, rely=0.5, anchor='center')
    description.tag_add("idk how this works", "1.0", "1.1000")
    description.tag_config("idk how this works", foreground="white", justify='center')
    
    gesture_recognition.recognize_gestures()


start = tkinter.Button(frame, bg = '#f5cb42', font=('Helvetica', 20), highlightthickness = 0, borderwidth=0, text ="Start", height=2, width=10, command = startProgram)
start.place(relx=0.5, rely=0.5, anchor="center")

#exit program key
# def OnKeyboardEvent(event):
#     print("keyboard pressed")
#     if (chr(event.Ascii)=='Q' or chr(event.Ascii)=='q'):
#         print("quit program")
#         quit()
#     return True
# hm = pyHook.HookManager()
# hm.KeyDown = OnKeyboardEvent
# hm.HookKeyboard()

window.mainloop()
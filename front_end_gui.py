import cv2
import tkinter

#window setup
window = tkinter.Tk(className="Conductor - a touch-free mouse")
window.geometry("800x500")
window.configure(background='orange')
frame = tkinter.Frame(window)
frame.pack(expand=True, fill="both")
frame.configure(background='orange')

#title
title = tkinter.Text(frame, bg = 'orange', font=('Times New Roman', 36), height = 1, highlightthickness = 0, borderwidth=0) #Times New Roman is a bad font for this
title.insert(tkinter.END, "Conductor")
title.place(x=0, y=20, width=800)
title.tag_add("idk how this works", "1.0", "1.20") #now the characters from index 0 to 20 is 'highlighted' under a tag, which is currently called "idk how this works"
title.tag_config("idk how this works", foreground="white", justify='center') #centering and setting the letters to white for the 'highlighted' characters

#start button
def clearScreen():
    global window, frame
    frame.destroy()
    frame = tkinter.Frame(window)
    frame.pack(expand=True, fill="both")
    frame.configure(background='orange')
def setBackground():
    clearScreen()
    

start = tkinter.Button(frame, bg = '#f5cb42', font=('Times New Roman', 20), highlightthickness = 0, borderwidth=0, text ="Start", height=2, width=10, command = setBackground)
start.place(x=320, y=200)

window.mainloop()
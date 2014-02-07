
import tkinter as tk
import tkinter.ttk as ttk


root = tk.Tk()

def printkey(event):
    print("eventdir: ", dir(event))
    print("event char: ", event.char)
    print("str ", str(event.char))
    print("repr ", repr(event.char))
    
    for k in dir(event):
        if not k.startswith("__"):
            print("%s: %r" % (k, getattr(event, k)))
    
root.bind("<Key>", printkey)
print(dir(root))
root.mainloop()
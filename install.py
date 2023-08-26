import tkinter as tk
from tkinter import filedialog


root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()

def install():
    filename = filedialog.askopenfilename(defaultextension='.exe', title="Select your Blender executable")

    # check platform...
    # windows: blender.exe

button1 = tk.Button(text='Install', command=install, bg='brown', fg='white')
canvas1.create_window(150, 150, window=button1)

root.mainloop()

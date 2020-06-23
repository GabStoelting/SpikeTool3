import matplotlib
from Controller import Controller
from tkinter import font

matplotlib.use("TkAgg")

version = "20200515-GS"

app = Controller()

scale = True # Set this to true if you want to scale all 

if scale:
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(size=24)

    default_font = font.nametofont("TkTextFont")
    default_font.configure(size=24)

    default_font = font.nametofont("TkFixedFont")
    default_font.configure(size=24)

    default_font = font.nametofont("TkMenuFont")
    default_font.configure(size=24)


app.run()

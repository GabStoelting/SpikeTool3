import matplotlib
from Controller import Controller
from tkinter import font

matplotlib.use("TkAgg")

version = "20210505-GS"

app = Controller()

scale = False  # Set this to true if you want to scale the fonts for 4K monitors

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

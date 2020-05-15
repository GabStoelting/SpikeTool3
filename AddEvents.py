import tkinter as tk
import tkSimpleDialog


class AddEvents(tkSimpleDialog.Dialog):

    def __init__(self, parent, initialValue = None):
        # Set the initialValue
        self.initialValue = initialValue
        super().__init__(parent)

    def body(self, master):
        tk.Label(master, text="Event or list of events (separated by commas):").grid(row=0, column=0)

        self.e1 = tk.Entry(master)
        # Set the Entry with the initialValue if given
        if self.initialValue != None:
            self.e1.insert(0, str(self.initialValue))
        self.e1.grid(row=0, column=1)

        return self.e1  # initial focus

    def apply(self):
        frame_str = self.e1.get()
        self.events = [int(frame) for frame in frame_str.split(sep=",")]
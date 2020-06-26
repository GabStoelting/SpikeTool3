import tkinter as tk
import tkSimpleDialog


class FindEvents_Peak(tkSimpleDialog.Dialog):

    def __init__(self, parent, select_from = None, select_to = None):
        self.select_from = select_from
        self.select_to = select_to

        super().__init__(parent)

    def body(self, master):
        if (self.select_from != None) & (self.select_to != None):
            tk.Label(master, text=f"Searching from frame {self.select_from} to {self.select_to}").grid(row=0, column=0, columnspan=2)
        else:
            tk.Label(master, text=f"Searching from first to last frame").grid(row=0, column=0)

        tk.Label(master, text="Baseline lambda:").grid(row=1, column=0)
        self.lam = tk.Entry(master)
        self.lam.grid(row=1, column=1)

        tk.Label(master, text="")

        return self.e1  # initial focus

    def validate(self):
        try:
            self.threshold = float(self.e1.get())
        except ValueError:
            tk.messagebox.showerror("Not a number", "You need to provide a numerical value!")
            return False

        return True

    def apply(self):
       self.threshold = float(self.e1.get())
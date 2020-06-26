import tkinter as tk
import tkSimpleDialog


class SubtractBaselineDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, select_from = None, select_to = None):
        self.select_from = select_from
        self.select_to = select_to

        super().__init__(parent)

    def body(self, master):

        tk.Label(master, text="Baseline lambda:").grid(row=1, column=0)
        self.e1 = tk.Entry(master)
        self.e1.grid(row=1, column=1)

        tk.Label(master, text="Baseline p:").grid(row=2, column=0)
        self.e2 = tk.Entry(master)
        self.e2.grid(row=2, column=1)

        tk.Label(master, text="Number of iterations:").grid(row=3, column=0)
        self.e3 = tk.Entry(master)
        self.e3.grid(row=3, column=1)


        return self.e1  # initial focus

    def validate(self):
        try:
            self.lam = float(self.e1.get())
            self.p = float(self.e2.get())
            self.iter = float(self.e3.get())
        except ValueError:
            tk.messagebox.showerror("Not a number", "You need to provide a numerical value!")
            return False

        return True

    def apply(self):
       self.lam = float(self.e1.get())
       self.p = float(self.e2.get())
       self.iter = int(self.e3.get())
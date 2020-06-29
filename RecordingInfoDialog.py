import tkinter as tk
import tkSimpleDialog
from tkintertable import TableCanvas, TableModel



class RecordingInfoDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, dt=0.0, **kwargs):
        self.information = None
        self.dt = None
        self.successful = False

        self.table = {"dt": {"name": "dt", "value": dt}}
        if kwargs:
            for key in kwargs.keys():
                self.table[key] = {"name": key, "value": kwargs[key]}
        else:
            self.table["animal"] = {"name": "animal", "value": 0}
            self.table["genotype"] = {"name": "genotype", "value": "wt"}
            self.table["birthdate"] = {"name": "birthdate", "value": "1900-01-01"}

        super().__init__(parent)


    def body(self, master, **kwargs):

        self.title("Information about .csv file")

        information_frame = tk.Frame(master)
        information_frame.grid(row=1, column=1)

        self.information_table = TableCanvas(information_frame, data=self.table, cols=2, rows=10, width=200)
        self.information_table.show()
        return self.information_table  # initial focus

    def validate(self):
        # Update self.information with the current data from the table

        self.information = {self.information_table.getModel().data[key]["name"]:
                                self.information_table.getModel().data[key]["value"]
                            for key in self.information_table.getModel().data}
        if not "dt" in self.information:
            tk.messagebox.showerror("No dt found.", "You need to provide a dt value!")
            self.information = None
            return False

        try:
            self.dt = float(self.information.pop("dt", None))
        except ValueError:
            tk.messagebox.showerror("dt is not numeric.", "You need to provide a numeric value for dt!")
            self.information = None
            self.dt = None
            return False

        if self.dt <= 0.0:
            tk.messagebox.showerror("dt is too small", "The dt value must be larger than 0.0!")
            self.information = None
            self.dt = None
            return False

        self.successful = True # This dialog was successful, even after validation!
        return True

#    def apply(self):
#        print(self.information)

    def cancel(self):
        self.parent.focus_set()
        self.destroy()
        return False


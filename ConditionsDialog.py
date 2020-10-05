import tkinter as tk
import tkSimpleDialog
from tkintertable import TableCanvas



class ConditionsDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, conditions=None):
        self.information = None

        # Check if conditions are given
        if conditions == None:
            self.table = {"start": {"name": "start", "c1": 0},
                          "end": {"name": "end", "c1": 1},
                          "angiotensin": {"name": "angiotensin", "c1": 100},
                          "potassium": {"name": "potassium", "c1": 4}}
        else:
            print("Load existing conditions!")
            self.table = {}
            self.table["start"] = {"name": "start"}
            self.table["end"] = {"name": "end"}

            for i, cond in enumerate(conditions):
                # Add start and end entries
                self.table["start"][f"c{i+1}"] = cond.start
                self.table["end"][f"c{i+1}"] = cond.end
                for info in cond.information:
                    # Add all other informations for this condition
                    if info not in self.table:
                        self.table[info] = {"name": info}
                    self.table[info][f"c{i+1}"] = cond.information[info]

        super().__init__(parent)


    def body(self, master, **kwargs):

        self.title("Information about .csv file")

        information_frame = tk.Frame(master)
        information_frame.grid(row=1, column=1)

        self.information_table = TableCanvas(information_frame, data=self.table, cols=5, rows=10, width=500)
        self.information_table.show()
        return self.information_table  # initial focus

    # TODO: Add a "validate" function that performs some basic sanity checks!

    def apply(self):

        self.information = {col: {self.information_table.getModel().data[key]["name"]:
                                self.information_table.getModel().data[key][col]
                            for key in self.information_table.getModel().data} for col in self.information_table.getModel().columnNames}
        self.information.pop("name") # Remove the first "name" column from the dictionary

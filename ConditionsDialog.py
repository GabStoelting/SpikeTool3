import tkinter as tk
import tkSimpleDialog
from tkintertable import TableCanvas

def flatten(input_l): 
    for l in input_l:
        if isinstance(l, list):
            yield from flatten(l)
        else:
            yield l


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
                self.table["start"][f"c{i+1}"] = int(cond.start)
                self.table["end"][f"c{i+1}"] = int(cond.end)
                for info in cond.information:
                    # Add all other informations for this condition
                    if info not in self.table:
                        self.table[info] = {"name": info}
                    self.table[info][f"c{i+1}"] = [cond.information[info]]

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

        for c in self.information:
            for key in self.information[c]:
                # Extract only the information if the entry is a list itself
                if isinstance(self.information[c][key], list):
                    # We've had problems with misbehaving lists, so
                    # flatten the list and then store the only entry
                    self.information[c][key] = list(flatten(self.information[c][key]))[0]

import tkinter as tk
import tkinter.ttk as ttk

class BaselineFrame(ttk.Frame):
    def __init__(self):
        # This is the frame for the baseline list
        super().__init__()

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=100)
        self.columnconfigure(0, weight=100)
        self.columnconfigure(1, weight=0)

        label = tk.Label(master=self, text="Baseline frames:")
        label.grid(row=0, column=0, sticky="nwe", columnspan=2)

        self.baseline_listbox = tk.Listbox(master=self, selectmode="extended", width=15, height=35)
        self.baseline_listbox.grid(row=1, column=0, sticky="nswe")

        baseline_scrollbar = tk.Scrollbar(master=self)
        baseline_scrollbar.grid(row=1, column=1, sticky="nswe")
        self.baseline_listbox.config(yscrollcommand=baseline_scrollbar.set)
        baseline_scrollbar.config(command=self.baseline_listbox.yview)

        self.menu = tk.Menu(self)

    def create_menu(self, controller):
        self.menu.add_command(label="Add selected frames to Baseline List", command=controller.add_baseline_list)
        self.menu.add_separator()
        self.menu.add_command(label="Activate Baseline Frames", command=controller.activate_baseline)
        self.menu.add_command(label="Inactivate Baseline Frames", command=controller.inactivate_baseline)

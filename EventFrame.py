import tkinter as tk
import tkinter.ttk as ttk


class EventFrame(ttk.Frame):
    def __init__(self):
        # This is the frame for the event list
        super().__init__()

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=100)
        self.columnconfigure(0, weight=100)
        self.columnconfigure(1, weight=0)

        label = tk.Label(master=self, text="Events:")
        label.grid(row=0, column=0, sticky="nwe", columnspan=2)

        self.event_listbox = tk.Listbox(master=self, selectmode="extended", width=15, height=35)
        self.event_listbox.grid(row=1, column=0, sticky="nswe")

        event_scrollbar = tk.Scrollbar(master=self)
        event_scrollbar.grid(row=1, column=1, sticky="nswe")
        self.event_listbox.config(yscrollcommand=event_scrollbar.set)
        event_scrollbar.config(command=self.event_listbox.yview)
        self.menu = tk.Menu(self)

    def create_menu(self, controller):
        self.menu.add_command(label="Activate Events", command=controller.activate_event)
        self.menu.add_command(label="Inactivate Event", command=controller.inactivate_event)
        self.menu.add_separator()
        self.menu.add_command(label="Add Single Event", command=controller.add_event_single)

    def event_menu_state(self, state="disabled"):
        self.filemenu.entryconfig("Add Single Event", state=state)

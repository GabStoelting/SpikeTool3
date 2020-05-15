import tkinter as tk
import tkinter.ttk as ttk

class EventFrame(ttk.Frame):
    def __init__(self):
        # This is the frame for the event list
        super().__init__()

        eventview_frame = ttk.Frame(master=self)
        eventview_frame.grid(row=1, column=0, sticky="nswe")

        label = tk.Label(master=eventview_frame, text="Events:")
        label.pack(side="top", fill=tk.BOTH, expand=True)

        self.event_listbox = tk.Listbox(master=eventview_frame, selectmode="extended", width=15, height=35)
        self.event_listbox.pack(side="left", fill=tk.BOTH, expand=True)

        event_scrollbar = tk.Scrollbar(master=eventview_frame)
        event_scrollbar.pack(side="right", fill=tk.BOTH, expand=True)
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


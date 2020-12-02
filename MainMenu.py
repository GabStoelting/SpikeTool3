import tkinter as tk

class MainMenu(tk.Menu):

    def __init__(self, parent):
        self.parent = parent
        super().__init__()


        self.filemenu = tk.Menu(self)
        self.add_cascade(label="File", menu=self.filemenu)

        self.eventmenu = tk.Menu(self)
        self.add_cascade(label="Events", menu=self.eventmenu)
        
        self.baselinemenu = tk.Menu(self)
        self.add_cascade(label="Baseline", menu=self.baselinemenu)


    def create_menu(self, parent):
        self.filemenu.add_command(label="New Pickle...", command=parent.new_file)
        self.filemenu.add_command(label="Open Pickle...", command=parent.open_file)
        self.filemenu.add_command(label="Save as Pickle...", command=parent.save_file)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Add .csv File", command=parent.add_csv)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Create .pdf Overview", command=parent.create_pdf)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=parent.quit)

        self.eventmenu.add_command(label="Find Events by Threshold", command=parent.find_events)
        self.eventmenu.add_command(label="Subtract Baseline", command=parent.subtract_baseline)
        self.eventmenu.add_command(label="Add Event List", command=parent.add_event_list)
        self.eventmenu.add_separator()
        self.eventmenu.add_command(label="Delete Event(s)", command=parent.delete_event_list)

        self.baselinemenu.add_command(label="Add selected frames to Baseline List", command=parent.add_baseline_list)
        self.baselinemenu.add_separator()
        self.baselinemenu.add_command(label="Activate Baseline Frames", command=parent.activate_baseline)
        self.baselinemenu.add_command(label="Inactivate Baseline Frames", command=parent.inactivate_baseline)


        # Disable all menu entries which can only be accessed if a file has been opened
        self.recording_menu_state(state="disabled")

    def recording_menu_state(self, state="disabled"):
        self.filemenu.entryconfig("Add .csv File", state=state)
        self.filemenu.entryconfig("Create .pdf Overview", state=state)
        self.filemenu.entryconfig("Save as Pickle...", state=state)
        self.eventmenu.entryconfig("Subtract Baseline", state=state)
        self.eventmenu.entryconfig("Find Events by Threshold", state=state)
        self.eventmenu.entryconfig("Add Event List", state=state)
        self.eventmenu.entryconfig("Delete Event(s)", state=state)
        self.baselinemenu.entryconfig("Add selected frames to Baseline List", state=state)
        self.baselinemenu.entryconfig("Activate Baseline Frames", state=state)
        self.baselinemenu.entryconfig("Inactivate Baseline Frames", state=state)

import tkinter as tk
import tkinter.ttk as ttk

class NavigationFrame(ttk.Frame):
    def __init__(self):
        super().__init__()

        # This is the whole "navigation frame" on the left
        # The treeview will be put in its own frame

        # This is for the foreground/background work around
        style = ttk.Style()
        style.map("Treeview",
                  foreground=self.fixed_map("foreground"),
                  background=self.fixed_map("background"))

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=100)
        self.columnconfigure(0, weight=100)
        self.columnconfigure(1, weight=0)

        label = tk.Label(master=self, text="Recordings:")
        label.grid(row=0, column=0, sticky="nwe", columnspan=2)

        self.tree = ttk.Treeview(master=self, height=25)
        self.tree.tag_configure('recording', foreground="black")
        self.tree.tag_configure('active_cell', foreground="black")
        self.tree.tag_configure('active_cell_has_events', foreground="green")
        self.tree.tag_configure('inactive_cell', foreground="gray")
        self.tree.grid(row=1, column=0, sticky="nswe")


        tree_scrollbar = tk.Scrollbar(master=self)
        tree_scrollbar.grid(row=1, column=1, sticky="nswe")

        self.tree.config(yscrollcommand=tree_scrollbar.set)
        tree_scrollbar.config(command=self.tree.yview)

        self.menu = tk.Menu(self)

    def create_menu(self, controller):
        # Create context menu for the navigation TreeView
        self.menu.add_command(label="Edit Recording Information",
                                                    command=controller.show_recording_information)
        self.menu.add_command(label="Edit Conditions",
                                                    command=controller.show_conditions_dialog)
        self.menu.add_separator()
        self.menu.add_command(label="Activate Cell",
                                                    command=controller.activate_cell)
        self.menu.add_command(label="Inactivate Cell",
                                                    command=controller.inactivate_cell)
        self.menu.add_separator()
        self.menu.add_command(label="Remove Recording",
                                                    command=controller.remove_recording)

    def navigation_menu_state(self, state="disabled"):
        self.menu.entryconfig("Edit Recording Information", state=state)
        self.menu.entryconfig("Remove Recording", state=state)


    # This function is a necessary workaround to get foreground and background colors
    # in the TreeView
    # Source: https://core.tcl-lang.org/tk/tktview?name=509cafafae (last read on 2020-02-28)
    def fixed_map(self, option):
        style = ttk.Style()
        # Returns the style map for 'option' with any styles starting with
        # ("!disabled", "!selected", ...) filtered out

        # style.map() returns an empty list for missing options, so this should
        # be future-safe
        return [elm for elm in style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]
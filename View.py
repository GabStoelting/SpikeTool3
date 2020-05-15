from NavigationFrame import NavigationFrame
from EventFrame import EventFrame
from GraphFrame import GraphFrame
from MainMenu import MainMenu


class View:
    def __init__(self, parent, controller):

        self.parent = parent
        self.controller = controller

        self.menu = MainMenu(self.parent)
        self.parent.config(menu=self.menu)

        self.navigation_frame = NavigationFrame()
        self.navigation_frame.grid(row=0, column=0, sticky="nsw", padx=5)

        self.event_frame = EventFrame()
        self.event_frame.grid(row=0, column=1, sticky="nsw", padx=5)

        self.graph_frame = GraphFrame(controller=self.controller)
        self.graph_frame.grid(row=0, column=2, sticky="nswe", padx=5, pady=5)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(1, weight=1)
        self.parent.columnconfigure(2, weight=10)


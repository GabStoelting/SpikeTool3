import tkinter as tk
import tkinter.ttk as ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import SpanSelector


class MyToolbar(NavigationToolbar2Tk):
    def __init__(self, figure_canvas, parent=None):
        self.parent = parent

        self.toolitems = (('Home', 'Reset view', 'home', 'home'),
                          (None, None, None, None),
                          ('Subplots', 'Subplot settings', 'subplots', 'configure_subplots'),
                          ('Save', 'Save as figure...', 'filesave', 'save_figure'),
                          (None, None, None, None),
                          ('Pan', 'Pan', 'move', 'pan'),
                          ('Zoom', 'Zoom', 'zoom_to_rect', 'zoom'),
                          )

        super().__init__(figure_canvas, parent)

        self.select = False
        self.select_icon = tk.PhotoImage(file = r"range.png")
        self.select_icon = self.select_icon.subsample(16) # Resize icon
        self.select_button = tk.Button(self, text="Select", image=self.select_icon, command=self.change_select)
        self.select_button.pack(side="left")

        self.synchronize = tk.IntVar()
        c = tk.Checkbutton(self, text="Synchronize", variable=self.synchronize, command=self.change_synchronization)
        c.pack(side="left")

        self.show_conditions = tk.IntVar()

        c = tk.Checkbutton(self, text="Show conditions", variable=self.show_conditions,
                           command=self.change_show_conditions)
        c.pack(side="left")

        self.show_events = tk.IntVar(value=1)
        self.show_baseline = tk.IntVar(value=1)
    
        c = tk.Checkbutton(self, text="Show events", variable=self.show_events,
                           command=self.change_show_events)
        c.pack(side="left")

        c = tk.Checkbutton(self, text="Show baseline", variable=self.show_baseline,
                           command=self.change_show_baseline)
        c.pack(side="left")

        tk.Label(master=self, text="From: ").pack(side="left")
        self.select_from = tk.Entry(master=self, width=6)
        self.select_from.pack(side="left")
        tk.Label(master=self, text="To: ").pack(side="left")
        self.select_to = tk.Entry(master=self, width=6)
        self.select_to.pack(side="left")
        self.update()

        self.cancel_select_icon = tk.PhotoImage(file = r"range_cancel.png")
        self.cancel_select_icon = self.cancel_select_icon.subsample(16) # Resize icon
        self.cancel_select_button = tk.Button(self, text="Cancel selection", image=self.cancel_select_icon, command=self.cancel_select)
        self.cancel_select_button.pack(side="left")


    def change_synchronization(self):
        # This function synchronizes or unsynchronizes the view of the two graphs (raw/di)
        if self.synchronize.get():
            self.parent.synchronize_axes(True)
        else:
            self.parent.synchronize_axes(False)

    def change_show_conditions(self):
        # This function turns the display of the conditions on or off
        if self.show_conditions.get():
            self.parent.show_conditions()
        else:
            self.parent.show_conditions()

    def change_show_events(self):
        if self.show_events.get():
            self.parent.show_events(True)
        else:
            self.parent.show_events(False)

    def change_show_baseline(self):
        if self.show_baseline.get():
            self.parent.show_baseline(True)
        else:
            self.parent.show_baseline(False)

    def cancel_select(self):
        self.parent.controller.cancel_selection()

    def change_select(self):
        if self.select: # Run if "select" has been pressed before
            self.select_button.configure(relief=tk.RAISED)
            self.parent.spansel.active = False

            self.select = False # Change state
        else: # Run if "select" hasn't been pressed before
            self.select_button.configure(relief=tk.SUNKEN)
            self.parent.spansel.active = True

            if self.mode == "zoom rect": # Check if the zoom button has previously been pressed
                self.zoom() # Disable zoom selection
            elif self.mode == "pan/zoom": # Check if the pan button has been pressed
                self.pan() # Disable pan selection

            self.select = True # Change state

    def zoom(self, *args): # Override the internal zoom() function to change the state of "select"
        if self.select == True:
            self.change_select()
        super().zoom(args) # Run native zoom()

    def pan(self, *args): # Override the internal pan() function to change the state of "select"
        if self.select == True:
            self.change_select()
        super().pan(args) # Run native pan()


class GraphFrame(ttk.Frame):
    def __init__(self, master=None, controller=None):
        super().__init__(master=master)

        self.controller = controller

        self.fig = plt.figure(figsize=(5, 5))

        # Create the graph for the raw view
        self.raw_ax = self.fig.add_subplot(211)
        # Remove the display of the coordinates:
        self.raw_ax.format_coord = lambda x, y: ""  # f"Frame: {'{:06.0f}'.format(x)}, Value: {'{:09.2f}'.format(y)}"

        # Create the graph for the approximation of the first derivative
        self.di_ax = self.fig.add_subplot(212)
        # Remove the display of the coordinates:
        self.di_ax.format_coord = lambda x, y: ""

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.toolbar = MyToolbar(self.canvas, parent=self)
        self.toolbar.update()

        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)

        # Setup the span selector
        rectprops = dict(facecolor='blue', alpha=0.5)
        self.spansel = SpanSelector(self.raw_ax, self.controller.onselect, 'horizontal', rectprops=rectprops, useblit=True)
        self.spansel.active = False

        # Connect the mouse button pressed and released events to the controller
        #self.canvas.mpl_connect('button_press_event', self.controller.graph_mouse_pressed)
        self.canvas.mpl_connect('button_release_event', self.controller.graph_mouse_released)

    def synchronize_axes(self, sync=True):
        if sync:
            self.raw_ax.get_shared_x_axes().join(self.raw_ax, self.di_ax)
        else:
            self.raw_ax.get_shared_x_axes().remove(self.di_ax)

    def show_conditions(self):
        self.controller.view_refresh()

    def show_events(self):
        self.controller.view_refresh()
        
    def show_baseline(self):
        self.controller.view_refresh()

    def show_selection_cursor(self):
        self.spansel.active = True

    def hide_selection_cursor(self):
        self.spansel.active = False

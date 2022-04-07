import pickle
import tkinter as tk
import pandas as pd
from pathlib import Path
from calim import *
from View import View
from FindEvents import FindEvents
from AddEvents import AddEvents
from RecordingInfoDialog import RecordingInfoDialog
from ConditionsDialog import ConditionsDialog
from PDFOverview import CreatePDF
from SubtractBaselineDialog import SubtractBaselineDialog
import platform

class Controller:
    def __init__(self):
        self.root = tk.Tk()

        self.pickle = None
        self.selected_cell = None
        self.selected_recording = None
        self.view = View(parent=self.root, controller=self)
        self.setup_events()
        self.setup_menu()
        self.selected_events = None
        self.event_lines_raw = None
        self.event_lines_di = None
        self.condition_lines_raw = None
        self.condition_lines_di = None
        self.condition_text_raw = None
        self.condition_text_di = None

        self.selected_baseline = None
        self.baseline_lines = None
        self.baseline_selected_lines = None
        
        self.select_state = 0
        self.select_from = None
        self.select_to = None
        self.select_lines = []

        self.last_threshold = 1000.0

    def run(self):
        self.root.title("Spike Tool")
        self.root.deiconify()
        self.root.mainloop()

    # This function links buttons to functions
    def setup_events(self):

        # Check if the operating system is "Darwin" (MacOS) to determine which
        # mouse key to bind for right-click (Button-2 for MacOS; Button-3 for everything else)

        if platform.system() == "Darwin":
            right_click = "<Button-2>"
        else:
            right_click = "<Button-3>"

        # Bind events from the NavigationFrame to commands
        self.view.navigation_frame.tree.bind("<Button-1>", self.tree_clicked)

        # Bind event context menu to ListBox
        self.view.event_frame.event_listbox.bind(right_click, self.event_context_clicked)
        
        # Bind baseline context menu to ListBox
        self.view.baseline_frame.baseline_listbox.bind(right_click, self.baseline_context_clicked)

        # Bind event context menu to ListBox
        self.view.navigation_frame.tree.bind(right_click, self.tree_context_clicked)

        # Bind the selection of one or more events
        self.view.event_frame.event_listbox.bind('<<ListboxSelect>>', self.event_list_select_event)

        # Bind the selection of one or more events
        self.view.baseline_frame.baseline_listbox.bind('<<ListboxSelect>>', self.baseline_list_select_baseline)
        
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        # Right now, this just quits everything
        # TODO: Add some safety checks
        self.root.destroy()

    def setup_menu(self):

        # Create menu and binding for the main menu bar
        self.view.menu.create_menu(self)

        # Create context menu for the events ListBox
        self.view.event_frame.create_menu(self)
        
        # Create context menu for the baseline ListBox
        self.view.baseline_frame.create_menu(self)

        self.view.navigation_frame.create_menu(self)

    def new_file(self):
        self.pickle = Project()
        if not self.add_csv():
            tk.messagebox.showerror("No csv file selected.", "You need to add a csv file initially!")
            self.pickle = None
            return False
        self.view.menu.recording_menu_state(state="normal")  # Activate menus

    def open_file(self):
        filename = tk.filedialog.askopenfilename(filetypes=(("HDF5 File", "*.hdf"), ("Python Pickle", "*.pkl"), ("All Files", "*.*")),
                                                 title="Choose a file.")
        if not filename:
            return False
       
        if filename.lower().endswith(".pkl"):
            self.pickle = pickle.load(open(filename, "rb"))
        elif filename.lower().endswith(".hdf"):
            self.pickle = Project()
            self.pickle.from_hdf(filename)
        else:
            return False
                   
        self.root.title(f"Spike Tool {filename}")    

        self.view.menu.recording_menu_state(state="normal")  # Activate menus
        self.tree_redraw()

    def save_file(self):
        # Ask for a filename for the pickle to be saved at
        filename = tk.filedialog.asksaveasfilename(defaultextension=".hdf", filetypes=(("HDF5 File", "*.hdf"), ("Python Pickle", "*.pkl"), ("All Files", "*.*")),
                                                   title="Choose a file.")        
        if not filename:
            return False
        
        if filename.lower().endswith(".pkl"):
            pickle.dump(self.pickle, open(filename, "wb"))
        elif filename.lower().endswith(".hdf"):
            self.pickle.to_hdf(filename)
        else:
            filename = filename+".hdf"
            self.pickle.to_hdf(filename)
        
        self.root.title(f"Spike Tool {filename}")    

    def append_file(self):
        filename = tk.filedialog.askopenfilename(filetypes=(("HDF5 File", "*.hdf"), ("Python Pickle", "*.pkl"), ("All Files", "*.*")),
                                                 title="Choose a file.")
        if not filename:
            return False
       
        if filename.lower().endswith(".pkl"):
            project = pickle.load(open(filename, "rb"))
        elif filename.lower().endswith(".hdf"):
            project = Project()
            project.from_hdf(filename)
        else:
            return False
        for recording in project.recordings:
            self.pickle.append(project.recordings[recording])

        self.view.menu.recording_menu_state(state="normal")  # Activate menus
        self.tree_redraw()
		
    def show_recording_information(self):
        # This opens the recording information table
        if not self.selected_recording:
            return

        # It should not happen that the information is not filled out but if this happens
        # we should just try to create a new information
        if not self.pickle.recordings[self.selected_recording].information:
            d = RecordingInfoDialog(self.root)
        else:
            d = RecordingInfoDialog(self.root, dt=self.pickle.recordings[self.selected_recording].dt,
                                    **self.pickle.recordings[self.selected_recording].information)
        # Only update if the information was validated!
        if d.successful:
            self.pickle.recordings[self.selected_recording].information = d.information
            self.pickle.recordings[self.selected_recording].dt = d.dt

    def show_conditions_dialog(self):
        # This opens the recording information table
        if not self.selected_recording:
            return

        # Create a new condition entry if there is none already
        if not self.pickle.recordings[self.selected_recording].conditions:
            d = ConditionsDialog(self.root)
        else:
            d = ConditionsDialog(self.root, conditions=self.pickle.recordings[self.selected_recording].conditions)
            # Reset the existing Conditions if values are passed on:
            if d.information:
                self.pickle.recordings[self.selected_recording].conditions = []

        # Now put the new or changed conditions into the file
        if d.information:
            # Delete old conditions in recording
            self.pickle.recordings[self.selected_recording].conditions = []
            for cell in self.pickle.recordings[self.selected_recording].cells:
                self.pickle.recordings[self.selected_recording].cells[cell].conditions = []
            for condition in d.information:
                if d.information[condition]["end"] == "end":
                    d.information[condition]["end"] = len(self.pickle.recordings[self.selected_recording])
                self.pickle.recordings[self.selected_recording].add_condition(**d.information[condition])

    def add_csv(self):
        # Add a .csv file to the current pickle file
        if self.pickle:
            csv_filepath = tk.filedialog.askopenfilename(filetypes=(("CSV-File", "*.csv"), ("All Files", "*.*")),
                                                         title="Choose a file.")
            if not csv_filepath:
                return False
            csv_filename = Path(csv_filepath).name
            csv_file = pd.read_csv(csv_filepath, index_col=0)

            d = RecordingInfoDialog(self.root)

            experiment = Recording(file_id=csv_filename, dt=d.dt, raw_data=csv_file, **d.information)
            self.pickle.append(experiment)
            self.tree_redraw()
            return True
        else:
            tk.messagebox.showerror("No PKL loaded", "You need to load a pickle file first!")
            return False

    def create_pdf(self):
        if self.pickle:
            CreatePDF(self.root, self.pickle)

    def find_events(self):
        # Search for events by thresholding of the approximated first derivative of the raw trace
        # Only run if a pickle has been loaded or created
        if not self.pickle:
            return

        d = FindEvents(parent=self.root, select_from=self.select_from, select_to=self.select_to, last_threshold=self.last_threshold)

        # See if d.threshold exists
        try:
            d.threshold
        except AttributeError:
            d.threshold = 0.0

        # only proceed if the threshold is larger than 0.0
        if d.threshold <= 0.0:
            return

        self.last_threshold = d.threshold
        
        # Check and ask if the cell already has events assigned
        if self.selected_cell.has_events(self.select_from, self.select_to):
            msg_box = tk.messagebox.askyesno("Overwrite Events?", "This cell may already contain events within the \
                                            chosen range. Do you want to replace the potentially existing events?")
            if msg_box:
                if self.select_from and self.select_to:
                    self.selected_cell.reset_events(start=self.select_from, end=self.select_to)
                else:
                    self.selected_cell.reset_events()
            else:
                return

        # Find events and redraw all necessary views
        events = self.selected_cell.find_events(cutoff=d.threshold, start=self.select_from, end=self.select_to)
        self.selected_cell.add_events(events)

        self.event_list_rebuild()
        #self.view_rebuild(retain_zoom=True)
        #self.event_view_rebuild()
        self.view_refresh()
        self.selected_events = None

    def subtract_baseline(self):
        if not self.pickle:
            return

        d = SubtractBaselineDialog(parent=self.root)
        self.selected_cell.subtract_baseline(d.lam, d.p, d.iter)

    def delete_event_list(self):
        # Search for events by thresholding of the approximated first derivative of the raw trace
        # Only run if a pickle has been loaded or created
        if not self.pickle:
            return

        if not self.selected_events:
            print("No events selected. 1")
        elif self.selected_events == []:
            print("No events selected. 2")

        # Check and ask if events shall really be deleted
        MsgBox = tk.messagebox.askyesno("Delete Events?", "Do you really want to delete the selected events?")
        if MsgBox:
            if self.select_from and self.select_to:
                self.selected_cell.delete_events(
                    [self.selected_cell.events[i].frame for i in self.selected_events])
        else:
            return

        # Redraw all necessary views
        self.event_list_rebuild()
        #self.view_rebuild(retain_zoom=True)
        #self.event_view_rebuild()
        self.view_refresh()
        self.selected_events = None

    def tree_clicked(self, event):
        # TODO: Change appearance of currently selected item

        # Handle selections of the TreeView
        cell = self.view.navigation_frame.tree.identify('item', event.x, event.y)
        rec = self.view.navigation_frame.tree.parent(cell)
        cell = self.view.navigation_frame.tree.item(cell)["text"]

        # Check if the selected entry is a cell or a recording
        # if rec is set, a cell has been selected
        if rec:
            self.selected_recording = rec
            self.selected_cell = self.pickle.recordings[self.selected_recording].cells[cell]
            self.view.navigation_frame.navigation_menu_state(state="disabled")
        else:
            self.selected_recording = cell
            self.selected_cell = None
            self.view.navigation_frame.navigation_menu_state(state="normal")

            # TODO: Clear the graphs!
            return

        # This should only be run if a cell was selected!
        self.event_list_rebuild()
        self.baseline_list_rebuild()
        self.view_rebuild()
        self.view_refresh()

    def tree_context_clicked(self, event):
        self.view.navigation_frame.menu.post(event.x_root, event.y_root)

    def tree_redraw(self):
        # Delete old entries
        self.view.navigation_frame.tree.delete(*self.view.navigation_frame.tree.get_children())

        # Fill the TreeView with the recordings
        for rec in self.pickle.recordings:
            self.view.navigation_frame.tree.insert("", "end", rec, text=rec, tags=("recording",))
            # Add the cells below the recording, assign different labels for active or inactive cells
            for cell in self.pickle.recordings[rec].cells:
                if self.pickle.recordings[rec].cells[cell].use:
                    if self.pickle.recordings[rec].cells[cell].has_events():
                        self.view.navigation_frame.tree.insert(rec, "end", rec+"/"+cell, text=cell, tags=("active_cell_has_events",))
                    else:
                        self.view.navigation_frame.tree.insert(rec, "end", rec+"/"+cell, text=cell, tags=("active_cell",))
                else:
                    self.view.navigation_frame.tree.insert(rec, "end", rec+"/"+cell, text=cell, tags=("inactive_cell",))
    
    def tree_update(self, tag):
        current_selection = self.view.navigation_frame.tree.selection()[0]
        #current_index = self.view.navigation_frame.tree.index(current_selection)

        self.view.navigation_frame.tree.item(current_selection, tags=(tag, ))

    def event_context_clicked(self, event):
        # Show the context menu in the event list when clicked
        self.view.event_frame.menu.post(event.x_root, event.y_root)

    def baseline_context_clicked(self, event):
        # Show the context menu in the baseline list when clicked
        self.view.baseline_frame.menu.post(event.x_root, event.y_root)

    def view_rebuild(self, retain_zoom=False):
        # This clears the graphs and plots the data again
        current_xlim = self.view.graph_frame.raw_ax.get_xlim()
        current_ylim = self.view.graph_frame.raw_ax.get_ylim()
        self.view.graph_frame.raw_ax.clear()
        self.view.graph_frame.raw_ax.plot(range(0, len(self.selected_cell.raw_data)), self.selected_cell.raw_data)

        self.view.graph_frame.di_ax.clear()
        self.view.graph_frame.di_ax.plot(range(1, len(self.selected_cell.raw_data)), self.selected_cell.get_di())

        # Set the old zoom again if desired
        if retain_zoom:
            self.view.graph_frame.raw_ax.set_xlim(current_xlim)
            self.view.graph_frame.raw_ax.set_ylim(current_ylim)

        # draw all changes
        self.view.graph_frame.canvas.draw()

    def view_refresh(self):
        # Call this function if everything on top of the raw trace should be refreshed
        self.view_event_refresh()
        self.view_baseline_refresh()
        self.view_condition_refresh()
        self.view.graph_frame.canvas.draw()
        #tk.messagebox.showinfo(title="refresh", message=f"refresh done")


    def view_baseline_refresh(self):
        # This function replots all baseline lines
        if self.selected_recording and self.selected_cell:

            if len(self.selected_cell.baseline) > 0:

                # Remove all old lines from the raw graph
                if self.baseline_lines:
                    for line in self.baseline_lines:
                        line.remove()

                self.baseline_lines = []
                                      
                self.baseline_lines.append(
                    self.view.graph_frame.raw_ax.scatter(
                        [self.selected_cell.baseline[i].frame for i in range(len(self.selected_cell.baseline)) if self.selected_cell.baseline[i].use],
                            [[0.7] for j in range(len(self.selected_cell.baseline)) if self.selected_cell.baseline[j].use], color="purple"))
                            
                self.baseline_lines.append(
                    self.view.graph_frame.raw_ax.scatter(
                        [self.selected_cell.baseline[i].frame for i in range(len(self.selected_cell.baseline)) if self.selected_cell.baseline[i].use==False],
                            [[0.7] for j in range(len(self.selected_cell.baseline)) if self.selected_cell.baseline[j].use==False], color="gray"))      
                            
                            
                            
    def view_event_refresh(self):
        # This function replots all events
        if self.selected_recording and self.selected_cell:
            if len(self.selected_cell.events) > 0:

                # Remove all old lines from the raw graph
                if self.event_lines_raw:
                    for line in self.event_lines_raw:
                        line.remove()

                # Remove all old lines from the di graph
                if self.event_lines_di:
                    for line in self.event_lines_di:
                        line.remove()


                self.event_lines_raw = []
                self.event_lines_di = []


                if self.view.graph_frame.toolbar.show_events.get():
                    for i, event in enumerate(self.selected_cell.events):

                        if event.use:
                            self.event_lines_raw.append(
                                self.view.graph_frame.raw_ax.axvline(int(event.frame), lw=0.5, color="green"))
                            self.event_lines_di.append(
                                self.view.graph_frame.di_ax.axvline(int(event.frame), lw=0.5, color="green"))
                        else:
                            self.event_lines_raw.append(
                                self.view.graph_frame.raw_ax.axvline(int(event.frame), lw=0.2, color="gray"))
                            self.event_lines_di.append(
                                self.view.graph_frame.di_ax.axvline(int(event.frame), lw=0.2, color="gray"))
                                

    def view_condition_refresh(self):
        # This function refreshes the displayed information about conditions

        # remove condition information from raw graph
        if self.condition_lines_raw:
            for line in self.condition_lines_raw:
                line.remove()
        if self.condition_text_raw:
            for text in self.condition_text_raw:
                text.remove()
        # remove condition information from di graph
        if self.condition_lines_di:
            for line in self.condition_lines_di:
                line.remove()
        if self.condition_text_di:
            for text in self.condition_text_di:
                text.remove()

        self.condition_lines_raw = []
        self.condition_lines_di = []
        self.condition_text_raw = []
        self.condition_text_di = []
        # Show condition boundaries if the checkbox is set
        if self.view.graph_frame.toolbar.show_conditions.get():
            for condition in self.pickle.recordings[self.selected_recording].conditions:
                self.condition_lines_raw.append(
                self.view.graph_frame.raw_ax.axvline(int(condition.end), lw=1.0, color="red"))
                self.condition_lines_di.append(
                self.view.graph_frame.di_ax.axvline(int(condition.end), lw=1.0, color="red"))
                condition_info = f"Start: {condition.start}\nEnd: {condition.end}\n"

                for ci in condition.information:
                    condition_info = condition_info+f"{ci}: {condition.information[ci]}\n"
                self.condition_text_raw.append(
                    self.view.graph_frame.raw_ax.text(int(condition.start), self.view.graph_frame.raw_ax.get_ylim()[0], condition_info, fontsize=8))

    def view_event_update(self, event_i, color, lw=0.2):
        # This function only changes a subset of the events
        [self.event_lines_raw[i].set_color(color) for i in event_i]
        [self.event_lines_raw[i].set_linewidth(lw) for i in event_i]

        [self.event_lines_di[i].set_color(color) for i in event_i]
        [self.event_lines_di[i].set_linewidth(lw) for i in event_i]

        self.view.graph_frame.canvas.draw()

    def view_event_reset(self, event_i):
        if len(event_i) > 0:
            if event_i[-1] < len(self.selected_cell.events): #only reset view  selected of events that actually exist in the event list of the selected cell
                for i in event_i:
                    event = self.selected_cell.events[i]
                    if event.use:
                        self.event_lines_raw[i].set_color("green")
                        self.event_lines_di[i].set_color("green")
                        self.event_lines_raw[i].set_linewidth(0.5)
                        self.event_lines_di[i].set_linewidth(0.5)
                    else:
                        self.event_lines_raw[i].set_color("gray")
                        self.event_lines_di[i].set_color("gray")
                        self.event_lines_raw[i].set_linewidth(0.2)
                        self.event_lines_di[i].set_linewidth(0.2)

    def event_list_rebuild(self):
        self.view.event_frame.event_listbox.delete(0, "end")
        for i, event in enumerate(self.selected_cell.events):
            if event.use:
                self.view.event_frame.event_listbox.insert("end", f"{event.frame}")
            else:
                self.view.event_frame.event_listbox.insert("end", f"{event.frame}")
                self.view.event_frame.event_listbox.itemconfig(i, {"fg": "grey"})
                            
    def baseline_list_rebuild(self):
        try:
            self.view.baseline_frame.baseline_listbox.delete(0, "end")
            for i, baseline in enumerate(self.selected_cell.baseline):
                if baseline.use:
                    self.view.baseline_frame.baseline_listbox.insert("end", f"{baseline.frame}")
                else:
                    self.view.baseline_frame.baseline_listbox.insert("end", f"{baseline.frame}")
                    self.view.baseline_frame.baseline_listbox.itemconfig(i, {"fg": "grey"})
        except AttributeError:
            self.selected_cell.baseline = []


    def event_list_select_event(self, event):
        
        # This function updates the list of selected events
        # and redraws the graph to highlight those

        # First reset the old events to their colors
        if self.selected_events is not None:
            self.view_event_reset(self.selected_events)

        # Read the selected events from the listbox
        self.selected_events = ([i for i in self.view.event_frame.event_listbox.curselection()])

        # Change the color of the selected events to red
        if self.selected_events is not None:
            self.view_event_update(self.selected_events, "red", lw=1.0)

    def baseline_list_select_baseline(self, event):
        # This function updates the list of selected baseline frames
        # and redraws the graph to highlight those

        # First reset the old baseline frames to their colors
        #if self.selected_baseline is not None:
        #    self.view_baseline_reset(self.selected_baseline)

        # Read the selected baseline frames from the listbox
        self.selected_baseline = ([i for i in self.view.baseline_frame.baseline_listbox.curselection()])


        # Change the color of the selected baseline frames plot
        if self.baseline_selected_lines:
            for line in self.baseline_selected_lines:
                line.remove()

        self.baseline_selected_lines = []
                                              
        self.baseline_selected_lines.append(
            self.view.graph_frame.raw_ax.scatter(
                [item.frame for i, item in enumerate(self.selected_cell.baseline) if i in self.selected_baseline],
                    [[0.6] for j, item in enumerate(self.selected_cell.baseline) if j in self.selected_baseline], color="pink"))
                    
        self.view.graph_frame.canvas.draw()

                        

    def add_event_list(self):
        d = AddEvents(self.root)
        # Find events and redraw all necessary views
        self.selected_cell.add_events(d.events)
        self.event_list_rebuild()

        self.view_refresh()

    def add_event_single(self):
        if self.select_from == self.select_to:
            self.selected_cell.reset_events(self.select_from, self.select_to)
            self.selected_cell.add_events(self.select_from)
            self.event_list_rebuild()
            self.view_refresh()
        else:
            self.selected_cell.reset_events(self.select_from, self.select_to)
            self.selected_cell.add_events([self.select_from, self.select_to])
            self.event_list_rebuild()
            self.view_refresh()



    def add_baseline_list(self):        
        self.selected_cell.reset_baseline(self.select_from, self.select_to)
        self.selected_cell.add_baseline(list(range(self.select_from, self.select_to)))
        self.baseline_list_rebuild()
        self.view_refresh()

    def inactivate_event(self):
        if self.selected_events is not None:
            selected_frames = ([self.selected_cell.events[i].frame
                                for i in self.selected_events])
            self.selected_cell.reject_event(selected_frames)
            self.event_list_rebuild()
            self.view_event_update(self.selected_events, "gray")

        else:
            tk.messagebox.showerror("No cell selected.", "You need to select a cell first!")
            return

    def inactivate_baseline(self):
        if self.selected_baseline is not None:
            selected_frames = ([self.selected_cell.baseline[i].frame
                                for i in self.selected_baseline])
            self.selected_cell.reject_baseline(selected_frames)
            self.baseline_list_rebuild()
            self.view_baseline_refresh()
            self.view.graph_frame.canvas.draw()

            #self.view_baseline_update(self.selected_events, "gray")

        else:
            tk.messagebox.showerror(title="selected baseline", message=f"!--{self.selected_baseline}--!")
            tk.messagebox.showerror("Inactivations: No baseline frames selected.", "You need to select baseline frames first!")
            return

    def inactivate_cell(self):
        if self.selected_cell is not None:
            self.selected_cell.reject()
            self.tree_update("inactive_cell")

    def activate_cell(self):
        if self.selected_cell is not None:
            self.selected_cell.accept()
            if self.selected_cell.has_events():
                self.tree_update("active_cell_has_events")
            else:
                self.tree_update("active_cell")

    def activate_event(self):
        if self.selected_events is not None:
            selected_frames = ([self.selected_cell.events[i].frame
                                for i in self.selected_events])
            self.selected_cell.activate_event(selected_frames)
            self.event_list_rebuild()
            self.view_event_update(self.selected_events, "green", lw=0.5)
        else:
            tk.messagebox.showerror("No cell selected.", "You need to select a cell first!")
            return

    def activate_baseline(self):
        if self.selected_baseline is not None:
            selected_frames = ([self.selected_cell.baseline[i].frame
                                for i in self.selected_baseline])
            self.selected_cell.activate_baseline(selected_frames)
            self.baseline_list_rebuild()
            self.view_baseline_refresh()
            self.view.graph_frame.canvas.draw()

            #self.view_baseline_update(self.selected_events, "purple", lw=0.5)
        else:
            tk.messagebox.showerror("Activation: No Baseline frames selected.", "You need to select baseline frames first!")
            return

    def remove_recording(self):
        MsgBox = tk.messagebox.askyesno("Remove Recording from File?", "Do you really want to remove this \
            recording from the file? All events, informations and conditions will be lost!")
        if MsgBox:
            self.pickle.remove(self.selected_recording)
        self.tree_redraw()


    def graph_mouse_released(self, event):
        # This function runs when the mouse button was released

        # If the right mouse button (button == 3) was released, show the context menu!
        if event.button == 3:
            # Get the coordinates
            # TODO: This still doesn't work quite as it should. The appearance is not next to the mouse cursor. Improve!
            graph_frame_x = self.view.graph_frame.winfo_rootx()
            graph_frame_y = self.view.graph_frame.winfo_rooty() + self.view.graph_frame.canvas.get_width_height()[1]
            self.view.event_frame.menu.post(graph_frame_x + event.x,
                                            graph_frame_y - event.y)

    def onselect(self, vmin, vmax):
        # This handles the input from the SpanSelector in GraphFrame
        (self.select_from, self.select_to) = self.graph_set_from_to(int(vmin), int(vmax))
        self.graph_select_event()
        self.graph_select_baseline()


    def cancel_selection(self):
        # Set selected range to None
        self.select_from = None
        self.select_to = None

        # Clear the current selection from the listbox
        self.view.event_frame.event_listbox.selection_clear(0, tk.END)
        self.view.baseline_frame.baseline_listbox.selection_clear(0, tk.END)


        for line in self.select_lines:
            line.remove()
        self.select_lines = [] # Remove the selection boundary lines

        # Reset the color of the selected events
        if self.selected_events != None:
            self.view_event_reset(self.selected_events)
        self.view.graph_frame.canvas.draw() # Redraw
        
        #if self.selected_baseline != None:
            #self.view_baseline_reset(self.selected_baseline)
        #self.view.graph_frame.canvas.draw() # Redraw

        # Remove the numbers from the "from" and "to" fields
        self.view.graph_frame.toolbar.select_to.delete(0, tk.END)
        self.view.graph_frame.toolbar.select_from.delete(0, tk.END)

        # Empty the selected events and baseline frames
        self.selected_events = []
        self.selected_baseline = []
        
    def graph_select_event(self):
        # This function updates the list of selected events
        # and redraws the graph to highlight those

        if self.selected_cell != None:
            # First reset the old events to their colors
            # only reset view if there are old events selected
            if ((self.selected_events is not None) and (len(self.selected_events) > 0)): 
                self.view_event_reset(self.selected_events)

            if self.selected_cell.has_events():
                # Read the new selected events within the range of the selection
                self.selected_events = [i for (i, x) in enumerate(self.selected_cell.events)
                                        if (x.frame >= self.select_from) and (x.frame <= self.select_to)]

            if (self.selected_events != []) and (self.selected_events != None):
                # Clear the current selection
                self.view.event_frame.event_listbox.selection_clear(0, tk.END)
                # Set the current selection to the ones chosen in the graph
                self.view.event_frame.event_listbox.selection_set(self.selected_events[0], self.selected_events[-1])
                # Change the color of the selected events to red
                self.view_event_update(self.selected_events, "red", lw=1.0)

    def graph_select_baseline(self):
        # This function updates the list of selected baseline frames
        # and redraws the graph to highlight those

        if self.selected_cell != None:
            # First reset the old baseline frames to their colors
            #if self.selected_baseline is not None:
                #self.view_baseline_reset(self.selected_baseline)

            if self.selected_cell.has_baseline():
                # Read the new selected events within the range of the selection
                self.selected_baseline = [i for (i, x) in enumerate(self.selected_cell.baseline)
                                        if (x.frame >= self.select_from) and (x.frame <= self.select_to)]

            if (self.selected_baseline != []) and (self.selected_baseline != None):
                # Clear the current selection
                self.view.baseline_frame.baseline_listbox.selection_clear(0, tk.END)
                # Set the current selection to the ones chosen in the graph
                self.view.baseline_frame.baseline_listbox.selection_set(self.selected_baseline[0], self.selected_baseline[-1])
                # show selected baseline frames in graph raw frame

                if self.baseline_selected_lines:
                    for line in self.baseline_selected_lines:
                        line.remove()

                self.baseline_selected_lines = []
                                      
                self.baseline_selected_lines.append(
                    self.view.graph_frame.raw_ax.scatter(
                        [item.frame for i, item in enumerate(self.selected_cell.baseline) if i in self.selected_baseline],
                            [[0.67] for j, item in enumerate(self.selected_cell.baseline) if j in self.selected_baseline], color="pink"))
                
                self.view.graph_frame.canvas.draw()



    def graph_set_from_to(self, vmin, vmax):
        # Set the "From"-Value to zero if the selection extends to lower values
        if vmin < 0:
            vmin = 0

        if vmax < 0 :
            vmax = 0

        if (vmax != None) & (self.selected_cell != None):
            if vmax >= len(self.selected_cell):
                vmax = len(self.selected_cell) - 1

        # Delete the old selection boundary lines
        for line in self.select_lines:
            line.remove()
        ####################
        # Handle the "From" and "To" fields
        # Delete and then fill the "From" field with selected_frame
        self.view.graph_frame.toolbar.select_from.delete(0, tk.END)
        self.view.graph_frame.toolbar.select_from.insert(0, vmin)

        # Delete the "to" filed if to_value is not specified
        if vmax == None:
            self.view.graph_frame.toolbar.select_to.delete(0, tk.END)
        else:
            self.view.graph_frame.toolbar.select_to.delete(0, tk.END)
            self.view.graph_frame.toolbar.select_to.insert(0, vmax)
        ###########################
        # Handle the boundary lines
        self.select_lines = []
        # Add the selection start boundary line to the graphs
        self.select_lines.append(
            self.view.graph_frame.raw_ax.axvline(vmin, lw=1.0, color="black"))
        self.select_lines.append(
            self.view.graph_frame.di_ax.axvline(vmin, lw=1.0, color="black"))

        if vmax != None:
            # Add the selection end boundary line to the graphs
            self.select_lines.append(
                self.view.graph_frame.raw_ax.axvline(vmax, lw=1.0, color="black"))
            self.select_lines.append(
                self.view.graph_frame.di_ax.axvline(vmax, lw=1.0, color="black"))

        self.view.graph_frame.canvas.draw()

        return (vmin, vmax)

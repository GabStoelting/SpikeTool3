import numpy as np
import pandas as pd
import h5py

#####################################################################
#
#####################################################################


class Condition:
    # This class describes a recording condition.
    # Included are the start frame (self.start),
    # the end frame (self.end),
    # the deadtime for the perfusion change (self.deadtime)
    # and further definitions as a dictionary in self.information

    def __init__(self, start=0, end=0, deadtime=0, **kwargs):
        self.start = start
        self.end = end
        self.deadtime = deadtime
        self.information = kwargs

    def __repr__(self):
        return f"From frame {self.start} to {self.end}, deadtime: {self.deadtime}, information: {self.information}"
    
    def values(self):
        # return the values of this condition as a numpy array
        vals = np.array([self.start, self.end, self.deadtime]).astype(int)
        for info in self.information:
            vals = np.append(vals, self.information[info]).astype(int)
            
        return vals
    
    def descriptors(self):
        descs = ["start", "end", "deadtime"]
        for key in self.information.keys():
            descs.append(key)
        return descs

#####################################################################
#
#####################################################################


class Event:
    # This class contains information about a single event
    # within a calcium imaging recording
    #

    def __init__(self, frame=0, use=True):
        self.frame = frame
        self.use = use

    def reject(self):
        self.use = False

    def accept(self):
        self.use = True

    def __repr__(self):
        return f"frame: {self.frame}, use:{self.use}"

#####################################################################
#
#####################################################################

class Baseline:
    # This class contains information about a single baseline frame
    # within a calcium imaging recording
    #

    def __init__(self, frame=0, use=True):
        self.frame = frame
        self.use = True

    def reject(self):
        self.use = False

    def accept(self):
        self.use = True

    def __repr__(self):
        return f"frame: {self.frame}, use:{self.use}"

#####################################################################
#
#####################################################################

class Cell:
    # This class contains information about a single cell
    # from a calcium imaging recording

    def __init__(self, cell_id, raw_data, use=True, cutoff=0, **kwargs):
        self.cell_id = cell_id
        self.raw_data = raw_data
        self.baseline = []

        self.events = []
        self.conditions = []
        self.use = use
        self.cutoff = cutoff
        self.information = kwargs

    def __repr__(self):
        return f"cell_id: {self.cell_id}, len: {len(self)} frames, number of events:{len(self.events)}"

    def __len__(self):
        return len(self.raw_data)

    def reject(self):
        self.use = False

    def accept(self):
        self.use = True

    def add_condition(self, start, end, **kwargs):
        self.conditions.append(Condition(start, end, **kwargs))

    def get_condition_events(self, **kwargs):
        print(kwargs)
        for condition in self.conditions:
            print(condition)
            if kwargs.items() <= condition.information.items():
                return self.get_event(range(int(condition.start), int(condition.end)))

    def has_events(self):
        if len(self.events) > 0:
            return True
        else:
            return False

    def has_baseline(self):
        if len(self.baseline) > 0:
            return True
        else:
            return False

    def reset_events(self, start=None, end=None):
        if not start and not end:  # Reset all events if start and end are not specified
            self.events = []
            return
        # If end is not specified but start is, set it from start to the end of the recording
        elif start and not end:
            end = len(self.raw_data)
        elif not start and end:  # This should not happen!
            return

        self.events = [x for x in self.events if ((x.frame < start) or (x.frame > end))]
        
    def reset_baseline(self, start=None, end=None):
        if not start and not end:  # Reset all baseline frames if start and end are not specified
            self.baseline = []
            return
        # If end is not specified but start is, set it from start to the end of the recording
        elif start and not end:
            end = len(self.raw_data)
        #elif not start and end:  # This should not happen!
            #return

        self.baseline = [x for x in self.baseline if ((x.frame < start) or (x.frame > end))]
  

    def set_events(self, event_list):
        # Define the list of events for this cell
        if isinstance(event_list, int):
            event_list = [event_list]
        self.events = [Event(event) for event in event_list]

    def add_events(self, event_list):
        # Add events to the list of events for this cell

        if isinstance(event_list, int):
            event_list = [event_list]
        self.events = self.events + [Event(event) for event in event_list]
        self.events = sorted(self.events, key=lambda event: event.frame)

    def add_baseline(self, baseline_list):
		# Add baseline frames to the list of baseline for this cell

        if isinstance(baseline_list, int):
            baseline_list = [baseline_list]
        self.baseline = self.baseline + [Baseline(baseline_frame) for baseline_frame in baseline_list]
        self.baseline = sorted(self.baseline, key=lambda baseline_frame: baseline_frame.frame)

    def get_event(self, frame, only_active=True):
        # Get a list of events from this cell
        if isinstance(frame, int):
            frame = [frame]
        for event in self.events:
            if event.frame in frame:
                if only_active:
                    if event.use is True:
                        yield event
                else:
                    yield event

    def get_baseline(self, frame, only_active=True):
        # Get a list of baseline frames from this cell
        if isinstance(frame, int):
            frame = [frame]
        for baseline_frame in self.baseline:
            if baseline_frame.frame in frame:
                if only_active:
                    if baseline_frame.use is True:
                        yield baseline_frame
                else:
                    yield baseline_frame
					
    def reject_event(self, frame):
        # Reject a single event or a list of events
        if isinstance(frame, int):
            frame = [frame]
        for event in self.events:
            if event.frame in frame:
                event.use = False
                
    def reject_baseline(self, frame):
        # Reject a single baseline frame or a list of baseline
        if isinstance(frame, int):
            frame = [frame]
        for baseline in self.baseline:
            if baseline.frame in frame:
                baseline.use = False
                
    def delete_events(self, frame):
        # Delete a single event or a list of events
        if isinstance(frame, int):
            frame = [frame]
        frames_to_be_deleted = [x for x in self.get_event(frame, only_active=False)]
        for event in frames_to_be_deleted:
            self.events.remove(event)
            
    def activate_event(self, frame):
        # Reject a single event or a list of events
        if isinstance(frame, int):
            frame = [frame]
        for event in self.events:
            if event.frame in frame:
                event.use = True
                
    def activate_baseline(self, frame):
        # Activate a single baseline frame or a list of baseline
        if isinstance(frame, int):
            frame = [frame]
        for baseline in self.baseline:
            if baseline.frame in frame:
                baseline.use = True     
                                 
    def find_events(self, cutoff=0.0, min_distance_to_last_spike=2, start=None, end=None):
        self.cutoff = cutoff
        if self.cutoff > 0:
            d_data = np.diff(self.raw_data)
            # eventList = []
            if not start:
                start = 1
            if not end:
                end = len(d_data)

            for i in range(start, end):
                if d_data[i] > cutoff:
                    if (d_data[i + 1: i + min_distance_to_last_spike + 1] < cutoff).all():
                        yield i+1
            # return eventList
        else:
            return []
	
    def get_di(self):
        return np.diff(self.raw_data)
    
    def store_hdf(self, cell_grp):
        # Store all informations about the cell
        # in the group attributes
        current_cell = cell_grp.create_dataset(f"{self.cell_id}", data=self.raw_data)
               
        current_cell.attrs["cell_id"] = self.cell_id # fixed
        current_cell.attrs["use"] = self.use # fixed
        current_cell.attrs["cutoff"] = self.cutoff # fixed
        
        # Add all other information fields
        for i in self.information:
            current_cell.attrs[i] = self.information[i]
            
        
        # Store all events (if self.events exists)
        try:
            event_array = np.array([])
            for e in self.events:
                event_array = np.append(event_array, np.array([e.frame, e.use]), axis=0)
            event_array = event_array.reshape(-1, 2)
        
            cell_grp.create_dataset(f"events/{self.cell_id}", data=event_array)
        except AttributeError:
            pass
        
        # Store all baselines (if self.baseline exists)

        try:
            baseline_array = np.array([])
            for b in self.baseline:
                baseline_array = np.append(baseline_array, np.array([b.frame, b.use]), axis=0)
            baseline_array = baseline_array.reshape(-1, 2)
        
            cell_grp.create_dataset(f"baseline/{self.cell_id}", data=baseline_array)
        except AttributeError:
            pass

        # Save the conditions of this recording       
        if len(self.conditions) > 0:
            # Add the column descriptors into the attributes
            cond_grp = cell_grp.create_group(f"conditions/{self.cell_id}")
            cond_grp.attrs["columns"] = self.conditions[0].descriptors()
           
            # Now, combine the condition data into a numpy array
            cond_values = np.array([])
            for cond in self.conditions:
                cond_values = np.append(cond_values, cond.values())
            cond_values = cond_values.reshape(-1, len(self.conditions[0].descriptors()))
            cond_grp.create_dataset(f"{self.cell_id}", data=cond_values)


        
    
#####################################################################
#
#####################################################################


def load_cells(raw_data):
    cells = {cell: Cell(cell, raw_data[cell]) for cell in
             raw_data.columns.values}
    return cells


class Recording:
    # This class stores information about a single
    # calcium imaging recording (aka "slice")
    #
    # file_id - Unique (<- this is not enforced!) identifier for the recording
    # dt - temporal distance between two frames in seconds
    # raw_data - Table with the time series data with individual cells in
    #            columns with a unique name
    # **kwargs - You may supply a list of further information about the
    #            recording such as date, animal id, etc. that will be stored
    #            in a dictionary called "information"
    #
    # TODO: It was a somewhat stupid idea to save conditions in both, Recording and every Cell.
    # It gets more complicated with more usage of calim but this should be reconsidered...

    def __init__(self, file_id, dt, raw_data, **kwargs):
        self.file_id = file_id
        self.dt = dt
        # This is a list of cell objects
        if isinstance(raw_data, pd.DataFrame):
            self.cells = load_cells(raw_data)
        else:
            self.cells = {}
        # This is a list of condition objects
        self.conditions = []
        # Add to the list if conditions are supplied
        if "conditions" in kwargs:
            for c in kwargs["conditions"]:
                self.add_condition(**c)
        # Further information will be stored in dicts
        self.information = kwargs

    def __repr__(self):
        return f"{self.file_id}, {len(self)} frames, {self.dt} s/frame, {len(self.cells)} cells, {self.information}"

    def __len__(self):
        # This returns the number of frames of the first cell.
        # The assumption is that all cells should have the same number of frames!
        return len(self.cells[next(iter(self.cells))])

    def add_condition(self, start, end, update_cells=True, **kwargs):
        self.conditions.append(Condition(start, end, **kwargs))
        # Automatically update the conditions for all cells
        if update_cells is True:
            for cell in self.cells:
                self.cells[cell].add_condition(start, end, **kwargs)
                
    def store_hdf(self, rec_grp):
        # Store all informations about the recordings
        # in the group attributes
        rec_grp.attrs["file_id"] = self.file_id # fixed
        rec_grp.attrs["dt"] = self.dt # fixed
        
        # Add all other information fields
        for i in self.information:
            rec_grp.attrs[i] = self.information[i]
            
        # Iterate over cells to save them into the HDF
        if self.cells:
            cell_grp = rec_grp.create_group("cells")
            for cell in self.cells:
                self.cells[cell].store_hdf(cell_grp)
        
        # Save the conditions of this recording       
        if len(self.conditions) > 0:
            # Add the column descriptors into the attributes
            cond_grp = rec_grp.create_group("conditions")
            cond_grp.attrs["columns"] = self.conditions[0].descriptors()
           
            # Now, combine the condition data into a numpy array
            cond_values = np.array([])
            for cond in self.conditions:
                cond_values = np.append(cond_values, cond.values())
            cond_values = cond_values.reshape(-1, len(self.conditions[0].descriptors()))
            cond_grp.create_dataset(f"rec_conditions", data=cond_values)
            
    def load_hdf(self, rec_grp):
        pass

#####################################################################
#
#####################################################################


class Project:
    def __init__(self, **kwargs):
        self.recordings = {}
        self.information = kwargs

    def append(self, recording: Recording):
        self.recordings[recording.file_id] = recording
        # self.recordings.append(recording)
        
    def to_hdf(self, filename):
        # Save to HDF      
        f = h5py.File(filename, "w")
        
        # Create a group for every recording
        if self.recordings:
            f.create_group("recordings")
            for rec in self.recordings:
                rec_grp = f.create_group(f"recordings/{rec}")
                self.recordings[rec].store_hdf(rec_grp)
                    
    
    def from_hdf(self, filename):
        # Load from HDF
        print("Project.from_hdf")
        f = h5py.File(filename, "r")
        
        # Iterate over recordings
        for r in f["recordings"]:
            
            
            rec_name = f"recordings/{r}"
            rec_attrs = list(f[rec_name].attrs)
            
            # Read the fixed field "file_id"
            file_id = f[rec_name].attrs["file_id"]
            rec_attrs.remove("file_id")
            
            # Read the fixed field "dt"
            dt = f[rec_name].attrs["dt"]
            rec_attrs.remove("dt")
            
            # Read the variable fields into info
            info = {}
            for a in rec_attrs:
                info[a] = f[rec_name].attrs[a]
                
            # Create a new recording
            rec = Recording(file_id, dt, None, **info)
            
            # Read and append the recording conditions
            if "conditions" in f[f"recordings/{r}"]:
                cond_cols = f[f"recordings/{r}/conditions"].attrs["columns"]
                cond_vals = np.array(
                    f.get(f"recordings/{r}/conditions/rec_conditions")).astype(float)
                for cv in cond_vals:
                    cond= {}
                    for i, col in enumerate(cond_cols):
                        cond[col] = cv[i]
                    rec.add_condition(**cond)
                          
            # Iterate over cells and load cells, events and conditions
            for c in f[f"{rec_name}/cells"]:
                # Only entries with a "cell_id" field contain cell data
                if "cell_id" in f[f"{rec_name}/cells/{c}"].attrs:
                    cell_attrs = list(f[f"{rec_name}/cells/{c}"].attrs)

                    cell_id = f[f"{rec_name}/cells/{c}"].attrs["cell_id"]
                    cell_attrs.remove("cell_id")

                    use = f[f"{rec_name}/cells/{c}"].attrs["use"]
                    cell_attrs.remove("use")

                    cutoff = f[f"{rec_name}/cells/{c}"].attrs["cutoff"]
                    cell_attrs.remove("cutoff")

                    raw_data = np.array(f.get(f"{rec_name}/cells/{c}"))
                    
                    info = {}
                    # Load the other attributes 
                    for a in cell_attrs:
                        info[a] = f[f"{rec_name}/cells/{c}"].attrs[a]
                        
                    # Create cell and append to recording
                    rec.cells[c] = Cell(cell_id, raw_data, use=use, 
                                        cutoff=cutoff, **info)
                    
                    # Read and append the cell conditions
                    if "conditions" in f[f"{rec_name}/cells"]:
                        cond_cols = f[f"{rec_name}/cells/conditions/{c}"].attrs["columns"]
                        cond_vals = np.array(
                            f.get(f"{rec_name}/cells/conditions/{c}/{c}")).astype(float)
                        for cv in cond_vals:
                            cond= {}
                            for i, col in enumerate(cond_cols):
                                cond[col] = cv[i]
                            rec.cells[c].add_condition(**cond)
                    
                    # Read and append events       
                    if "events" in f[f"{rec_name}/cells"]:
                        if c in f[f"{rec_name}/cells/events"]:  
                            event_list = np.array(f.get(f"{rec_name}/cells/events/{c}"))
                            for e in event_list:
                                rec.cells[c].events.append(Event(frame=e[0], use=e[1]))
                            
                    # Read and append baseline         
                    if "baseline" in f[f"{rec_name}/cells"]:
                        if c in f[f"{rec_name}/cells/baseline"]:
                            baseline_list = np.array(f.get(f"{rec_name}/cells/baseline/{c}"))
                            for b in baseline_list:
                                rec.cells[c].baseline.append(Event(frame=b[0], use=b[1]))
                
                # Add recording to project
                self.append(rec)
                            
                                    

            
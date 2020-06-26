import numpy as np
from scipy.signal import find_peaks
from scipy import sparse
from scipy.sparse.linalg import spsolve

#####################################################################
#
#####################################################################


class Condition:
    # This class describes a recording condition.
    # Included are the start frame (self.start),
    # the end frame (self.end),
    # the deadtime for the perfusion change (self.deadtime)
    # and further definitions as a dictionary in self.information

    def __init__(self, start, end, deadtime=0, **kwargs):
        self.start = start
        self.end = end
        self.deadtime = deadtime
        self.information = kwargs

    def __repr__(self):
        return f"From frame {self.start} to {self.end}, deadtime: {self.deadtime}, information: {self.information}"

#####################################################################
#
#####################################################################


class Event:
    # This class contains information about a single event
    # within a calcium imaging recording
    #

    def __init__(self, frame):
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

    def __init__(self, cell_id, raw_data, **kwargs):
        self.cell_id = cell_id
        self.raw_data = raw_data
        self.baseline_lam = 10e7
        self.baseline_p = 0.001
        self.baseline_iter = 10
        self.baseline = []

        self.events = []
        self.conditions = []
        self.use = True
        self.cutoff = 0
        self.information = kwargs

    def __repr__(self):
        return f"cell_id: {self.cell_id}, len: {len(self)} franes, number of events:{len(self.events)}"

    def __len__(self):
        return len(self.raw_data)

    def reject(self):
        self.use = False

    def accept(self):
        self.use = True

    def add_condition(self, start, end, **kwargs):
        self.conditions.append(Condition(start, end, **kwargs))

    def get_condition_events(self, **kwargs):
        for condition in self.conditions:
            if kwargs.items() <= condition.information.items():
                yield (condition.start, condition.end,
                       self.get_event(range(condition.start, condition.end)))

    def has_events(self):
        if len(self.events) > 0:
            return True
        else:
            return False

    def reset_events(self, start=None, end=None):
        if not start and not end: # Reset all events if start and end are not specified
            self.events = []
            return
        # If end is not specified but start is, set it from start to the end of the recording
        elif start and not end:
            end = len(self.raw_data)
        elif not start and end: # This should not happen!
            return

        self.events = [x for x in self.events if ((x.frame<start) or (x.frame>end))]

    def set_events(self, event_list):
        # TODO: Determine if this function is needed or can be condensed into add_events()
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

    def reject_event(self, frame):
        # Reject a single event or a list of events
        if isinstance(frame, int):
            frame = [frame]
        for event in self.events:
            if event.frame in frame:
                event.use = False

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

    def find_events(self, cutoff=0.0, min_distance_to_last_spike=5, start=None, end=None):
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
                    if (d_data[i-min_distance_to_last_spike:i] < cutoff).all():
                        yield i+1
            # return eventList
        else:
            return []

    def get_di(self):
        return np.diff(self.raw_data)

    def subtract_baseline(self, lam, p, niter=10):

        L = len(self.raw_data)
        D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
        w = np.ones(L)
        for i in range(niter):
            W = sparse.spdiags(w, 0, L, L)
            Z = W + lam * D.dot(D.transpose())
            z = spsolve(Z, w * self.raw_data)
            w = p * (self.raw_data > z) + (1 - p) * (self.raw_data < z)

        self.baseline = z

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

    def __init__(self, *, file_id, dt, raw_data, **kwargs):
        self.file_id = file_id
        self.dt = dt
        # This is a list of cell objects
        # TODO: Check that raw_data contains at least one cell!
        self.cells = load_cells(raw_data)
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

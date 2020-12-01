from calim import *
import pandas as pd
import pickle
import numpy as np
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

root = tk.Tk()
root.tk.call('tk', 'scaling', 2.0)

hdf_filename = askopenfilename(filetypes=(("HDF File", "*.hdf"), ("All Files", "*.*")),
                                         title="Choose a file.")

pkl_filename = asksaveasfilename(filetypes=(("Python Pickle", "*.pkl"), ("All Files", "*.*")),
                                         title="Choose a file.")

hdf = pd.HDFStore(hdf_filename)

pkl = Project()

for filename in hdf.conditions.filename.unique():

    hdf_columns = list(hdf.conditions[hdf.conditions.filename == filename].columns.values)
    print(hdf_columns)

    # We don't need the additional filename column if present
    if "filename" in hdf_columns:
        hdf_columns.remove("filename")

    # Recording informations
    if "dt" in hdf_columns:
        dt = float(hdf.conditions[hdf.conditions.filename == filename].dt.values[0])
        hdf_columns.remove("dt")
    else:
        dt = 0.1
        
    if "animal" in hdf_columns:
        animal = str(hdf.conditions[hdf.conditions.filename == filename].animal.values[0])
        hdf_columns.remove("animal")
    else:
        animal = "0000"
        
    if "birthdate" in hdf_columns:
        birthdate = str(hdf.conditions[hdf.conditions.filename == filename].birthdate.values[0])
        hdf_columns.remove("birthdate")
    else:
        birthdate = "1900-01-01"

    if "genotype" in hdf_columns:
        genotype = str(hdf.conditions[hdf.conditions.filename == filename].genotype.values[0])
        hdf_columns.remove("genotype")
    else:
        genotype = "xx"
        
    if "date" in hdf_columns:
        date = str(hdf.conditions[hdf.conditions.filename == filename].date.values[0])
        hdf_columns.remove("date")
    else:
        date = "1900-00-00"
        
    if "sex" in hdf_columns:
        sex = str(hdf.conditions[hdf.conditions.filename == filename].sex.values[0])
        hdf_columns.remove("sex")
    else:
        sex = "unknown"


    # Conditions
    if "begin" in hdf_columns:
        begin = hdf.conditions[hdf.conditions.filename == filename].begin.values
        hdf_columns.remove("begin")
    else:
        begin = [0]
    if "end" in hdf_columns:
        end = hdf.conditions[hdf.conditions.filename == filename].end.values
        hdf_columns.remove("end")
    else:
        end = [1]
 
    print(filename, dt, animal, birthdate, genotype, date, sex)
    print(begin, end)

    # Create entry for the recording
    information = {"animal": animal, "birthdate": birthdate, "genotype": genotype, "date":date, "sex":sex}



    rec = Recording(file_id=filename, dt=dt, raw_data=hdf["/raw/"+filename], **information)

    # Create conditons

    for i, start in enumerate(begin):
        k = {}
        # Add all additional columns from the original:
        for col in hdf_columns:
            k[col] = hdf.conditions[hdf.conditions.filename == filename][col].values[i]
        print(k)

        rec.add_condition(int(start), int(end[i]), update_cells=True, **k)


    # Transfer events
    for cell in hdf["/events/"+filename].columns:
        events = hdf["/events/"+filename][cell]
        events = events.replace(-1, np.nan)
        events = events.dropna()

        if len(events) == 0:
            rec.cells[cell].reject()

        rec.cells[cell].add_events(events)

    # Append the recording + conditions to the project
    pkl.append(rec)

for rec in pkl.recordings:
    for cond in pkl.recordings[rec].conditions:
        print(cond)

pickle.dump(pkl, open(pkl_filename, "wb"))
hdf.close()

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
print(hdf.keys())

pkl = Project()

for filename in hdf.conditions.filename.unique():

    # Recording informations
    dt = float(hdf.conditions[hdf.conditions.filename == filename].dt.values[0])
    animal = str(hdf.conditions[hdf.conditions.filename == filename].animal.values[0])
    birthdate = str(hdf.conditions[hdf.conditions.filename == filename].birthdate.values[0])
    genotype = str(hdf.conditions[hdf.conditions.filename == filename].genotype.values[0])
    date = str(hdf.conditions[hdf.conditions.filename == filename].date.values[0])
    sex = str(hdf.conditions[hdf.conditions.filename == filename].sex.values[0])


    # Conditions
    begin = hdf.conditions[hdf.conditions.filename == filename].begin.values
    end = hdf.conditions[hdf.conditions.filename == filename].end.values
    potassium = hdf.conditions[hdf.conditions.filename == filename].potassium.values
    angiotensin = hdf.conditions[hdf.conditions.filename == filename].angiotensin.values

    print(filename, dt, animal, birthdate, genotype, date, sex)
    print(begin, end, potassium, angiotensin)

    # Create entry for the recording
    information = {"animal": animal, "birthdate": birthdate, "genotype": genotype, "date":date, "sex":sex}
    rec = Recording(file_id=filename, dt=dt, raw_data=hdf["/raw/"+filename], **information)

    # Create conditons

    for i, start in enumerate(begin):
        k = {"potassium": float(potassium[i]), "angiotensin": float(angiotensin[i])}
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

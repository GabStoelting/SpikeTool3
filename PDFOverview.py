import tkinter as tk
from tkinter.ttk import Progressbar, Style
import tkSimpleDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class CreatePDF(tkSimpleDialog.Dialog):

    def __init__(self, parent, pickle):
        self.pickle = pickle
        self.filelist = [f for f in self.pickle.recordings]
        super().__init__(parent)

    def body(self, master):
        # TODO: Add a checkbox to determine whether cells not meant for inclusion should be saved
        # TODO: Add a checkbox whether conditions should be included

        fl_frame = tk.Frame(master=self)

        self.file_listbox = tk.Listbox(master=fl_frame, selectmode="extended", height=20, width=20)
        self.file_listbox.pack(side="left", fill=tk.BOTH, expand=True)

        file_scrollbar = tk.Scrollbar(master=fl_frame, orient="vertical")
        file_scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=file_scrollbar.set)

        file_scrollbar.config(command=self.file_listbox.yview)

        fl_frame.pack(side="top", fill=tk.X, expand=True)

        tk.Label(master, text="Select recording(s) to be \nsaved into a PDF", width=18).pack(side="top")

        # Create the style for the Progressbar to be able to display text
        self.pb_style = Style(self)
        self.pb_style.layout("LabeledProgressbar",
                             [("LabeledProgressbar.trough",
                               {"children": [("LabeledProgressbar.pbar",
                                              {"side": "left", "sticky": "ns"}),
                                             ("LabeledProgressbar.label",
                                              {"side": "left", "sticky": ""})],
                                "sticky":"nswe"})])

        self.progress = Progressbar(self, orient=tk.HORIZONTAL, length=200,
                                    mode="determinate", style="LabeledProgressbar")
        self.progress.pack()

        for rec in self.filelist:
            self.file_listbox.insert("end", f"{rec}")

    def SavePDF(self, pdf, recording):
        # This function prepares the figure to be saved in the PDF file
        for cell in recording.cells:
            if recording.cells[cell].use:
                plt.figure(figsize=(30,4))

                plt.plot(recording.cells[cell].raw_data, lw=0.1, color="black")

                for cond in recording.conditions:
                    plt.axvline(int(cond.end), lw=1.0, color="red")
                    condition_info = f"Start: {cond.start}\nEnd: {cond.end}\n"

                    for ci in cond.information:
                        condition_info = condition_info+f"{ci}: {cond.information[ci]}\n"
                    plt.text(int(cond.start), plt.gca().get_ylim()[1], condition_info, fontsize=8,
                             verticalalignment="top")



                plt.title(f"Recording: {recording.file_id} Cell:{cell}")
                plt.xlabel("Frame")
                pdf.savefig()
                plt.close()

    def validate(self):
        # TODO: Add something like a progress bar!
        self.selected_files = ([i for i in self.file_listbox.curselection()])

        pdf_filepath = tk.filedialog.asksaveasfilename(filetypes=(("PDF File", "*.pdf"), ("All Files", "*.*")),
                                             title="Choose a file.")
        if not pdf_filepath:
            return False

        allfiles = [self.filelist[f] for f in self.selected_files]
        with PdfPages(pdf_filepath) as pdf:
            for i, rec in enumerate(allfiles):
                self.progress["value"] = ((i+1)/len(allfiles))*100
                self.pb_style.configure("LabeledProgressbar", text=f"Processing file {i+1}/{len(allfiles)}")

                self.update_idletasks()
                self.SavePDF(pdf, self.pickle.recordings[rec])


        return True


    def apply(self):
        return True
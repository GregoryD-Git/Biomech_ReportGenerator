# -*- coding: utf-8 -*-
'''
Created on Mon Sep 11 16:11:41 2023

@author: Dan Gregory
daniel.gregory@shrinenet.org
'''

"""
Notes of updates made to v2.3.5:
11/12/24  - Use patient main folder and static python file to extract info for
            main patient frame
          
Notes of updates made to v1.3.4:
11/12/24  - added ability to save pdf report and go back and create a new report
          - **preserves the name, MRN, Dx, visit type, brace type, and VST used
          
          - automatically pulls the patient static python file to get the 
          patients age to auto-select the age-specific norm file
          
          - added a "Generate Report (no EMG)" button which will 
           automatically plot: kinematics, kinetics (if present), muscle 
          lengths, and foot model (if present)
          - changed the "Plot All" button with "Generate Report (with EMG)" 
          button which will automatically plot all data where kinetics and 
          foot model will only print if present in GCD file
          
          - added a text file export for all processed files which is 
          automatically stored in the patients top-level folder - skips 
          this if the MRN number is '1234567' so doesn't save the text file 
          when doing QA checks without patient info
          
Notes of updates made to v1.3.5:
          - updated EMG scaling from -1:1 to scaling y-axis and norms to max
          value of raw EMG signal to preserve raw EMG scaleing; also added
          y-values and axis label
"""

### ------------------------ SITE SPECIFIC SETTINGS ---------------------------
# Specify folder/file paths, norm data files, and site name
main_directory      = 'K:/ViconDatabase/Patients'
normfolderfile_name = 'K:/ViconDatabase/Normative Data'
norm4_7             = 'TD_Ave_4-7y.GCD'
norm8_12            = 'TD_Ave_8-12y.GCD'
norm13_21           = 'TD_Ave_13-21y.GCD'
norm_all            = 'TD_Ave.GCD'

# global normFile
normFile            = norm_all # defualt norm file, will be reset if program can find patient static python file
site_name           = 'New England'

# plot characteristics
FaceCol             = 'black'
FaceColAlpha        = 0.1

### ---------------------------------------------------------------------------

# Combobox selections
Dx_select           = ['Gait Abnormality','Cerebral Palsy','Idiopathic Toe Walking',
                       'Club Foot','Sports','Other','Neuro','Ortho']
visit_select        = ['Eval','Pre-Op','RTS','Post-Op','Long-Term','Research',
                       'Quality Assurance']
brace_select        = ["Barefoot","B AFO-PLS","L AFO-PLS","R AFO-PLS",
                        "B AFO-Solid","L AFO-Solid","R AFO-Solid",
                        "B AFO-FR","L AFO-FR","R AFO-FR",
                        "B AFO-Artic","L AFO-Artic","R AFO-Artic",
                        "L LIFT","R LIFT","B SMO","L SMO","R SMO",
                        "B UCBL","L UCBL","R UCBL",
                        "KAFO","HKAFO","RGO","Parawalker","Shoes Only","Other",
                        "Shod"]
walkaid_select      = ["None","Walker","Walker - Wheeled","Walker - Pickup",
                          "Crutches","Crutches - Axillary","Crutches - Loftstrand",
                          "Cane","Bobath Poles","Hand-Held","Other"]
vstused_select      = ['no KAD','Foot Model no KAD','RTS no KAD','no KAD Dypstick',
                       'Foot Model no KAD w/FootNotFlat','Foot Model Dypstick no KAD',
                       'KAD','KAD Dypstick','Foot Model with KAD',
                       'Foot Model Dypstick with KAD', 'new no KAD & old KAD']

# Initialize values with memory
dia                 = [Dx_select[0]]        # diagnosis entry
fse                 = False                 # indicate whether patient folder has been selected already

# bookmarks and bookmark number
bookmarks           = []
marknum             = 0

# Import packages
import tkinter as tk
from tkinter import ttk, filedialog, StringVar 
from datetime import datetime as date
import os 
import os.path
import glob
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import PyPDF2

# Primary call to all forms
class Motion_Report(tk.Tk):
    #This __init__ part of the code runs everytime
    def __init__(self):
        
        tk.Tk.__init__(self)
        # Specify title of Form
        tk.Tk.wm_title(self, "Shriners Motion Lab Report Generator")
        
        #Create a dictionary of frames/forms
        self.frames = {} 
        frames = (PatientStudyInfo_Page, SelectData_Page)
        #Specify all the form names
        for F in frames:
            frame = F(self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame
    
        #Initialize the first form
        self.frames[PatientStudyInfo_Page].tkraise()
        self.frames[PatientStudyInfo_Page].build_PatientInfoUI()
        
def get_PatientInfo_fromPyfile(selected_folder, self):
    global pid
    global fne
    global dte
    global brt
    global det
    global wat
    global age
    global vst
    global vis
    
    # List all files in the directory
    py_patient_directory = selected_folder + '/**/*.py*'
    python_files = []
    for file in glob.glob(py_patient_directory, recursive=True):
        if file.endswith('.py'):
            py_filename = file.replace('/','\\')
            python_files.append(py_filename)
        
    # If a Python file is found, open and read it
    if python_files:
        try:
            for StaticDataFileName in python_files:
                print(StaticDataFileName)
                # define python file name
                
                # open python file
                exec(open(StaticDataFileName).read())
                
                # try to extract variables that should exist in the file
                ################## patient name and id
                first_name = self.valueFirstName
                last_name = self.valueLastName
                pid = [self.valuePatientNumber]
                fne = [first_name + " " + last_name]
                
                ################## VST used
                try:
                    # check to see if T1 marker exists to pre-set RTS VST
                    t1  = self.T1MarkerName
                    vst = [vstused_select[2]]   # vst used entry
                    vis = [visit_select[2]]     # visit type entry
                except:
                    # else, select no KAD VST
                    vst = [vstused_select[0]]   # vst used entry
                    vis = [visit_select[0]]     # visit type entry
                
                ################## brace trial modifier
                brt = [self.valueTrialModifier]
                if brt == 'Barefoot':
                    brt = 'None'
                
                ################## date of data collection
                collect_day = self.valueDataCollectionDate_Day
                collect_mon = self.valueDataCollectionDate_Month
                collect_yer = self.valueDataCollectionDate_Year
                
                # combine into date string mo-day-year
                dte = [f'{collect_mon}-{collect_day}-{collect_yer}']
                
                ################## patient walk aide used
                wat = [self.valueAssistiveDevice]
                
                ################## patient age at time of collection
                patient_day = self.valueDateOfBirth_Day
                patient_month = self.valueDateOfBirth_Month
                patient_year = self.valueDateOfBirth_Year
                
                # Combine strings into a date
                birth_date_str = f"{patient_year}-{patient_month}-{patient_day}"
                birth_date = date.strptime(birth_date_str, "%Y-%b-%d")
                
                # Format the datetime object to the desired format
                date.strptime
                current_date =  date.today()
                age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
                print(f'Patient age is: {age}')
                return pid, fne, brt, dte, wat, age, vst, vis
        # if python file is in folder but not static python file or corrupt
        except:
            fne = ['Patient Name']
            pid = ['1234567']
            dte = [date.today().strftime('%m-%d-%Y')]
            brt = [brace_select[0]]
            wat = [walkaid_select[0]]
            age = 1
            vst = [vstused_select[0]]   # vst used entry
            vis = [visit_select[0]]     # visit type entry
            
            print('Static python file not found or could not be accessed. Defualt values used for patient information')
            return pid, fne, brt, dte, wat, age
    # if no python file is located in patient directory folder
    else:
        fne = ['Patient Name']
        pid = ['1234567']
        dte = [date.today().strftime('%m-%d-%Y')]
        brt = [brace_select[0]]
        wat = [walkaid_select[0]]
        age = 1
        vst = [vstused_select[0]]   # vst used entry
        vis = [visit_select[0]]     # visit type entry
        
        print('Static python file not found or could not be accessed. Defualt values used for patient information')
        return pid, fne, brt, dte, wat, age, vst, vis

class PatientStudyInfo_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid()
    
        # Open top level folder for patient
        self.selected_folder = filedialog.askdirectory(initialdir=main_directory, title="Select a Folder")
        if self.selected_folder == "":
            tk.messagebox.showerror('Python Error', 'Error: No files were selected! \nGo back and select a file or close the window')
            quit()
          
        global patient_directory
        patient_directory = f'{self.selected_folder}/**/*.gcd*'
        
        # Get patient info from python file in folder
        [pid, fne, brt, dte, wat, age, vst, vis] = get_PatientInfo_fromPyfile(self.selected_folder, self)
    
    
    def build_PatientInfoUI(self):
        # --------------------------- Master Frame ------------------------------------
        global firstlastname_entry
        global MRN_entry
        global Dx_type_combobox
        global date_entry
        global visit_type_combobox
        global condition_type_combobox
        global brace_type_combobox
        global walkaid_type_combobox
        global report_type_combobox
        global VSTused_type_combobox
        global varLR
        
        # Patient Information
        patient_info_frame = tk.LabelFrame(self, text='Patient Information')
        patient_info_frame.grid(row=0, column=0, sticky='news', padx=10, pady=5) # in row 1 column 1 in frame 1

        firstlastname_label = tk.Label(patient_info_frame, text='First and Last Name')
        firstlastname_label.grid(row=0, column=0, padx=5, pady=5) # in row 1 column 1 in label frame 1
        firstlastname_entry = tk.Entry(patient_info_frame)
        firstlastname_entry.grid(row=1, column=0, padx=5, pady=5)
        firstlastname_entry.insert(0, fne[0])

        MRN_label = tk.Label(patient_info_frame, text='Medical Record Number')
        MRN_label.grid(row=0, column=1, padx=5, pady=5)
        MRN_entry = tk.Entry(patient_info_frame)
        MRN_entry.grid(row=1,column=1, padx=5, pady=5)
        MRN_entry.insert(0, pid[0])
        
        Dx_type = tk.Label(patient_info_frame, text='Diagnosis')
        Dx_type.grid(row=0, column=2, padx=5, pady=5)
        Dx_type_combobox = ttk.Combobox(patient_info_frame, values=dia[0])
        Dx_type_combobox['values'] = Dx_select
        Dx_type_combobox.grid(row=1, column=2, padx=5, pady=5)
        dxIDX = Dx_select.index(dia[0])
        Dx_type_combobox.current(dxIDX)
        
        date_label = tk.Label(patient_info_frame, text='Date of Study')
        date_label.grid(row=0, column=3, padx=5, pady=5)
        date_entry = tk.Entry(patient_info_frame)
        date_entry.grid(row=1, column=3, padx=5, pady=5)
        date_entry.insert(0,dte[0])

        # pack and scale size of widgets after information has been printed to frames
        for nchild in range(0,4):
            patient_info_frame.grid_rowconfigure(nchild, weight=1)
            patient_info_frame.grid_columnconfigure(nchild, weight=1)        

        # Visit information
        visit_info_frame = tk.LabelFrame(self, text='Visit Information')
        visit_info_frame.grid(row=1, column=0, sticky='news', padx=10, pady=5)

        visit_type = tk.Label(visit_info_frame, text='Visit Type')
        visit_type.grid(row=0, column=0, padx=5, pady=5)
        visit_type_combobox = ttk.Combobox(visit_info_frame, values=vis[0])
        visit_type_combobox['values'] = visit_select
        visit_type_combobox.grid(row=1, column=0, padx=5, pady=5)
        visIDX = visit_select.index(vis[0])
        visit_type_combobox.current(visIDX)

        condition_type = tk.Label(visit_info_frame, text='Condition')
        condition_type.grid(row=0, column=1, padx=5, pady=5)
        condition_type_combobox = ttk.Combobox(visit_info_frame, values= ['Barefoot','Braced','Foot Model','Best Walk','Walker','Shoes','Lift','Comparison','Other'])
        condition_type_combobox.grid(row=1, column=1, padx=5, pady=5)
        condition_type_combobox.current(0)

        brace_type = tk.Label(visit_info_frame, text='Brace Type')
        brace_type.grid(row=0, column=2, padx=5, pady=5)
        brace_type_combobox = ttk.Combobox(visit_info_frame, values=brt[0])
        brace_type_combobox['values'] = brace_select
        brace_type_combobox.grid(row=1, column=2, padx=5, pady=5)
        brtIDX = brace_select.index(brt[0])
        brace_type_combobox.current(brtIDX)

        walkaid_type = tk.Label(visit_info_frame, text='Walk Aid Type')
        walkaid_type.grid(row=0, column=3, padx=5, pady=5)
        walkaid_type_combobox = ttk.Combobox(visit_info_frame, values=wat[0])
        walkaid_type_combobox['values'] = walkaid_select
        walkaid_type_combobox.grid(row=1, column=3, padx=5, pady=5)
        watIDX = walkaid_select.index(wat[0])
        walkaid_type_combobox.current(watIDX)

        # pack and scale size of widgets after information has been printed to frames
        for nchild in range(0,4):
            visit_info_frame.grid_rowconfigure(nchild, weight=1)
            visit_info_frame.grid_columnconfigure(nchild, weight=1)    
            
        # Report and proceed
        reportplot_info_frame = tk.LabelFrame(self, text='Report, VST, and Proceed to Plot')
        reportplot_info_frame.grid(row=2, sticky='news', column=0, padx=10, pady=5)

        report_type = tk.Label(reportplot_info_frame, text='Report Type')
        report_type.grid(row=0, column=0, padx=5, pady=5)
        report_type_combobox = ttk.Combobox(reportplot_info_frame, values=['Quick Check','Consistency Both','Consistency Left','Consistency Right','Working','BF-AFO Comparison','Pre-Post Comparison','Normal vs. Best Walk','Quality Assurance','Other'])
        report_type_combobox.grid(row=1, column=0, padx=5, pady=5)
        report_type_combobox.current(1)  
        
        VSTused_type = tk.Label(reportplot_info_frame, text='Select VST Used')
        VSTused_type.grid(row=0, column=1, padx=5, pady=5)
        VSTused_type_combobox = ttk.Combobox(reportplot_info_frame, values=vst[0])
        VSTused_type_combobox['values'] = vstused_select
        VSTused_type_combobox.grid(row=1, column=1, padx=5, pady=5)
        vstIDX = vstused_select.index(vst[0])
        VSTused_type_combobox.current(vstIDX)
        
        LRplot_Label = tk.Label(reportplot_info_frame, text = 'Specify Limbs to Plot')
        LRplot_Label.grid(row=0, column=2)
        varLR = tk.IntVar()
        
        LRplot_checkbutton = tk.Radiobutton(reportplot_info_frame, text='Left & Right', variable=varLR, value=0)
        LRplot_checkbutton.grid(row=1, column=2, sticky='w')
        
        Lplot_checkbutton = tk.Radiobutton(reportplot_info_frame, text='Left Only', variable=varLR, value=1)
        Lplot_checkbutton.grid(row=2, column=2, sticky='w')
        
        Rplot_checkbutton = tk.Radiobutton(reportplot_info_frame, text='Right Only', variable=varLR, value=2)
        Rplot_checkbutton.grid(row=3, column=2, sticky='w')
        
        saveproceed_label = tk.Label(reportplot_info_frame, text='Save and Proceed or Exit')
        saveproceed_label.grid(row=0, column=3)
        
        save_button = tk.Button(reportplot_info_frame, text='Save and Pick Files', command=lambda: [save_entries(), self.parent.frames[SelectData_Page].tkraise(), self.parent.frames[SelectData_Page].build_PlotReportUI()])
        save_button.grid(row=1, column=3, sticky='news')

        exit_button = tk.Button(reportplot_info_frame, text="Close Window Without Saving", command=lambda: [self.parent.destroy()])        
        exit_button.grid(row=2, column=3, sticky='news')

        # pack and scale size of widgets after information has been printed to frames
        for nchild in range(0,9):
            reportplot_info_frame.grid_rowconfigure(nchild, weight=1)
            reportplot_info_frame.grid_columnconfigure(nchild, weight=1)  
            
class SelectData_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid()
         
    def on_combobox_selected(self, event, side):
        combobox = event.widget
        updated_label = combobox.get()
        for Llabel, Lvar in self.Lcheckbox_vars.items():
            if Llabel == updated_label:
                Lvar.set(True)
                print(f'{Llabel} is set to true')
            else:
                Lvar.set(False)
                print(f'{Llabel} is set to false')
                
        for Rlabel, Rvar in self.Rcheckbox_vars.items():
            if Rlabel == updated_label:
                Rvar.set(True)
                print(f'{Rlabel} is set to true')
            else:
                Rvar.set(False)
                print(f'{Rlabel} is set to false')
                
    def get_EMGcheckbox_info(self):
        # Function to access checkbox information
        Lselected_checkboxes = {Llabel: Lvar.get() for Llabel, Lvar in self.Lcheckbox_vars.items()}
        Rselected_checkboxes = {Rlabel: Rvar.get() for Rlabel, Rvar in self.Rcheckbox_vars.items()}
        return Lselected_checkboxes, Rselected_checkboxes
    
    def build_PlotReportUI(self):
        # Navigation frame
        navigation_frame = tk.LabelFrame(self, text='Navigation')
        navigation_frame.grid(row=0, column=0, sticky='news', padx=5, pady=5)
        
        back_button = tk.Button(navigation_frame, text="Back", command = lambda: [self.parent.frames[PatientStudyInfo_Page].tkraise(), self.parent.frames[PatientStudyInfo_Page].build_PatientInfoUI(), clear_bookmarks()])
        back_button.grid(row=0, column=0, sticky='news', padx=3, pady=5)
        
        save_button = tk.Button(navigation_frame, text="Save PDF", command = lambda: [close_pdf()])
        save_button.grid(row=0, column=1, sticky='news', padx=3, pady=5)
        
        ghost_label = tk.Label(navigation_frame,text="                                                                                                                  ")        
        ghost_label.grid(row=1, column=0, columnspan=2, sticky='news', padx=3, pady=5)
        
        exit_button = tk.Button(navigation_frame,text="Close Window", command=lambda: [self.parent.destroy()])        
        exit_button.grid(row=1, column=0, columnspan=2, sticky='news', padx=3, pady=5)
        
        # Plot frame
        plot_frame = tk.LabelFrame(self, text='Plot Options for Selected Files')
        plot_frame.grid(row=0, column=1, sticky='news', padx=5, pady=5)
        
        button_plotKMT = tk.Button(plot_frame, text="Kinematics", command=lambda: [plot_kinematics(self)])
        button_plotKMT.grid(row=0, column=0, sticky='news', padx=3, pady=3)
        button_plotKMT = tk.Button(plot_frame, text="Prog. Angles", command=lambda: [plot_progression(self)])
        button_plotKMT.grid(row=0, column=1, sticky='news', padx=3, pady=3)
        button_plotSaK = tk.Button(plot_frame, text="Sag. Kinetics", command=lambda: [plot_sagittalKinetics(self)])
        button_plotSaK.grid(row=0, column=2, sticky='news', padx=3, pady=3)
        button_plotCoK = tk.Button(plot_frame, text="Cor. Kinetics", command=lambda: [plot_coronalKinetics(self)])
        button_plotCoK.grid(row=0, column=3, sticky='news', padx=3, pady=3)
        button_plotMLV = tk.Button(plot_frame, text="Muscle Lengths", command=lambda: [plot_MuscleLengthVel(self)])
        button_plotMLV.grid(row=1, column=0, sticky='news', padx=3, pady=3)
        button_plotEMG = tk.Button(plot_frame, text="EMG", command=lambda: [plot_EMG(self)])
        button_plotEMG.grid(row=1, column=1, sticky='news', padx=3, pady=3)
        button_plotSPT = tk.Button(plot_frame, text="Spatiotemporal", command=lambda: [plot_SpatioTemporal(self)])
        button_plotSPT.grid(row=1, column=2, sticky='news', padx=3, pady=3)
        button_plotSFM = tk.Button(plot_frame, text="Foot Kinematics", command=lambda: [plot_FootModel(self)])
        button_plotSFM.grid(row=1, column=3, sticky='news', padx=3, pady=3)
        button_plotBas = tk.Button(plot_frame, text="Generate Report\n(no EMG)", command=lambda: [plot_kinematics(self), plot_progression(self), plot_sagittalKinetics(self), plot_coronalKinetics(self), plot_MuscleLengthVel(self), plot_SpatioTemporal(self), plot_FootModel(self)])
        button_plotBas.grid(row=2, column=0, rowspan=1, columnspan=2, sticky='news', padx=3, pady=3)
        button_plotALL = tk.Button(plot_frame, text="Generate Report\n(with EMG)", command=lambda: [plot_kinematics(self), plot_progression(self), plot_sagittalKinetics(self), plot_coronalKinetics(self), plot_MuscleLengthVel(self), plot_EMG(self), plot_SpatioTemporal(self), plot_FootModel(self)])
        button_plotALL.grid(row=2, column=2, rowspan=1, columnspan=2, sticky='news', padx=3, pady=3)
        
        # EMG selection and labels frame
        EMGusedL_frame = tk.LabelFrame(self, text='Left EMG Channels and Labels')
        EMGusedL_frame.grid(row=1, column=0, sticky='news', padx=10, pady=5)
        EMGusedR_frame = tk.LabelFrame(self, text='Right EMG Channels and Labels')
        EMGusedR_frame.grid(row=1, column=1, sticky='news', padx=10, pady=5)
        
        # EMG checkboxes and label names
        EMGplotLabels = [' Rectus Femoris (raw)', ' Vastus Lateralis (raw)',
                         ' Medial Hamstring (raw)',' Medial Gastroc (raw)',
                         ' Tibialis Anterior (raw)', ' Peroneus Longus (raw)']
        # Create a dictionary to store the checkbox variables
        self.Lcheckbox_vars = {label: tk.BooleanVar(value=True) for label in EMGplotLabels}
        self.Rcheckbox_vars = {label: tk.BooleanVar(value=True) for label in EMGplotLabels}
        # Create a dictionary to store the comboboxes
        self.Lcomboboxes = {}
        self.Rcomboboxes = {}
        
        # Create checkboxes
        # Left boxes
        for i, label in enumerate(EMGplotLabels[:5]):
            ri = i
            ci = 0
            if i >= 3:
                ri = i - 3
                ci = 2
            EMGusedL_frame.rowconfigure(i, weight=1)
            Lemgchk = tk.Checkbutton(EMGusedL_frame, text='', variable=self.Lcheckbox_vars[label], )
            Lemgchk.grid(row=ri+1, column=ci, sticky="w")
            
            # Create Combobox
            Lcombobox = ttk.Combobox(EMGusedL_frame, values=EMGplotLabels)
            Lcombobox.grid(row=ri+1, column=ci+1, pady=5)
            Lcombobox.set(label)
            Lcombobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)
            self.Lcomboboxes[label] = Lcombobox
            print(f'row index = {ri}')
        
        # Right boxes
        for i, label in enumerate(EMGplotLabels[:5]):
            ri = i
            ci = 0
            if i >= 3:
                ri = i - 3
                ci = 2
            EMGusedR_frame.rowconfigure(i, weight=1)
            Remgchk = tk.Checkbutton(EMGusedR_frame, text='', variable=self.Rcheckbox_vars[label])
            Remgchk.grid(row=ri+1, column=ci, sticky="w")
            
            # Create Combobox
            Rcombobox = ttk.Combobox(EMGusedR_frame, values=EMGplotLabels)
            Rcombobox.grid(row=ri+1, column=ci+1, pady=5)
            Rcombobox.bind("<<ComboboxSelected>>", self.on_combobox_selected)
            Rcombobox.set(label)
            self.Rcomboboxes[label] = Rcombobox
        
        # get current combobox selections and set to current
        diagnosis_get = Dx_type_combobox.get()
        dia[0] = diagnosis_get
        
        visit_get = visit_type_combobox.get()
        vis[0] = visit_get
        
        brace_get = brace_type_combobox.get()
        brt[0] = brace_get
        
        walkaid_get = walkaid_type_combobox.get()
        wat[0] = walkaid_get
        
        vstused_get = VSTused_type_combobox.get()
        vst[0] = vstused_get
        
        # global patient_directory
        self.selected_files = []
        selected_patient_folders = []
        # Pull all files within the folder and subfolders with .gcd file extension
        for file in glob.glob(patient_directory, recursive=True, include_hidden=True):
            self.selected_files.append(file.lower())
            folder = file.split("\\")[-2]
            if folder not in selected_patient_folders:
                selected_patient_folders.append(folder)
            
        global folderfile_name
        folderfile_name = []
        for name in self.selected_files:
            filename = name.replace('/','\\')
            folderfile_name.append(os.path.split(filename))
        
        rowidx = 2
        global checkboxes
        checkboxes = {}
        # fns = []
        
        # reverse order of patient folders so most recent comes first
        ordered_patient_folders = selected_patient_folders[::-1]
        
        for curr_session in ordered_patient_folders:
            selectLeft_file_frame = tk.LabelFrame(self, text=f'Select Left {curr_session} files')
            selectLeft_file_frame.grid(row=rowidx, column=0, sticky='news', padx=5, pady=5)
           
            selectRight_file_frame = tk.LabelFrame(self, text=f'Select Right {curr_session} files')
            selectRight_file_frame.grid(row=rowidx, column=1, sticky='news', padx=5, pady=5)
            rowidx += 1
        
            # get file names and print to checkboxes on select file frame
            for num in range(0,len(self.selected_files)):
                folder_forFile = self.selected_files[num].split("\\")[-2]
                if folder_forFile == curr_session.lower():
                    gcdfile = os.path.basename(self.selected_files[num])
                    Lvar = StringVar()
                    filenameLeft_checkbox = tk.Checkbutton(selectLeft_file_frame, text=gcdfile, variable=Lvar, onvalue=gcdfile, offvalue="")
                    filenameLeft_checkbox.grid(row=num, column=0, sticky='w')
                    # filenameLeft_checkbox.select()                                        Uncommenting this line of code will automatically pre-select all files
                    Rvar = StringVar()
                    filenameRight_checkbox = tk.Checkbutton(selectRight_file_frame, text=gcdfile, variable=Rvar, onvalue=gcdfile, offvalue="")
                    filenameRight_checkbox.grid(row=num, column=1, sticky='w')
                    # filenameRight_checkbox.select()                                        Uncommenting this line of code will automatically pre-select all files
                    checkboxes.update({gcdfile+'L': Lvar, gcdfile+'R': Rvar})
                
        # pack and scale size of widgets after information has been printed to frames
        for widget in plot_frame.winfo_children():
            widget.grid_configure(padx=3, pady=3)
            
        # pack and scale size of widgets after information has been printed to frames
        for nchild in selectLeft_file_frame.winfo_children():
            selectLeft_file_frame.grid_columnconfigure(nchild, weight=1)
        for nchild in selectRight_file_frame.winfo_children():
            selectRight_file_frame.grid_columnconfigure(nchild, weight=1)    
            
        for nchild in range(0,3):
            navigation_frame.grid_rowconfigure(nchild, weight=1)
            navigation_frame.grid_columnconfigure(nchild, weight=1)
        
        # main frame widget packing
        for widget in self.winfo_children():
            widget.grid_configure(padx=3, pady=3)

def clear_bookmarks():
    global bookmarks
    global marknum
    
    bookmarks = []
    marknum = 0

def get_gcdData(gcd_file, folderfile_name):
    # ----------------------------- Get data ------------------------------
        f = open(folderfile_name +'\\' +gcd_file, 'r+')
        data = f.readlines()
        # return data
    # ---------------------------- Get headers ----------------------------
        # find index of data headers that start with "!"
        headerIndex = [i for i, e in enumerate(data) if e[0] == "!"]
       
    # ----------------------------- Convert data --------------------------
        data_dict ={}
        # irlen = list(range(0,len(headerIndex)))
        for num in list(range(0,len(headerIndex))):
            # pull keys and asign to temporary variable
            key = data[headerIndex[num]][1:-1]
            # pull data associated with given key, minus "\n" and convert to float
            try:
                # get all values of data for key associated with headerIndex[num] up to next headerIndex[num+1]
                val = data[headerIndex[num]+1:headerIndex[num+1]]
            except:
                # same as above but for the reamining set of data for the last key
                val = data[headerIndex[num]+1:]
                    
            # convert values to float
            values = []
            for i in val:
                try:
                    values.append(float(i))    
                except:
                    continue
            # add key:value pairs to dictionary
            data_dict.update({key: values})
        return data_dict  
    
def get_normData(normfolderfile_name, isEMG, self):
    
    # 'age' is a global variable either calculated or set to '1' if static file is not available
    if age > 3 and age < 8:
        normFile = norm4_7
        EMGnormFile = norm4_7
    elif age > 7 and age < 13:
        normFile = norm8_12
        EMGnormFile = norm8_12
    elif age > 12:
        normFile = norm13_21
        EMGnormFile = norm13_21
    else:
        normFile = norm_all
        EMGnormFile = norm_all
    
    if isEMG == True:
        normFile = EMGnormFile
    else:
        normFile = normFile
    
    normFile_path = os.path.join(normfolderfile_name, normFile)
    f = open(normFile_path, 'r+')
    dataN = f.readlines()
    headerIndexN = [i for i, e in enumerate(dataN) if e[0] == "!"]
    dataNmean_dict = {}
    dataNstd_dict = {}
    
    for num in list(range(0,len(headerIndexN))):
        # pull keys and asign to temporary variable
        keyN = dataN[headerIndexN[num]].split()[0][1:]
        # pull data associated with given key, minus "\n" and number of subjects used, then convert to float
        try:
            # get all values of data for key associated with headerIndex[num] up to next headerIndex[num+1]
            valN = dataN[headerIndexN[num]+1:headerIndexN[num+1]]
        except:
            # same as above but for the reamining set of data for the last key
            valN = dataN[headerIndexN[num]+1:]
        # convert values to float
        meanN = []
        sdN = []
        for i in valN:
            # most variables have MEAN and SD data, but some only have a single value
            try:
                meanN.append(float(i.split()[0]))  
                sdN.append(float(i.split()[1]))
            except:
                meanN.append(float(i))
                
        # add key:value pairs to dictionary
        dataNmean_dict.update({keyN: meanN})
        dataNstd_dict.update({keyN: sdN})
    return dataNmean_dict, dataNstd_dict, normFile
        
# saving entry data
def save_entries():
    global PatientName
    global MRN
    global diagnosis
    global studydate
    global visit
    global condition
    global brace
    global walkaid
    global report
    global pdffile
    global VSTmodelused
    
    PatientName = firstlastname_entry.get()
    fne[0] = PatientName
    MRN = (MRN_entry.get() +'_')                            # adds underscore for file naming convention
    pid[0] = MRN[0:-1]                                      # Save entered name for use in another report
    diagnosis = Dx_type_combobox.get()
    studydate = date_entry.get()
    dte[0] = studydate
    visit = visit_type_combobox.get()
    condition = (condition_type_combobox.get() +'_')
    brace = brace_type_combobox.get()
    walkaid = walkaid_type_combobox.get()
    report = (report_type_combobox.get() +'_')
    VSTmodelused = VSTused_type_combobox.get()
    # "keep_empty = False" prevents the files from being corrupted, default is True
    # see: https://github.com/matplotlib/matplotlib/issues/11771
    try:
        pdffile = PdfPages(f'{condition +MRN +report +studydate}.pdf', keep_empty=False)
    except: 
        tk.messagebox.showerror('Python Error', 'ERROR: \n\nIt appears that the filename you are trying to use already exists and is open in another program. \n\nClose the file and retry, or change patient info to continue.')
        quit()
    
def close_pdf():
    try:
        pdffile.close()
        # write headers to pdf file
        pdf_reader = PyPDF2.PdfReader(f'{condition +MRN +report +studydate}.pdf')
        pdf_writer = PyPDF2.PdfWriter()
        for numpage in range(0,len(bookmarks)):
            page = pdf_reader.pages[numpage]
            pdf_writer.add_page(page)
            pdf_writer.add_outline_item(bookmarks[numpage][0], bookmarks[numpage][1])
            output_file = open(f'{condition +MRN +report +studydate}.pdf', 'wb')
            pdf_writer.write(output_file)
            
        output_file.close()
        tk.messagebox.showinfo("PDF file has been saved", "Go back and pick files for a new report or close the window.")
       
        # Text file export
        if not MRN == '1234567':
            try:
                # get the current date
                date_today = date.today().strftime('%m-%d-%Y')
                
                # specify file path where saved file will go
                save_path = patient_directory.split("/")
                file_path = os.path.join('/'.join(save_path[0:4]),f'{PatientName}_{MRN}_ProcessingLog.txt')
                
                # open the file in append mode ('a')
                with open(file_path, 'a') as f:
                    # check if the file exists
                    if os.path.getsize(file_path) == 0:
                        # write each variable to the file
                        f.write('PATIENT INFO \n')
                        f.write(f'{PatientName} \n')
                        f.write(f'{MRN} \n')
                        f.write(f'{diagnosis} \n')
                        f.write(f'File created on: {date_today} \n\n\n')
                    
                    f.write(f'REPORT GENERATION LOG CREATED ON: {date_today} \n')
                    f.write(f'Study date: {studydate} \n')
                    f.write(f'Visit Type: {visit} \n')
                    f.write(f'Condition: {condition} \n')
                    f.write(f'Brace Type: {brace} \n')
                    f.write(f'Walk Aide Type: {walkaid} \n')
                    f.write(f'Report Type Generated: {report} \n')
                    f.write(f'VST Model Used: {VSTmodelused} \n\n')
                    f.write('Files included in report: \n')
                    
                    for file in checkboxes:
                        # If the variable is set
                        if checkboxes[file].get():
                            f.write(str(f'{file}' + '\n'))
                    
                    f.write(f'END OF REPORT LOG FOR: {date_today} \n\n\n')
            except: 
                tk.messagebox.showerror('Python Error', 'ERROR: \n\nIt appears that the text filename you are trying to use already exists and is open in another program. \n\nClose the file and retry, or change patient info to continue.')
    except:
        print('Window closed, no data to save')
   
# Global parameters
"""
'bookmarks' will set and save pdf bookmarks to be saved to the final pdf file 
for quick page to page access in the final pdf file

"""  

def plot_kinematics(self):
    global bookmarks
    global marknum
    num_rows = 6
    num_cols=3
    
    # Create a figure with subplots
    fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
    fig.tight_layout()
    plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
    
    fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
    titlenamestr = 'Kinematics \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
    plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')

    # Flatten the axes1 array
    axes1 = axes1.flatten()
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            if gcd_count == 0:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
            limb_spec = ['Left','Right']
            plotloop = [0,1]
            plotLimb = file[-1]
            if plotLimb == 'L':
                plotloop = [0]
            elif plotLimb == 'R':
                plotloop = [1]
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'PelvicObliquity']
                        # cc = np.flipud(plt.cm.winter(np.linspace(0,1,n))) # left blue-->green
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print('LEFT Limb data for file {[gcd_file]} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicObliquity']
                        # cc = np.flipud(plt.cm.autumn(np.linspace(0,1,n))) # right red-->yellow
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1.0
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                
                # ----------------- Trunk Lateral Bend ------------------------
                
                data_label = ['TrunkObliquity']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Con\nExt')
                    lowerstr = ('Lat')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Obliquity (global)')
                # ax1.set_xlabel('% Gait Cycle')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),20)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Trunk Flexion/Extension -------------------
                data_label = ['TrunkTilt']
                ax = axes1[1]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Tilt (global)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),20)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Trunk Rotation ----------------------------
                data_label = ['TrunkRotation']
                ax = axes1[2]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Rotation (global)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),20)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # -----------------  Pelvic Obliquity -------------------------
                data_label = ['PelvicObliquity']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Up')
                    lowerstr = ('Dwn')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Obliquity ROT (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Pelvic Tilt -------------------------------
                data_label = ['PelvicTilt']
                ax = axes1[4]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Tilt ROT (global)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-5)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Pelvic Rotation ---------------------------
                data_label = ['PelvicRotation']
                ax = axes1[5]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Pro')
                    lowerstr = ('Ret')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Rotation (global)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Hip Ab/Adduction --------------------------
                data_label = ['HipAbAdduct']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Add')
                    lowerstr = ('Abd')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip AB/Adduction (pelvis)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Hip Flexion/Extension ---------------------
                data_label = ['HipFlexExt']
                ax = axes1[7]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip Flexion-Extension (pelvis)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),60)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Hip Rotation ------------------------------
                data_label = ['HipRotation']
                ax = axes1[8]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip Rotation (pelvis)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Knee Valgus/Varus -------------------------
                data_label = ['KneeValgVar']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Var')
                    lowerstr = ('Val')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Varus/Valgus (hip)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Knee Flexion/Extension --------------------
                data_label = ['KneeFlexExt']
                ax = axes1[10]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Flexion/Extension (hip)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),80)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- Knee Rotation ----------------------------
                data_label = ['KneeRotation']
                ax = axes1[11]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Rotation (hip)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- Foot Progression -------------------------
                # No Frontal plane equivalent for ankle in standard model
                data_label = ['FootProgression']
                ax = axes1[12]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Foot Progression (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                ax.fontsize = sf
                # y-limits
                getylim = ax.get_ylim()
                ylower = min(getylim[0],min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(getylim[1],max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- Ankle Plantar/Dorsiflexion ---------------
                data_label = ['DorsiPlanFlex']
                ax = axes1[13]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Dorsi-Plantarflexion (knee)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- Foot Rotation ----------------------------
                data_label = ['FootRotation']
                ax = axes1[14]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Foot Rotation (knee)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- figure layout options --------------------
                 
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if gcd_count == 0:
                    # --------------- Note on data and VST used for norms -----------------
                    VSTmessage = f"Biomechanical model used is the Shriners Standard Gait Model. VST used is the '{VSTmodelused}' skeletal template"
                    plt.gcf().text(0.935, titleRow, VSTmessage, fontsize=sf-1, rotation=90, color='k')
                    normDataUsed = 'Greenville, Salt Lake, & Spokane'
                    if normFile[0:2] == 'Gr':
                        normDataUsed = 'Greenville'
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                         
                    filenamestr = ('GDI')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    try:
                        GDM = round(dataNmean_dict['GDI'][0],2)
                        GDSD = round(dataNstd_dict['GDI'][0],2)
                        plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(firstcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                    except:
                        print(f'GDI is not found in {gcd_file}, not printed to kinematics page')
                                   
                    filenamestr = ('Spd')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    Spp1M = round((dataNmean_dict['Speed'][0]/1000) + (dataNstd_dict['Speed'][0]/1000),2)
                    Spm1M = round((dataNmean_dict['Speed'][0]/1000) - (dataNstd_dict['Speed'][0]/1000),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('Cad')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    cap1M = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    cam1M = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                      
                    LSL = round(data_dict['LeftSpeed'][0]/1000,2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LSL, fontsize=sf-1, color='k')
                   
                    Lca = round(data_dict['LeftCadence'][0],2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], Lca, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    
                    RSL = round(data_dict['RightSpeed'][0]/1000,2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RSL, fontsize=sf-1, color='k')
                    
                    Rca = round(data_dict['RightCadence'][0],2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], Rca, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')    
 
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1
            
        # Hide empty subplots if there are fewer graphs than subplots
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0:
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)):
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
               
    # Show the plot
    plt.show()
    # Save plot as PDF
    pdffile.savefig(fig)
    bookmarks.append(('Kinematics', marknum))
    marknum += 1

def plot_progression(self):
    global bookmarks
    global marknum
    num_rows = 6
    num_cols=3
    
    # Create a figure with subplots
    fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
    fig.tight_layout()
    plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
    
    fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
    titlenamestr = 'Progression Angles \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
    plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')

    # Flatten the axes1 array
    axes1 = axes1.flatten()
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            if gcd_count == 0:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
            limb_spec = ['Left','Right']
            plotloop = [0,1]
            plotLimb = file[-1]
            if plotLimb == 'L':
                plotloop = [0]
            elif plotLimb == 'R':
                plotloop = [1]
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'PelvicRotation']
                        # cc = np.flipud(plt.cm.winter(np.linspace(0,1,n))) # left blue-->green
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print('LEFT Limb data for file {[gcd_file]} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicRotation']
                        # cc = np.flipud(plt.cm.autumn(np.linspace(0,1,n))) # right red-->yellow
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                
                # ----------------- Pevlic Rotation ------------------------
                
                data_label = ['PelvicRotation']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Progression (global)')
                # ax1.set_xlabel('% Gait Cycle')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # -----------------  Femoral Rotation -------------------------
                data_label = ['FemurRotation']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    # lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    # upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    # ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Femur Progression (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Tibia Rotation --------------------------
                data_label = ['TibiaRotation']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    # lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    # upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    # ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Tibia Progression (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- Foot Progression -------------------------
                # No Frontal plane equivalent for ankle in standard model
                data_label = ['FootProgression']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Foot Progression (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- figure layout options --------------------
                 
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if gcd_count == 0:
                    # --------------- Note on data and VST used for norms -----------------
                    VSTmessage = f"Biomechanical model used is the Shriners Standard Gait Model. VST used is the '{VSTmodelused}' skeletal template"
                    plt.gcf().text(0.935, titleRow, VSTmessage, fontsize=sf-1, rotation=90, color='k')
                    normDataUsed = 'Greenville, Salt Lake, & Spokane'
                    if normFile[0:2] == 'Gr':
                        normDataUsed = 'Greenville'
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                         
                    filenamestr = ('GDI')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    try:
                        GDM = round(dataNmean_dict['GDI'][0],2)
                        GDSD = round(dataNstd_dict['GDI'][0],2)
                        plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(firstcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                    except:
                        print(f'GDI is not found in {gcd_file}, not printed to kinematics page')
                                   
                    filenamestr = ('Spd')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    Spp1M = round((dataNmean_dict['Speed'][0]/1000) + (dataNstd_dict['Speed'][0]/1000),2)
                    Spm1M = round((dataNmean_dict['Speed'][0]/1000) - (dataNstd_dict['Speed'][0]/1000),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('Cad')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    cap1M = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    cam1M = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                      
                    LSL = round(data_dict['LeftSpeed'][0]/1000,2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LSL, fontsize=sf-1, color='k')
                   
                    Lca = round(data_dict['LeftCadence'][0],2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], Lca, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    
                    RSL = round(data_dict['RightSpeed'][0]/1000,2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RSL, fontsize=sf-1, color='k')
                    
                    Rca = round(data_dict['RightCadence'][0],2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], Rca, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')    
 
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1
            
        # Hide empty subplots if there are fewer graphs than subplots
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0:
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)):
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
               
    # Show the plot
    plt.show()
    # Save plot as PDF
    pdffile.savefig(fig)
    bookmarks.append(('Progression Angles', marknum))
    marknum += 1

def plot_sagittalKinetics(self):
    global foldername
    global bookmarks
    global marknum
    fig = None
    plotNorm = False
    num_rows = 6
    num_cols=3
    
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file+'L') pulls the index of the first gcd file in checkboxes with the root name to reference appropriate file-path when accessing .gcd files from subfolders
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
            # check to see if kinetics data present, if not, skip file and move to next within 'checkboxes' for-loop
            limbassign = 'Left'
            if file[-1] == 'R':
                limbassign = 'Right'
            
            data_label = f'{limbassign}HipFlexExtMoment'
            if not data_label in data_dict.keys():
                print(f'{limbassign} SAGITTAL kinetics were not found in file {gcd_file}')
                gcd_count += 1 
                # This code will keep counting files so plots will match color schemes throughout the report
                if limbassign == 'Left':
                    LeftPlotNum += 1 
                    PlotNum = LeftPlotNum
                elif limbassign == 'Right':
                    RightPlotNum += 1 
                    PlotNum = RightPlotNum
                continue
            elif data_label in data_dict.keys() and limbassign == 'Left':
                plotloop = [0]
            elif data_label in data_dict.keys() and limbassign == 'Right':
                plotloop = [1]                
            else:
                print(f'Check SAGITTAL kinetics regarding file {gcd_file}, limb-specific message should have been displayed or data plotted')
                
        # ----------------------------- Set pdf page and subplots -------------
            if not fig:
                # Create a figure with subplots
                fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
                # fig.tight_layout(pad=2, w_pad=1.0, h_pad=1.0)
                fig.tight_layout()
                plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
               
                # fig.tight_layout(pad=3.0)  # Adjust spacing between subplots
                fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
                titlenamestr = 'Sagittal Kinetics \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
                plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')
                
                # Flatten the axes1 array
                axes1 = axes1.flatten()
        # ----------------------------- Get norm data -------------------------
                # ONLY GET and PLOT norm data once
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
                plotNorm = True
                
        # ----------------------------- Plot data -----------------------------
        
            
            limb_spec = ['Left','Right']
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print('LEFT Limb data for file {gcd_file} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                
                # ----------------- Trunk Flexion/Extension -------------------
                data_label = ['TrunkTilt']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Tilt (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),20)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                                
                # ----------------- Pelvic Tilt -------------------------------
                data_label = ['PelvicTilt']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Tilt ROT (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-5)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Hip Flexion/Extention --------------------------
                data_label = ['HipFlexExt']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip Flexion-Extension (pelvis)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),60)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Knee Flexion/Extension ---------------------
                data_label = ['KneeFlexExt']
                ax = axes1[7]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Flexion/Extension (pelvis)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),80)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Ankle Dorsi/Plantarflexion ------------------------------
                data_label = ['DorsiPlanFlex']
                ax = axes1[8]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Dorsi-Plantarflexion (knee)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Hip Moment -------------------------
                data_label = ['HipFlexExtMoment']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Ext')
                    lowerstr = ('Flx')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try: 
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)  
                    ax.set_title('Hip Extensor Moment')
                    ax.set_ylabel('Nm/kg')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no hip sagittal moments')
                    ax.set_title('Hip Extensor Moment')
                    ax.set_ylabel('Nm/kg')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                # ----------------- Knee Moment --------------------
                data_label = ['KneeFlexExtMoment']
                ax = axes1[10]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Ext')
                    lowerstr = ('Flx')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Knee Extensor Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no knee sagittal moments')
                    ax.set_title('Knee Extensor Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Ankle Moment ----------------------------
                data_label = ['DorsiPlanFlexMoment']
                ax = axes1[11]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Ext')
                    lowerstr = ('Flx')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Ankle Plantarflexor Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no ankle sagittal moment')
                    ax.set_title('Ankle Plantarflexor Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Hip Power (Sagittal) -------------------------
                data_label = ['HipFlexExtPower']
                if normFile[0:2] == 'TD':
                    data_label = ['HipPower']
                    
                ax = axes1[12]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Gen')
                    lowerstr = ('Abs')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Hip Power')
                    ax.set_ylabel('Watts/kg')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),3)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no sagittal hip power')
                    ax.set_title('Hip Power (Sagittal)')
                    ax.set_ylabel('Watts/kg')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Knee extension power ---------------
                data_label = ['KneeFlexExtPower']
                if normFile[0:2] == 'TD':
                    data_label = ['KneePower']
                
                ax = axes1[13]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Gen')
                    lowerstr = ('Abs')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Knee Power')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),3)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no knee sagittal power')
                    ax.set_title('Knee Power (Sagittal)')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Ankle sagittal power ----------------------------
                data_label = ['DorsiPlanFlexPower']
                if normFile[0:2] == 'TD':
                    data_label = ['AnklePower']
                
                ax = axes1[14]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Gen')
                    lowerstr = ('Abs')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Ankle Power')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),5)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no ankle sagittal power')
                    ax.set_title('Ankle Power (Sagittal)')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -2
                    yupper = 5
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- figure layout options --------------------
                
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
               
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if plotNorm:
                    # --------------- Note on data used for norms -----------------
                    normDataUsed = 'Greenville'
                    if normFile[0:2] == 'TD':
                        normDataUsed = 'Greenville, Salt Lake, & Spokane'
                        # KineticMessage = 'When using combined norms, joint powers shown here are TOTAL joint powers, NOT sagittal joint powers'
                        # plt.gcf().text(0.92, titleRow, KineticMessage, fontsize=sf-1, rotation=90, color='r')
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    
                    filenamestr = ('pHP')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    # peak Knee Power plus 1 SD of mean
                    HPname = 'HipFlexExtPower'
                    if normFile[0:2] == 'TD':
                        HPname = 'HipPower'
                    pHPp1M = round(max(np.add(dataNmean_dict[HPname], dataNstd_dict[HPname])),2)
                    pHPm1M = round(max(np.subtract(dataNmean_dict[HPname], dataNstd_dict[HPname])),2)
                    plt.gcf().text(firstcol+0.185, 0.0175, pHPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.185, 0.0075, pHPm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0175, pHPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0075, pHPm1M, fontsize=sf-1, color='k')
                                   
                    filenamestr = ('pKP')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    # peak Knee Power plus 1 SD of mean
                    KPname = 'KneeFlexExtPower'
                    if normFile[0:2] == 'TD':
                        KPname = 'KneePower'
                    pKPp1M = round(max(np.add(dataNmean_dict[KPname], dataNstd_dict[KPname])),2)
                    pKPm1M = round(max(np.subtract(dataNmean_dict[KPname], dataNstd_dict[KPname])),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, pKPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, pKPm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, pKPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, pKPm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('pAP')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    APname = 'DorsiPlanFlexPower'
                    if normFile[0:2] == 'TD':
                        APname = 'AnklePower'
                    pAPp1M = round(max(np.add(dataNmean_dict[APname], dataNstd_dict[APname])),2)
                    pAPm1M = round(max(np.subtract(dataNmean_dict[APname], dataNstd_dict[APname])),2)
                    plt.gcf().text(firstcol+0.245, 0.0175, pAPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, pAPm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, pAPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, pAPm1M, fontsize=sf-1, color='k')
                                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                    
                    LpHP = round(max(data_dict['LeftHipFlexExtPower']),2)
                    plt.gcf().text(firstcol+0.185, rowvec[LeftPlotNum-1], LpHP, fontsize=sf-1, color='k')
                    
                    LpKP = round(max(data_dict['LeftKneeFlexExtPower']),2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LpKP, fontsize=sf-1, color='k')
                   
                    LpAP = round(max(data_dict['LeftDorsiPlanFlexPower']),2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], LpAP, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    
                    RpHP = round(max(data_dict['RightHipFlexExtPower']),2)
                    plt.gcf().text(nextcol+0.185, rowvec[RightPlotNum-1], RpHP, fontsize=sf-1, color='k')
                
                    RpKP = round(max(data_dict['RightKneeFlexExtPower']),2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RpKP, fontsize=sf-1, color='k')
                    
                    RpAP = round(max(data_dict['RightDorsiPlanFlexPower']),2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], RpAP, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')    
                    
                plotNorm = False
    
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1
        
        # Hide empty subplots if there are fewer graphs than subplots but only when a pdf page is created
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)) and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
            
    try:
        # Show the plot
        plt.show()
        # Save plot as PDF
        pdffile.savefig(fig)
        bookmarks.append(('Sagittal Kinetics', marknum))
        marknum += 1
    except:
        print(f'No SAGITTAL kinetics have been plotted for file {gcd_file}. Check to ensure force plate assignments have been made properly if expecting kinetics.')

def plot_coronalKinetics(self):
    global foldername
    global bookmarks
    global marknum
    fig = None
    plotNorm = False
    num_rows = 6
    num_cols=3
    
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file+'L') pulls the index of the first gcd file in checkboxes with the root name to reference appropriate file-path when accessing .gcd files from subfolders
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
            # check to see if kinetics data present, if not, skip file and move to next within 'checkboxes' for-loop
            limbassign = 'Left'
            if file[-1] == 'R':
                limbassign = 'Right'
            data_label = f'{limbassign}HipAbAdductMoment'
            
            # if normFile == 'SpokaneTD_Walking_ShrMdl Distal 51pts.GCD':
            #     continue
            if not data_label in data_dict.keys():
                print(f'{limbassign} CORONAL kinetics were not found in file {gcd_file}')
                gcd_count += 1
                if limbassign == 'Left':
                    LeftPlotNum += 1 
                    PlotNum = LeftPlotNum
                elif limbassign == 'Right':
                    RightPlotNum += 1 
                    PlotNum = RightPlotNum
                continue
            elif data_label in data_dict.keys() and limbassign == 'Left':
                plotloop = [0]
            elif data_label in data_dict.keys() and limbassign == 'Right':
                plotloop = [1]
            else:
                print(f'Check CORONAL kinetics regarding file {gcd_file}, limb-specific message should have been displayed or data plotted')
                
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            # Coronal kinetics requires Greenville norm data to plot norm bands
            CORnormFile = 'GreenevilleTD_Ave.GCD'
            if not fig:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Set pdf page and subplots -------------
                # Create a figure with subplots
                fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
                # fig.tight_layout(pad=2, w_pad=1.0, h_pad=1.0)
                fig.tight_layout()
                plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
                
                # fig.tight_layout(pad=3.0)  # Adjust spacing between subplots
                fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
                titlenamestr = 'Coronal Kinetics \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
                plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')
                
                # Flatten the axes1 array
                axes1 = axes1.flatten()
                plotNorm = True
        # ----------------------------- Plot data -----------------------------
        
            limb_spec = ['Left','Right']
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print('LEFT Limb data for file {gcd_file} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                                
                # ----------------- Trunk Flexion/Extension -------------------
                data_label = ['TrunkObliquity']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Up')
                    lowerstr = ('Dwn')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Obliquity (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),15)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                                
                # ----------------- Pelvic Tilt -------------------------------
                data_label = ['PelvicObliquity']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Up')
                    lowerstr = ('Dwn')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Obliquity ROT (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),15)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Hip Flexion/Extention --------------------------
                data_label = ['HipAbAdduct']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Add')
                    lowerstr = ('Abd')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip Ab-Adduction (pelvis)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),15)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Knee Flexion/Extension ---------------------
                data_label = ['KneeValgVar']
                ax = axes1[7]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Var')
                    lowerstr = ('Val')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Varus-Valgus (pelvis)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Hip Moment -------------------------
                data_label = ['HipAbAdductMoment']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Abd')
                    lowerstr = ('Add')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try: 
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)  
                    ax.set_title('Hip Abduction Moment')
                    ax.set_ylabel('Nm/kg')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no hip coronal moments')
                    ax.set_title('Hip Abduction Moment')
                    ax.set_ylabel('Nm/kg')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                # ----------------- Knee Moment --------------------
                data_label = ['KneeValgVarMoment']
                ax = axes1[10]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Val')
                    lowerstr = ('Var')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Knee Valgus Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no knee coronal moments')
                    ax.set_title('Knee Valgus Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                    # y-limits
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Ankle Moment ----------------------------
                data_label = ['FootAbAdductMoment']
                ax = axes1[11]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Abd')
                    lowerstr = ('Add')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Ankle Abduction Moment')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-1)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no ankle coronal moment')
                    ax.set_title('Ankle Abduction Moment')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -1
                    yupper = 2
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Hip Power (Coronal) -------------------------
                data_label = ['HipAbAdductPower']
                ax = axes1[12]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Gen')
                    lowerstr = ('Abs')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Hip Abduction Power (Coronal)')
                    ax.set_ylabel('Watts/kg')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),3)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no coroanl hip power')
                    ax.set_title('Hip Abduction Power (Coronal)')
                    ax.set_ylabel('Watts/kg')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- Knee Valg power ---------------
                data_label = ['KneeValgVarPower']
                ax = axes1[13]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    # motion direction text
                    upperstr = ('Gen')
                    lowerstr = ('Abs')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                try:
                    ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                    ax.set_title('Knee Valgus Power (Coronal)')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                    yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),3)
                    getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                    ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                    # ipsi foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot off lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                    # contra foot contact lines
                    x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                    x2 = x1
                    ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                except:
                    # print('no knee coronal power')
                    ax.set_title('Knee Valgus Power (Coronal)')
                    ax.set_xlabel('% Gait Cycle')
                    ax.set_xlim([0,datLen])
                    ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                    # y-limits
                    ylower = -2
                    yupper = 3
                    ax.set_ylim([ylower,yupper])
                    ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                
                #  ----------------- figure layout options --------------------
                
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if plotNorm:
                    # --------------- Note on data used for norms -----------------
                    normDataUsed = 'Greenville'
                    if normFile[0:2] == 'TD':
                        normDataUsed = 'Greenville, Salt Lake, & Spokane'
                        # KineticMessage = 'When using combined norms, joint powers shown here are TOTAL joint powers, NOT sagittal joint powers'
                        # plt.gcf().text(0.92, titleRow, KineticMessage, fontsize=sf-1, rotation=90, color='r')
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                    
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    
                    filenamestr = ('pHP')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    # peak Knee Power plus 1 SD of mean
                    pHPp1M = round(max(np.add(dataNmean_dict['HipAbAdductPower'], dataNstd_dict['HipAbAdductPower'])),2)
                    pHPm1M = round(max(np.subtract(dataNmean_dict['HipAbAdductPower'], dataNstd_dict['HipAbAdductPower'])),2)
                    plt.gcf().text(firstcol+0.185, 0.0175, pHPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.185, 0.0075, pHPm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0175, pHPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0075, pHPm1M, fontsize=sf-1, color='k')
                                   
                    filenamestr = ('pKP')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    # peak Knee Power plus 1 SD of mean
                    pKPp1M = round(max(np.add(dataNmean_dict['KneeValgVarPower'], dataNstd_dict['KneeValgVarPower'])),2)
                    pKPm1M = round(max(np.subtract(dataNmean_dict['KneeValgVarPower'], dataNstd_dict['KneeValgVarPower'])),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, pKPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, pKPm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, pKPp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, pKPm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('pAM')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    pAMp1M = round(max(np.add(dataNmean_dict['FootAbAdductMoment'], dataNstd_dict['FootAbAdductMoment'])),2)
                    pAMm1M = round(max(np.subtract(dataNmean_dict['FootAbAdductMoment'], dataNstd_dict['FootAbAdductMoment'])),2)
                    plt.gcf().text(firstcol+0.245, 0.0175, pAMp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, pAMm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, pAMp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, pAMm1M, fontsize=sf-1, color='k')
                                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                    
                    LpHP = round(max(data_dict['LeftHipAbAdductPower']),2)
                    plt.gcf().text(firstcol+0.185, rowvec[LeftPlotNum-1], LpHP, fontsize=sf-1, color='k')
                    
                    LpKP = round(max(data_dict['LeftKneeValgVarPower']),2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LpKP, fontsize=sf-1, color='k')
                   
                    LpAP = round(max(data_dict['LeftFootAbAdductMoment']),2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], LpAP, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                     
                    RpHP = round(max(data_dict['RightHipAbAdductPower']),2)
                    plt.gcf().text(nextcol+0.185, rowvec[RightPlotNum-1], RpHP, fontsize=sf-1, color='k')
                
                    RpKP = round(max(data_dict['RightKneeValgVarPower']),2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RpKP, fontsize=sf-1, color='k')
                    
                    RpAP = round(max(data_dict['RightFootAbAdductMoment']),2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], RpAP, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')  
                    
                plotNorm = False
    
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1
        
        # Hide empty subplots if there are fewer graphs than subplots but only when a pdf page is created
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)) and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
                
    try:
        # Show the plot
        plt.show()
        # Save plot as PDF
        pdffile.savefig(fig)
        bookmarks.append(('Coronal Kinetics', marknum))
        marknum += 1
    except:
        print(f'No CORONAL kinetics have been plotted for file {gcd_file}. \n\nCheck to ensure force plate assignments have been made properly if expecting kinetics. \n\n**If using Spokane Norms with 51 data points, coronal kinetics are not available.')

def plot_MuscleLengthVel(self):
    global foldername
    global bookmarks
    global marknum
    num_rows = 6
    num_cols=3
    
    # Create a figure with subplots
    fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
    # fig.tight_layout(pad=2, w_pad=1.0, h_pad=1.0)
    fig.tight_layout()
    plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
    
    # fig.tight_layout(pad=3.0)  # Adjust spacing between subplots
    fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
    titlenamestr = 'Muscle Length & Velocity \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
    plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')
    
    # Flatten the axes1 array
    axes1 = axes1.flatten()
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            if gcd_count == 0:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
            
            limb_spec = ['Left','Right']
            plotloop = [0,1]
            plotLimb = file[-1]
            if plotLimb == 'L':
                plotloop = [0]
            elif plotLimb == 'R':
                plotloop = [1]
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print('LEFT Limb data for file {gcd_file} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                                
                # ----------------- Trunk Flexion/Extension -------------------
                data_label = ['TrunkTilt']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Trunk Tilt (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),20)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                                
                # ----------------- Pelvic Tilt -------------------------------
                data_label = ['PelvicTilt']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Ant')
                    lowerstr = ('Pst')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Pelvic Tilt ROT (global)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-5)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Iliopsoas Length -------------------------------
                data_label = ['IlioPsoasLength']
                ax = axes1[4]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Lng')
                    lowerstr = ('Sht')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('IlioPsoas Length (normalized)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),0.8)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),1.2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(1, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Hip Flexion/Extention --------------------------
                data_label = ['HipFlexExt']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hip Flexion-Extension (pelvis)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-15)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),60)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Med Hamstring Length --------------------------
                data_label = ['MedHamstringLength']
                ax = axes1[7]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Lng')
                    lowerstr = ('Sht')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Med Hamstring Length (norm)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),0.8)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),1.2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(1, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Lat Hamstring Length --------------------------
                data_label = ['LatHamstringLength']
                ax = axes1[8]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Lng')
                    lowerstr = ('Sht')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Lat Hamstring Length (norm)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),0.8)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),1.2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(1, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Knee Flexion/Extension ---------------------
                data_label = ['KneeFlexExt']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Flx')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Knee Flexion/Extension (pelvis)')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-20)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),80)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Med Hamstring Velocity --------------------------
                data_label = ['MedHamstringVelocity']
                ax = axes1[10]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Fst')
                    lowerstr = ('Slw')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Med Hamstring Velocity (norm)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Lat Hamstring Velocity --------------------------
                data_label = ['LatHamstringVelocity']
                ax = axes1[11]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Fst')
                    lowerstr = ('Slw')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Lat Hamstring Velocity (norm)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-2)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Ankle Dorsi/Plantarflexion ------------------------------
                data_label = ['DorsiPlanFlex']
                ax = axes1[12]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Dorsi-Plantarflexion (knee)')
                ax.set_ylabel('range (deg)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Gastroc Length --------------------------
                data_label = ['GastrocLength']
                ax = axes1[13]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Lng')
                    lowerstr = ('Sht')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Gastrocnemius Length (norm)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),0.8)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),1.2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(1, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- Soleus Length --------------------------
                data_label = ['SoleusLength']
                ax = axes1[14]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if gcd_count == 0: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Lng')
                    lowerstr = ('Sht')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Soleus Length (norm)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),0.8)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),1.2)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(1, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- figure layout options --------------------
                
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if gcd_count == 0:
                    # --------------- Note on data used for norms -----------------
                    normDataUsed = 'Greenville, Salt Lake, & Spokane'
                    if normFile[0:2] == 'Gr':
                        normDataUsed = 'Greenville'
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    
                    filenamestr = ('GDI')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    try:
                        GDM = round(dataNmean_dict['GDI'][0],2)
                        GDSD = round(dataNstd_dict['GDI'][0],2)
                        plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(firstcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                    except:
                        print('GDI not printed to muscle length plots')
                                   
                    filenamestr = ('Spd')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    Spp1M = round((dataNmean_dict['Speed'][0]/1000) + (dataNstd_dict['Speed'][0]/1000),2)
                    Spm1M = round((dataNmean_dict['Speed'][0]/1000) - (dataNstd_dict['Speed'][0]/1000),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('Cad')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    cap1M = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    cam1M = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                    LSL = round(data_dict['LeftSpeed'][0]/1000,2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LSL, fontsize=sf-1, color='k')
                   
                    Lca = round(data_dict['LeftCadence'][0],2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], Lca, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    RSL = round(data_dict['RightSpeed'][0]/1000,2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RSL, fontsize=sf-1, color='k')
                    
                    Rca = round(data_dict['RightCadence'][0],2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], Rca, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')    
                    
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1     
            
        # Hide empty subplots if there are fewer graphs than subplots but only when a pdf page is created
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)) and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        
    # Show the plot
    plt.show()
    # Save plot as PDF
    pdffile.savefig(fig)
    bookmarks.append(('Muscle Length & Velocity', marknum))
    marknum += 1

def plot_EMG(self):   
    global bookmarks
    global marknum
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    # plotting column index
    colIDX = 0
    
    for file in checkboxes:
        
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            
            # Determine if both, left only, or right only EMG data will be plotted to specify how many files will plot to a single pdf page
            if gcd_count == 0:
                newFig = True
                colIDX = 0
            elif varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0: # both, new fig with each odd number of files plotted after 1, i.e. each pdf page gets a left and a right, then a new pdf page is created for the next pair of limbs
                newFig = True
                colIDX = 0
            elif varLR.get() == 1 and gcd_count%3 == 0: # left, new fig after every 3 left files plotted to one pdf page
                newFig = True
                colIDX = 0
            elif varLR.get() == 2 and gcd_count%3 == 0: # right, new fig after every 3 right files plotted to one pdf page
                newFig = True 
                colIDX = 0
            else:
                newFig = False
                colIDX += 1
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            
            # index into folder file names is divided by 2 because each file is loaded into checkboxes twice for left/right plotting
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once per column
            if gcd_count < 2 and varLR.get() == 0:
                isEMG = True
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
            elif gcd_count < 3 and varLR.get() != 0:
                isEMG = True
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
            plotLimb = file[-1]
            if plotLimb == 'L':
                Lnum = 0
            elif plotLimb == 'R':
                Lnum = 1     
        # ----------------------------- Plot data -----------------------------
            
            Elimb_spec = ['LeftRawL','RightRawR']
            limb_spec = ['Left','Right']
            
            num_rows = 6
            num_cols=3
            
            if newFig == True:
                # Create a figure with subplots
                fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
                fig.tight_layout()
                plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
                
                fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
                titlenamestr = 'Muscle Activity \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
                plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')
                # Flatten the axes1 array
                axes1 = axes1.flatten()
                # checking if a left or right limb has already been plotted - used to keep file names plotting to appropriate line
                Lplotted = False
                Rplotted = False
            
            # for Lnum in plotColumn:
            n = 16 # default number of colormap vectors to use in plotting
            if gcdNum_selected < 16 and varLR.get() == 0:
                n = round(gcdNum_selected/2)
            elif gcdNum_selected < 12 and varLR.get() != 0:
                n = gcdNum_selected
           
            if Lnum == 0:
                try:
                    # below here should work
                    confLeft = [Elimb_spec[Lnum] + 'RectFem']
                    cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                    PlotNum = LeftPlotNum
                    LeftPlotNum += 1
                    datLen = len(data_dict[confLeft[0]])
                except:
                    print('LEFT EMG data for file {gcd_file} has not been plotted')
                    continue   
            elif Lnum == 1:
                try:
                    confRight = [Elimb_spec[Lnum] + 'RectFem']
                    cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                    PlotNum = RightPlotNum
                    RightPlotNum += 1
                    datLen = len(data_dict[confRight[0]])
                except:
                    print('RIGHT EMG data for file {gcd_file} has not been plotted')
                    continue
                    
            # changing colormap to gray when total file numbers over 10 (5 per side)
            if gcdNum_selected > 16:
                cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                
            # setting plotting parameters
            x = list(range(0,datLen))
            # xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
            sf = 8
            mf = 10
            lf = 12
            
            plt.rc('font', size=sf)          # controls default text sizes
            plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
            plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
            plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
            plt.rc('legend', fontsize=mf)    # legend fontsize
            plt.rc('figure', titlesize=lf)   # fontsize of the figure title
            
            # Get EMG checkbox and labels selected on first frame
            Lcheckbox_info, Rcheckbox_info = self.get_EMGcheckbox_info()
            
            for Lidx, Lvar in enumerate(Lcheckbox_info):
                print(Lvar)
                if Lcheckbox_info[Lvar]:
                    a  = 1
                    
            for key, item in self.Lcomboboxes.items():
                if item.get():
                    print(item.get())
            
            for Rlabel, Rvar in self.Rcheckbox_vars.items():
                if Rvar.get():
                    print(f'Right variables selected: {Rvar.get()}')
            
            # ----------------- Rectus Femoris ----------------------------
            data_label = ['RectFem']
            axIDX = [0,1,2]
            ax = axes1[axIDX[colIDX]]
            ax.set_facecolor(FaceCol)
            ax.patch.set_alpha(FaceColAlpha)
            
            # Get norm data and interpolate to length of collected EMG data
            VariableData = np.array(dataNmean_dict[data_label[0]+'Envelope'])
            Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
            x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
            upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
            
            # Get EMG max absolute value, if data exists
            plotRF = True
            try:
                Edata = np.array(data_dict[Elimb_spec[Lnum] + data_label[0]])
                EdataMean = np.mean(Edata)
                Edata = Edata - EdataMean
                ScalFac = max(abs(Edata))
            except:
                print(f'{limb_spec[Lnum]} Rectus Femoris data not present')
                ScalFac = max(upperUnScaleN)
                plotRF  = False
            
            # norm bands
            lowerN = [0] * datLen            
            upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
            
            # plot EMG data if it exists
            if plotRF:
                ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                
            y_limits = ax.get_ylim()
            yupper = 1.4 * y_limits[1]
            ylower = -yupper
            y_range = yupper - ylower
            # EMG on-off bars
            ax.hlines(ylower + 0.05*y_range, xmin=0, xmax=0.15*datLen, ls='-', color='k', linewidth=2)
            ax.hlines(ylower + 0.05*y_range, xmin=0.55*datLen, xmax=0.7*datLen, ls='-', color='k', linewidth=2)
            ax.hlines(ylower + 0.05*y_range, xmin=0.95*datLen, xmax=datLen, ls='-', color='k', linewidth=2)
            ax.set_ylim([ylower, yupper])
            ax.set_title(limb_spec[Lnum] +' Rectus Femoris (raw)')
            ax.set_xlim([0,datLen])
            ax.set_xticks(np.linspace(0,datLen,6), ['','','','','',''])
            ax.fontsize = sf
            ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
            if newFig:
                ax.set_ylabel('amplitude (Volts)')
            
            # ipsi foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'FootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot contact lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            
            # ----------------- Vastus Lateralis ----------------------------
            data_label = ['VastLat']
            axIDX = [3,4,5]
            ax = axes1[axIDX[colIDX]]
            ax.set_facecolor(FaceCol)
            ax.patch.set_alpha(FaceColAlpha)
            
            # Get norm data and interpolate to length of collected EMG data
            VariableData = np.array(dataNmean_dict[data_label[0]+'Envelope'])
            Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
            x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
            upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
            
            # Get EMG max absolute value, if data exists
            plotVL = False
            try:
                Edata = np.array(data_dict[Elimb_spec[Lnum] + data_label[0]])
                EdataMean = np.mean(Edata)
                Edata = Edata - EdataMean
                ScalFac = max(abs(Edata))
            except:
                print(f'{limb_spec[Lnum]} Vastus Lateralis data not present')
                ScalFac = max(upperUnScaleN)
                plotVL  = False
            
            # norm bands
            lowerN = [0] * datLen            
            upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
            
            # plot EMG data if it exists
            if plotVL:
                ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                
            y_limits = ax.get_ylim()
            yupper = 1.4 * y_limits[1]
            ylower = -yupper
            y_range = yupper - ylower
            
            ax.set_ylim([ylower, yupper])
            ax.set_title(limb_spec[Lnum] +' Vastus Lateralis (raw)')
            ax.set_xlim([0,datLen])
            ax.set_xticks(np.linspace(0,datLen,6), ['','','','','',''])
            ax.fontsize = sf
            ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
            # EMG on-off bars
            ax.hlines(ylower + 0.05*y_range, xmin=0, xmax=0.25*datLen, ls='-', color='k', linewidth=2)
            ax.hlines(ylower + 0.05*y_range, xmin=0.95*datLen, xmax=datLen, ls='-', color='k', linewidth=2)
            if newFig:
                ax.set_ylabel('amplitude (Volts)')
            
            # ipsi foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'FootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot contact lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            
            # ----------------- Medial Hamstring ----------------------------
            data_label = ['MedHams']
            axIDX = [6,7,8]
            ax = axes1[axIDX[colIDX]]
            ax.set_facecolor(FaceCol)
            ax.patch.set_alpha(FaceColAlpha)
            
            # Get norm data and interpolate to length of collected EMG data
            VariableData = np.array(dataNmean_dict[data_label[0]+'Envelope'])
            Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
            x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
            upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
            
            # Get EMG max absolute value, if data exists
            plotRF = True
            try:
                Edata = np.array(data_dict[Elimb_spec[Lnum] + data_label[0]])
                EdataMean = np.mean(Edata)
                Edata = Edata - EdataMean
                ScalFac = max(abs(Edata))
            except:
                print(f'{limb_spec[Lnum]} Medial Hamstring data not present')
                ScalFac = max(upperUnScaleN)
                plotRF  = False
            
            # norm bands
            lowerN = [0] * datLen            
            upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
            
            # plot EMG data if it exists
            if plotRF:
                ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                
            y_limits = ax.get_ylim()
            yupper = 1.4 * y_limits[1]
            ylower = -yupper
            y_range = yupper - ylower
            
            ax.set_ylim([ylower, yupper])
            ax.set_title(limb_spec[Lnum] +' Medial Hamstring (raw)')
            ax.set_xlim([0,datLen])
            ax.set_xticks(np.linspace(0,datLen,6), ['','','','','',''])
            ax.fontsize = sf
            ax.set_ylim([ylower,yupper])
            ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
            # EMG on-off bars
            ax.hlines(ylower + 0.05*y_range, xmin=0, xmax=0.05*datLen, ls='-', color='k', linewidth=2)
            ax.hlines(ylower + 0.05*y_range, xmin=0.9*datLen, xmax=datLen, ls='-', color='k', linewidth=2)
            if newFig:
                ax.set_ylabel('amplitude (Volts)')
                
            # ipsi foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'FootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot contact lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            
            # ----------------- Medial Gastrocnemius ----------------------------
            data_label = ['GasTroc']
            axIDX = [9,10,11]
            ax = axes1[axIDX[colIDX]]
            ax.set_facecolor(FaceCol)
            ax.patch.set_alpha(FaceColAlpha)
            
            # Get norm data and interpolate to length of collected EMG data
            VariableData = np.array(dataNmean_dict[data_label[0]+'Envelope'])
            Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
            x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
            upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
            
            # Get EMG max absolute value, if data exists
            plotRF = True
            try:
                Edata = np.array(data_dict[Elimb_spec[Lnum] + data_label[0]])
                EdataMean = np.mean(Edata)
                Edata = Edata - EdataMean
                ScalFac = max(abs(Edata))
            except:
                print(f'{limb_spec[Lnum]} Medial Gastroc data not present')
                ScalFac = max(upperUnScaleN)
                plotRF  = False
            
            # norm bands
            lowerN = [0] * datLen            
            upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
            
            # plot EMG data if it exists
            if plotRF:
                ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                
            y_limits = ax.get_ylim()
            yupper = 1.4 * y_limits[1]
            ylower = -yupper
            y_range = yupper - ylower
            
            ax.set_ylim([ylower, yupper])
            ax.set_title(limb_spec[Lnum] +' Medial Gastroc (raw)')
            ax.set_xlim([0,datLen])
            ax.set_xticks(np.linspace(0,datLen,6), ['','','','','',''])
            ax.fontsize = sf
            ax.set_ylim([ylower,yupper])
            ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
            # EMG on-off bars
            ax.hlines(ylower + 0.05*y_range, xmin=0.15*datLen, xmax=0.5*datLen, ls='-', color='k', linewidth=2)
            if newFig:
                ax.set_ylabel('amplitude (Volts)')
                
            # ipsi foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'FootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot contact lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            
            # ----------------- Anterior Tibialis ----------------------------
            data_label = ['TibAnte']
            axIDX = [12,13,14]
            ax = axes1[axIDX[colIDX]]
            ax.set_facecolor(FaceCol)
            ax.patch.set_alpha(FaceColAlpha)
            
            # Get norm data and interpolate to length of collected EMG data
            VariableData = np.array(dataNmean_dict[data_label[0]+'Envelope'])
            Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
            x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
            upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
            
            # Get EMG max absolute value, if data exists
            plotRF = True
            try:
                Edata = np.array(data_dict[Elimb_spec[Lnum] + data_label[0]])
                EdataMean = np.mean(Edata)
                Edata = Edata - EdataMean
                ScalFac = max(abs(Edata))
            except:
                print(f'{limb_spec[Lnum]} Tibialis Anterior data not present')
                ScalFac = max(upperUnScaleN)
                plotRF  = False
            
            # norm bands
            lowerN = [0] * datLen            
            upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
            
            # plot EMG data if it exists
            if plotRF:
                ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                
            y_limits = ax.get_ylim()
            yupper = 1.4 * y_limits[1]
            ylower = -yupper
            y_range = yupper - ylower
            
            ax.set_ylim([ylower, yupper])
            ax.set_title(limb_spec[Lnum] +' Tibialis Anterior (raw)')
            ax.set_xlabel('% Gait Cycle')
            ax.set_xlim([0,datLen])
            ax.set_xticks(np.linspace(0,datLen,6), ['0','20','40','60','80','100'])
            ax.fontsize = sf
            ax.set_ylim([ylower,yupper])
            ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
            # EMG on-off bars
            ax.hlines(ylower + 0.05*y_range, xmin=0, xmax=0.15*datLen, ls='-', color='k', linewidth=2)
            ax.hlines(ylower + 0.05*y_range, xmin=0.55*datLen, xmax=datLen, ls='-', color='k', linewidth=2)
            if newFig:
                ax.set_ylabel('amplitude (Volts)')
                
            # ipsi foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'FootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot off lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            # contra foot contact lines
            x1 = datLen*(data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/100)
            x2 = x1
            ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
            
            #  ----------------- figure layout options --------------------
             
            # -----------------  Adding GCD file names --------------------
            # filename row and column spacing and adjustments
            firstcol = 0.35
            nextcol = 0.635
            rowvecBase = list([0.105,0.09,0.075])
            rowvec = np.tile(rowvecBase,round(gcdNum_selected/3) + gcdNum_selected%3)
            titlerowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
            titleRow = 0.1175
            
            # GCD file name to print
            gcdfilestr = (f'{gcd_file}')
                
            if newFig:
                # --------------- Note on data used for norms -----------------
                normDataUsed = 'Greenville, Salt Lake, & Spokane'
                if normFile[0:2] == 'Gr':
                    normDataUsed = 'Greenville'
                normMessage = f"**Gray bands are mean EMG rectified envelope during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
            
                # Patient info
                plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[2], 'Date: ' +studydate, fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[5], 'Brace: ' +brace, fontsize=sf)
                plt.gcf().text(0.06, titlerowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                
                # filename titles
                filenamestr = ('File Names')
                plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
            
                filenamestr = ('GDI')
                plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                try:
                    GDM = round(dataNmean_dict['GDI'][0],2)
                    GDSD = round(dataNstd_dict['GDI'][0],2)
                    plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                except:
                    print('GDI is not printed to EMG page')
                               
                filenamestr = ('Spd')
                plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                Spp1M = round((dataNmean_dict['Speed'][0]/1000) + (dataNstd_dict['Speed'][0]/1000),2)
                Spm1M = round((dataNmean_dict['Speed'][0]/1000) - (dataNstd_dict['Speed'][0]/1000),2)
                plt.gcf().text(firstcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                plt.gcf().text(firstcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                                
                filenamestr = ('Cad')
                plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                cap1M = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                cam1M = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                plt.gcf().text(firstcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                plt.gcf().text(firstcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                plt.gcf().text(nextcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                            
            # Single Value Data
            rvIDXL = 0
            rvIDXR = 0
            # added exception for plotting bilateral data with single R/L files to maintain file names plotting to correct slot: e.g. file 02R, 03R, 04L, 05L
            if varLR.get() == 0 and file[-1] == 'L' and gcd_count > 0 and colIDX == 1 and Lplotted == True:
                rvIDXL += 1
            elif varLR.get() == 0 and file[-1] == 'R' and gcd_count > 0 and colIDX == 1 and Rplotted == True:
                rvIDXR += 1
            
            if varLR.get() == 1:
                rvIDXL = LeftPlotNum - 1
            elif varLR.get() == 2:
                rvIDXR = RightPlotNum -1
                
            #Left
            if file[-1] == 'L':
                Lplotted = True
                LSL = round(data_dict['LeftSpeed'][0]/1000,2)
                plt.gcf().text(firstcol+0.215, rowvec[rvIDXL], LSL, fontsize=sf-1, color='k')
               
                Lca = round(data_dict['LeftCadence'][0],2)
                plt.gcf().text(firstcol+0.245, rowvec[rvIDXL], Lca, fontsize=sf-1, color='k')
            # Right
            elif file[-1] == 'R':
                Rplotted = True
                RSL = round(data_dict['RightSpeed'][0]/1000,2)
                plt.gcf().text(nextcol+0.215, rowvec[rvIDXR], RSL, fontsize=sf-1, color='k')
                
                Rca = round(data_dict['RightCadence'][0],2)
                plt.gcf().text(nextcol+0.245,    rowvec[rvIDXR], Rca, fontsize=sf-1, color='k')
            
            # Plot left file names
            # if gcdNum_selected < 12 and file[-1] == 'L':
            if file[-1] == 'L':
                plt.gcf().text(firstcol, rowvec[rvIDXL], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                            
            # Plot right file names
            # if gcdNum_selected < 12 and file[-1] == 'R':
            if file[-1] == 'R':
                plt.gcf().text(nextcol, rowvec[rvIDXR], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
            
            if checkboxes[file].get():
                gcd_count += 1        
            
        # Hide empty subplots if there are fewer graphs than subplots but only when a pdf page is created
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count%3 == 0 and gcdNum_selected > 3)) and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        
        if checkboxes[file].get() and varLR.get() == 0 and gcd_count%2 == 0:
            # Show the plot
            plt.show()
            # Save plot as PDF
            pdffile.savefig(fig)
            bookmarks.append((f'EMGfile_{gcd_file[-6:-4]}', marknum))
            marknum += 1
        elif checkboxes[file].get() and (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)):
            # Show the plot
            plt.show()
            # Save plot as PDF
            pdffile.savefig(fig)
            bookmarks.append((f'EMGfile_{gcd_file[-6:-4]}', marknum))
            marknum += 1

def plot_SpatioTemporal(self):
    global foldername
    global bookmarks
    global marknum
    num_rows = 6
    num_cols=3
    
    # Create a figure with subplots
    fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
    fig.tight_layout()
    plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
    
    fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
    titlenamestr = 'Spatiotemporal Parameters \n' +condition[0:-1] +' ' +report[0:-1]
    plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')

    # Flatten the axes1 array
    axes1 = axes1.flatten()
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            if gcd_count == 0:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
            
            limb_spec = ['Left','Right']
            plotloop = [0,1]
            plotLimb = file[-1]
            if plotLimb == 'L':
                plotloop = [0]
            elif plotLimb == 'R':
                plotloop = [1]
            
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                    PlotNum = LeftPlotNum
                    LeftPlotNum += 1
                     
                elif Lnum == 1:
                    
                    cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                    PlotNum = RightPlotNum
                    RightPlotNum += 1
                    
                # changing colormap to gray when total file numbers over 16 (8 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                sf = 8
                mf = 10
                lf = 12
                
                #  ----------------- figure layout options --------------------
                # Hide empty subplots if there are fewer graphs than subplots
                for j in list(range(0,18)):
                    axes1[j].axis('off')
                 
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                texRot = 65
                firstrow = 0.88
                lastrow = 0.1175
                rowspace = 0.02
                patientrow = 0.015
                firstcol = 0.06
                colspace = 0.0425
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                # Print patient info, data titles, and norm data only once
                if gcd_count == 0:
                    # --------------- Note on data used for norms -----------------
                    normDataUsed = 'Greenville, Salt Lake, & Spokane'
                    if normFile[0:2] == 'Gr':
                        normDataUsed = 'Greenville'
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(firstcol, lastrow-(patientrow*0), 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*1), 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*2), 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*3), 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*4), 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*5), 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*6), 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(firstcol, lastrow-(patientrow*7), 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, firstrow-(rowspace*7), 'Left '+filenamestr, fontsize=lf, color='k')
                    plt.gcf().text(firstcol, firstrow-(rowspace*8), 'Typ. Developing Mean+1SD', fontsize=sf, color='k')
                    plt.gcf().text(firstcol, firstrow-(rowspace*9), 'Typ. Developing Mean-1SD', fontsize=sf, color='k')
                    plt.gcf().text(firstcol, firstrow-(rowspace*25), 'Right '+filenamestr, fontsize=lf, color='k')
                    plt.gcf().text(firstcol, firstrow-(rowspace*26), 'Typ. Developing Mean+1SD', fontsize=sf, color='k')
                    plt.gcf().text(firstcol, firstrow-(rowspace*27), 'Typ. Developing Mean-1SD', fontsize=sf, color='k')
                    
                    # Data titles
                    # left
                    filenamestr = ('Opposite Toe Off (%GC)')
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Opposite IC (%GC)')
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Toe Off (%GC)')
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Single Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('1st Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('2nd Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stance (%GC)')
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Swing (%GC)')
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Step Length (m)')
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stride Length (m)')
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Step Time (s)')
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stride Time (s)')
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Cadence (steps/min)')
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Speed (m/s)')
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*7), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    # right
                    filenamestr = ('Opposite Toe Off (%GC)')
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Opposite IC (%GC)')
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Toe Off (%GC)')
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Single Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('1st Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('2nd Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Double Support (%GC)')
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stance (%GC)')
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Swing (%GC)')
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Step Length (m)')
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stride Length (m)')
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Step Time (s)')
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Stride Time (s)')
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Cadence (steps/min)')
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    filenamestr = ('Speed (m/s)')
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*25), filenamestr, rotation=texRot, fontsize=mf-1, color='k')
                    
                # Norm data
                    # left +1SD
                    normDAT = round(dataNmean_dict['OppositeFootOff'][0] + dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['OppositeFootContact'][0] + dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['FootOff'][0] + dataNstd_dict['FootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['SingleSupport'][0] + dataNstd_dict['SingleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport1'][0] + dataNstd_dict['DoubleSupport1'][0],1)
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['DoubleSupport2'][0] + dataNstd_dict['DoubleSupport2'][0],1)
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Stance'][0] + dataNstd_dict['Stance'][0],1)
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Swing'][0] + dataNstd_dict['Swing'][0],1)
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StepLength'][0] + dataNstd_dict['StepLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StepTime'][0] + dataNstd_dict['StepTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport'][0] + dataNstd_dict['DoubleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*8), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StrideLength'][0] + dataNstd_dict['StrideLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StrideTime'][0] + dataNstd_dict['StrideTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['Speed'][0] + dataNstd_dict['Speed'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*8), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                
                    # left -1SD
                    normDAT = round(dataNmean_dict['OppositeFootOff'][0] - dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['OppositeFootContact'][0] - dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['FootOff'][0] - dataNstd_dict['FootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['SingleSupport'][0] - dataNstd_dict['SingleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport1'][0] - dataNstd_dict['DoubleSupport1'][0],1)
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['DoubleSupport2'][0] - dataNstd_dict['DoubleSupport2'][0],1)
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Stance'][0] - dataNstd_dict['Stance'][0],1)
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Swing'][0] - dataNstd_dict['Swing'][0],1)
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StepLength'][0] - dataNstd_dict['StepLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StepTime'][0] - dataNstd_dict['StepTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport'][0] - dataNstd_dict['DoubleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*9), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StrideLength'][0] - dataNstd_dict['StrideLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StrideTime'][0] - dataNstd_dict['StrideTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['Speed'][0] - dataNstd_dict['Speed'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*9), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                
                # right
                    # right +1SD
                    normDAT = round(dataNmean_dict['OppositeFootOff'][0] + dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['OppositeFootContact'][0] + dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['FootOff'][0] + dataNstd_dict['FootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['SingleSupport'][0] + dataNstd_dict['SingleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport1'][0] + dataNstd_dict['DoubleSupport1'][0],1)
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['DoubleSupport2'][0] + dataNstd_dict['DoubleSupport2'][0],1)
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Stance'][0] + dataNstd_dict['Stance'][0],1)
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Swing'][0] + dataNstd_dict['Swing'][0],1)
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StepLength'][0] + dataNstd_dict['StepLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StepTime'][0] + dataNstd_dict['StepTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport'][0] + dataNstd_dict['DoubleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*26), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StrideLength'][0] + dataNstd_dict['StrideLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StrideTime'][0] + dataNstd_dict['StrideTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['Speed'][0] + dataNstd_dict['Speed'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*26), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                
                    # left -1SD
                    normDAT = round(dataNmean_dict['OppositeFootOff'][0] - dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['OppositeFootContact'][0] - dataNstd_dict['OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['FootOff'][0] - dataNstd_dict['FootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['SingleSupport'][0] - dataNstd_dict['SingleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport1'][0] - dataNstd_dict['DoubleSupport1'][0],1)
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['DoubleSupport2'][0] - dataNstd_dict['DoubleSupport2'][0],1)
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Stance'][0] - dataNstd_dict['Stance'][0],1)
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Swing'][0] - dataNstd_dict['Swing'][0],1)
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StepLength'][0] - dataNstd_dict['StepLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StepTime'][0] - dataNstd_dict['StepTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    
                    normDAT = round(dataNmean_dict['DoubleSupport'][0] - dataNstd_dict['DoubleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*27), str(normDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['StrideLength'][0] - dataNstd_dict['StrideLength'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['StrideTime'][0] - dataNstd_dict['StrideTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    normDAT = round((dataNmean_dict['Speed'][0] - dataNstd_dict['Speed'][0])/1000,2)
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*27), str(normDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    
                # Single Value Data
                #Left
                if (Lnum == 0 and LeftPlotNum < 9):
                    # Patient data
                    plt.gcf().text(firstcol, firstrow-(rowspace*(9+LeftPlotNum)), gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=mf-1, color=cc[PlotNum])
                    patientDAT = round(data_dict[limb_spec[Lnum] +'OppositeFootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'OppositeFootContact'][0],1)
                    plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'FootOff'][0],1)
                    plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'SingleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport1'][0],1)
                    plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport2'][0],1)
                    plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'Stance'][0],1)
                    plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'Swing'][0],1)
                    plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport'][0],1)
                    plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'StepLength'][0]/1000,2)
                    plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'StrideLength'][0]/1000,2)
                    plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'StepTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'StrideTime'][0],2)
                    plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'Cadence'][0],2)
                    plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                    patientDAT = round(data_dict[limb_spec[Lnum] +'Speed'][0]/1000,2)
                    plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*(9+LeftPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                # Right
                elif (Lnum == 1 and RightPlotNum < 9):
                   # Patient data
                   plt.gcf().text(firstcol, firstrow-(rowspace*(27+RightPlotNum)), gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=mf-1, color=cc[PlotNum])
                   patientDAT = round(data_dict[limb_spec[Lnum] +'OppositeFootOff'][0],1)
                   plt.gcf().text(firstcol+(colspace*5), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'OppositeFootContact'][0],1)
                   plt.gcf().text(firstcol+(colspace*6), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'FootOff'][0],1)
                   plt.gcf().text(firstcol+(colspace*7), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'SingleSupport'][0],1)
                   plt.gcf().text(firstcol+(colspace*8), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport1'][0],1)
                   plt.gcf().text(firstcol+(colspace*9), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport2'][0],1)
                   plt.gcf().text(firstcol+(colspace*10), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'Stance'][0],1)
                   plt.gcf().text(firstcol+(colspace*12), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'Swing'][0],1)
                   plt.gcf().text(firstcol+(colspace*13), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'DoubleSupport'][0],1)
                   plt.gcf().text(firstcol+(colspace*11), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT)+'%', fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'StepLength'][0]/1000,2)
                   plt.gcf().text(firstcol+(colspace*14), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'StrideLength'][0]/1000,2)
                   plt.gcf().text(firstcol+(colspace*15), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'StepTime'][0],2)
                   plt.gcf().text(firstcol+(colspace*16), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'StrideTime'][0],2)
                   plt.gcf().text(firstcol+(colspace*17), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'Cadence'][0],2)
                   plt.gcf().text(firstcol+(colspace*18), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                   patientDAT = round(data_dict[limb_spec[Lnum] +'Speed'][0]/1000,2)
                   plt.gcf().text(firstcol+(colspace*19), firstrow-(rowspace*(27+RightPlotNum)), str(patientDAT), fontsize=sf-1, color='k', horizontalalignment='left')
                
        if checkboxes[file].get():
            gcd_count += 1
                
    # display message that not all data has been shown when more than 8 files are selected
    if gcdNum_selected > 16:
        plt.gcf().text(firstcol, lastrow+rowspace, '**ADDITIONAL DATA HAS NOT BEEN PRINTED HERE - current limit is 8 files each side.', fontsize=lf, color='k')
               
    # Show the plot
    plt.show()
    # Save plot as PDF
    pdffile.savefig(fig)
    bookmarks.append(('Spatiotemporal', marknum))
    marknum += 1

def plot_FootModel(self):
    global bookmarks
    global marknum
    fig = None
    plotNorm = False
    num_rows = 6
    num_cols=3
    
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in checkboxes if checkboxes[i].get()])
    
    for file in checkboxes:
        # If the variable is set
        if checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0]) # the list 'folderfile_name' needs to have the contents reversed to match order of checkboxes
            # data_dict = get_gcdData(gcd_file, folderfile_name[list(checkboxes).index(gcd_file+'L')][0])
            
            # check to see if kinetics data present, if not, skip file and move to next within 'checkboxes' for-loop
            limbassign = 'Left'
            if file[-1] == 'R':
                limbassign = 'Right'
            
            data_label = f'{limbassign}HindFootTilt'
            if not data_label in data_dict.keys():
                print(f'{limbassign} FOOT KINEMATICS were not found in file {gcd_file}')
                gcd_count += 1 
                # This code will keep counting files so plots will match color schemes throughout the report
                if limbassign == 'Left':
                    LeftPlotNum += 1 
                    PlotNum = LeftPlotNum
                elif limbassign == 'Right':
                    RightPlotNum += 1 
                    PlotNum = RightPlotNum
                continue
            elif data_label in data_dict.keys() and limbassign == 'Left':
                plotloop = [0]
            elif data_label in data_dict.keys() and limbassign == 'Right':
                plotloop = [1]                
            else:
                print(f'Check FOOT KINEMATICS regarding file {gcd_file}, limb-specific message should have been displayed or data plotted')
        
        # ----------------------------- Set pdf page and subplots -------------
            
            if not fig:
                # Create a figure with subplots
                fig, axes1 = plt.subplots(num_rows, num_cols, figsize=(8.5,11))
                # fig.tight_layout(pad=2, w_pad=1.0, h_pad=1.0)
                fig.tight_layout()
                plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
               
                # fig.tight_layout(pad=3.0)  # Adjust spacing between subplots
                fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
                titlenamestr = 'Foot Kinematics \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
                plt.gcf().text(0.5,0.925, titlenamestr, fontsize=12, color='k', horizontalalignment='center')
                
                # Flatten the axes1 array
                axes1 = axes1.flatten()
        # ----------------------------- Get norm data -------------------------
                
                # ONLY GET and PLOT norm data once
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
                plotNorm = True
        # ----------------------------- Plot data -----------------------------
            
            limb_spec = ['Left','Right']
           
            for Lnum in plotloop:
                n = 16 # default number of colormap vectors to use in plotting
                if gcdNum_selected < 16 and varLR.get() == 0:
                    n = round(gcdNum_selected/2)
                elif gcdNum_selected < 8 and varLR.get() != 0:
                    n = gcdNum_selected
               
                if Lnum == 0:
                    try:
                        # below here should work
                        confLeft = [limb_spec[Lnum] + 'HindFootTilt']
                        # cc = np.flipud(plt.cm.winter(np.linspace(0,1,n))) # left blue-->green
                        cc = plt.cm.winter(np.linspace(0,1,n)) # left blue-->green
                        PlotNum = LeftPlotNum
                        LeftPlotNum += 1
                        datLen = len(data_dict[confLeft[0]])
                    except:
                        print(f'LEFT FOOT MODEL data for file {gcd_file} has not been plotted')
                        continue   
                elif Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'HindFootTilt']
                        # cc = np.flipud(plt.cm.autumn(np.linspace(0,1,n))) # right red-->yellow
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print(f'RIGHT FOOT MODEL data for file {gcd_file} has not been plotted')
                        continue
                        
                # changing colormap to gray when total file numbers over 10 (5 per side)
                if gcdNum_selected > 16:
                    cc = plt.cm.gray(np.linspace(0.5,0.5,gcdNum_selected))
                    
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1
                if xts<20:
                    scaleX = 2
                    
                sf = 8
                mf = 10
                lf = 12
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=sf-1)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                
                # ----------------- HindFootTilt ------------------------
                
                data_label = ['HindFootTilt']
                ax = axes1[0]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hindfoot Tilt')
                # ax1.set_xlabel('% Gait Cycle')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                ax.fontsize = sf
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-90)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),90)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- HindFootObliquity -------------------
                data_label = ['HindFootObliquity']
                ax = axes1[1]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Var')
                    lowerstr = ('Val')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Hindfoot Obliquity')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                # ----------------- ForeFootTilt ----------------------------
                data_label = ['ForeFootTilt']
                ax = axes1[2]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Forefoot Tilt')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-180)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),60)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Ankle DorsiPlanFlex -------------------------
                data_label = ['DorsiPlanFlex']
                ax = axes1[3]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Ankle Planti-Dorsiflexion')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- FootProgression ---------------------------
                data_label = ['FootProgression']
                ax = axes1[5]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Foot Progression')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- AnkleComplexDorsiPlanFlex --------------------------
                data_label = ['AnkleComplexDorsiPlanFlex']
                ax = axes1[6]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Ankle Complex Planti-Dorsiflexion')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- AnkleComplexValgVar ---------------------
                data_label = ['AnkleComplexValgVar']
                ax = axes1[7]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Var')
                    lowerstr = ('Val')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Ankle Complex Valgus/Varus')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- AnkleComplexRotation ------------------------------
                data_label = ['AnkleComplexRotation']
                ax = axes1[8]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Int')
                    lowerstr = ('Ext')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Ankle Complex Rotation')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- MidFootDorsiPlanFlex -------------------------
                data_label = ['MidFootDorsiPlanFlex']
                ax = axes1[9]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Midfoot Complex Flex/Extension')
                ax.set_ylabel('range (deg)')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-60)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),15)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                # ----------------- Supination --------------------
                data_label = ['Supination']
                ax = axes1[10]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Sup')
                    lowerstr = ('Pro')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Supination Index')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- MidFootAbAdduct ----------------------------
                data_label = ['MidFootAbAdduct']
                ax = axes1[11]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Add')
                    lowerstr = ('Abd')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Midfoot Ab/Adduction')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- HalDorsiPlanFlex -------------------------
                data_label = ['HalDorsiPlanFlex']
                ax = axes1[12]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Dor')
                    lowerstr = ('Pln')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('1st MTP Flexion/Extension')
                ax.set_ylabel('range (deg)')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),90)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                
                #  ----------------- Skew ---------------
                data_label = ['Skew']
                ax = axes1[13]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('sk+')
                    lowerstr = ('sk-')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                    
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('Skew Index')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-30)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),30)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- HalValgVar ----------------------------
                data_label = ['HalValgVar']
                ax = axes1[14]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                # norm bands, only plot once
                if plotNorm: 
                    lowerN = np.subtract(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    upperN = np.add(np.array(dataNmean_dict[data_label[0]]), np.array(dataNstd_dict[data_label[0]]))
                    ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                    # motion direction text
                    upperstr = ('Var')
                    lowerstr = ('Val')
                    plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[1][1]+0.005, upperstr, fontsize=sf-2, color='k')
                    plt.gcf().text(plotxy[0][0]-0.025, plotxy[0][1]-0.0125, lowerstr, fontsize=sf-2, color='k')
                
                ax.plot(x,data_dict[limb_spec[Lnum] + data_label[0]], color=cc[PlotNum], linewidth=0.75)
                ax.set_title('1st MTP Varus/Valgus')
                ax.set_xlabel('% Gait Cycle')
                ax.set_xlim([0,datLen])
                ax.set_xticks(list(range(0,datLen,xts)), ['0','20','40','60','80','100'])
                # y-limits
                ylower = min(min(data_dict[limb_spec[Lnum] + data_label[0]]),-45)
                yupper = max(max(data_dict[limb_spec[Lnum] + data_label[0]]),45)
                getYl = ax.get_ylim() # ylower is index [0], yupper is index [1]].
                ax.set_ylim([min(ylower,getYl[0]),max(yupper,getYl[1])])
                ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                # ipsi foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot off lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                # contra foot contact lines
                x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                x2 = x1
                ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum],linewidth=0.75)
                
                #  ----------------- figure layout options --------------------
                 
                # -----------------  Adding GCD file names --------------------
                # filename row and column spacing and adjustments
                firstcol = 0.35
                nextcol = 0.635
                rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
                titleRow = 0.1175
                
                # GCD file name to print
                gcdfilestr = (f'{gcd_file}')
                    
                if plotNorm:
                    # --------------- Note on data and VST used for norms -----------------
                    VSTmessage = f"Biomechanical model used is the Shriners Standard Gait Model. VST used is the '{VSTmodelused}' skeletal template"
                    plt.gcf().text(0.935, titleRow, VSTmessage, fontsize=sf-1, rotation=90, color='k')
                    normDataUsed = 'Greenville, Salt Lake, & Spokane'
                    if normFile[0:2] == 'Gr':
                        normDataUsed = 'Greenville'
                    normMessage = f"**Gray bands are mean +/- 1SD range during barefoot walking for typically developing children aged {normFile[7:-4]}- collected by Shriners Children's {normDataUsed}**"
                    plt.gcf().text(0.95, titleRow, normMessage, fontsize=sf-1, rotation=90, color='k')
                   
                    # Patient info
                    plt.gcf().text(0.06, titleRow, 'Name: ' +PatientName, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[0], 'MRN: ' +MRN[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[1], 'Diagnosis: ' +diagnosis, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[2], 'Date: ' +studydate, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[3], 'Condition: ' +condition[0:-1], fontsize=sf)
                    plt.gcf().text(0.06, rowvec[4], 'Visit Type: ' +visit, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[5], 'Brace: ' +brace, fontsize=sf)
                    plt.gcf().text(0.06, rowvec[6], 'Walk Aide: ' +walkaid, fontsize=sf)
                    
                    # filename titles
                    filenamestr = ('File Names')
                    plt.gcf().text(firstcol, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(nextcol, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
                    plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol,0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
                         
                    filenamestr = ('GDI')
                    plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
                    try:
                        GDM = round(dataNmean_dict['GDI'][0],2)
                        GDSD = round(dataNstd_dict['GDI'][0],2)
                        plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(firstcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                        plt.gcf().text(nextcol+0.185, 0.0075, GDSD, fontsize=sf-1, color='k')
                    except:
                        print(f'GDI is not found in {gcd_file}, not printed to kinematics page')
                                   
                    filenamestr = ('Spd')
                    plt.gcf().text(firstcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, titleRow, filenamestr, fontsize=sf-1, color='k')
                    Spp1M = round((dataNmean_dict['Speed'][0]/1000) + (dataNstd_dict['Speed'][0]/1000),2)
                    Spm1M = round((dataNmean_dict['Speed'][0]/1000) - (dataNstd_dict['Speed'][0]/1000),2)
                    plt.gcf().text(firstcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0175, Spp1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.215, 0.0075, Spm1M, fontsize=sf-1, color='k')
                                    
                    filenamestr = ('Cad')
                    plt.gcf().text(firstcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, titleRow, filenamestr, fontsize=sf-1, color='k')
                    cap1M = round(dataNmean_dict['Cadence'][0] + dataNstd_dict['Cadence'][0],2)
                    cam1M = round(dataNmean_dict['Cadence'][0] - dataNstd_dict['Cadence'][0],2)
                    plt.gcf().text(firstcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(firstcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0175, cap1M, fontsize=sf-1, color='k')
                    plt.gcf().text(nextcol+0.245, 0.0075, cam1M, fontsize=sf-1, color='k')
                                    
                # Single Value Data
                #Left
                if Lnum == 0 and LeftPlotNum < 7:
                      
                    LSL = round(data_dict['LeftSpeed'][0]/1000,2)
                    plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LSL, fontsize=sf-1, color='k')
                   
                    Lca = round(data_dict['LeftCadence'][0],2)
                    plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], Lca, fontsize=sf-1, color='k')
                # Right
                elif (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    
                    RSL = round(data_dict['RightSpeed'][0]/1000,2)
                    plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RSL, fontsize=sf-1, color='k')
                    
                    Rca = round(data_dict['RightCadence'][0],2)
                    plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], Rca, fontsize=sf-1, color='k')
                
                # Plot left file names
                if Lnum == 0 and LeftPlotNum < 7:
                    plt.gcf().text(firstcol, rowvec[LeftPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                                
                # Plot right file names
                if (Lnum == 1 and RightPlotNum < 6 and gcdNum_selected >= 12) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 12):
                    plt.gcf().text(nextcol, rowvec[RightPlotNum-1], gcdfilestr[0:18] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                
                if gcdNum_selected >= 12 and gcd_count == 0: 
                    textstr = 'Additional file names not shown'
                    plt.gcf().text(nextcol,0.03, textstr, fontsize=mf, color='k')    
 
                plotNorm = False
                
        if checkboxes[file].get():
            # should align with first for-loop in function
            gcd_count += 1
            
        # Hide empty subplots if there are fewer graphs than subplots but only when a pdf page is created
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)) and 'axes1' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes1[fignum].lines:
                    axes1[fignum].axis('off')
               
    try:
        # Show the plot
        plt.show()
        # Save plot as PDF
        pdffile.savefig(fig)
        bookmarks.append(('Foot Kinematics', marknum))
        marknum += 1
    except:
        print(f'No FOOT KINEMATICS have been plotted for file {gcd_file}. Check Nexus and re-process file if expecting foot kinematics.')

#Calls the main Function
app = Motion_Report()
app.mainloop()
# print(bookmarks)
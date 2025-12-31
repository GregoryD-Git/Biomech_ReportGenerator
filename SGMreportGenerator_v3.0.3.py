#! C:\Users\Vicon-OEM\AppData\Local\Programs\Python\Python311\python.exe
# -*- coding: utf-8 -*-
'''
Created on Mon Sep 11 16:11:41 2023

@author: Dan Gregory
daniel.gregory@shrinenet.org
'''
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
import sys
from PageSettings_SGM import (KinPageSettings as kps,
                        SagittalKinPageSettings as sps,
                        CoronalKinPageSettings as cps,
                        MuscleLengthVelocityPageSettings as mps,
                        FootKinematicsPageSettings as fps,
                        EMGpageSettings as eps
                        )

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

### ----------------------- Initialize selections -----------------------------

# Combobox selections
Dx_select           = ['Gait Abnormality','Cerebral Palsy','Idiopathic Toe Walking',
                       'Club Foot','Sports','Other','Neuro','Ortho']
visit_select        = ['Eval','Pre-Op','Post-Op','RTS','Long-Term','Research',
                       'Quality Assurance']
brace_select        = ["Barefoot","B AFO-PLS","L AFO-PLS","R AFO-PLS",
                        "B AFO-Solid","L AFO-Solid","R AFO-Solid",
                        "B AFO-FR","L AFO-FR","R AFO-FR",
                        "B AFO-Artic","L AFO-Artic","R AFO-Artic",
                        "L LIFT","R LIFT","B SMO","L SMO","R SMO",
                        "B UCBL","L UCBL","R UCBL",
                        "KAFO","HKAFO","RGO","Parawalker","Shoes Only","Other", "Shod"]
walkaid_select      = ['None','Posterior', 'Anterior','Canes','Crutches','Other']
vstused_select      = ['no KAD','no KAD Dypstick','Foot Model no KAD',
                       'Foot Model no KAD w/FootNotFlat','Foot Model Dypstick no KAD',
                       'KAD','KAD Dypstick','Foot Model with KAD',
                       'Foot Model Dypstick with KAD', 'new no KAD & old KAD']

# Initialize values with memory
dia                 = [Dx_select[0]]        # diagnosis entry
vis                 = [visit_select[0]]     # visit type entry
vst                 = [vstused_select[0]]   # vst used entry
fse                 = False                 # indicate whether patient folder has been selected already

# bookmarks and bookmark number
bookmarks           = []
marknum             = 0

### ---------------------- User Interface -------------------------------------
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
    
    # List all files in the directory
    py_patient_directory = selected_folder + '/**/*.py*'
    python_files = []

    # initialize variables
    fne = ['Patient Name']
    pid = ['1234567']
    dte = [date.today().strftime('%m-%d-%Y')]
    brt = [brace_select[0]]
    wat = [walkaid_select[0]]
    age = 1
    
    # collect files and creation times
    try:
        for file in glob.glob(py_patient_directory, recursive=True):
            pyfilename = os.path.basename(file)
    
            if pyfilename.endswith('.py') and pyfilename.startswith('Static'):
                py_filename = file.replace('/','\\')
                creation_time = os.path.getctime(file)
                python_files.append((py_filename, creation_time))
        
        
        # sort by creation time - most recent first
        python_files.sort(key=lambda x: x[1], reverse=True)
        
        sorted_python_files = [file[0] for file in python_files]
        
        # If a Python file is found, open and read it
        if sorted_python_files:
            try:
                # for StaticDataFileName in sorted_python_files:
                # pull first - most recent - static filename
                StaticDataFileName = sorted_python_files[0]
                print(f'Patient data pulled from {os.path.basename(StaticDataFileName)} static file')
                
                # open python file
                exec(open(StaticDataFileName).read())
                
                # try to extract variables that should exist in the file
                ################## patient name and id
                first_name = self.valueFirstName
                last_name = self.valueLastName
                pid = [self.valuePatientNumber]
                fne = [first_name + " " + last_name]
                
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
                # return pid, fne, brt, dte, wat, age
            except:
                # fne = ['Patient Name']
                # pid = ['1234567']
                # dte = [date.today().strftime('%m-%d-%Y')]
                # brt = [brace_select[0]]
                # wat = [walkaid_select[0]]
                # age = 1
                print('Static python file not found or could not be accessed. Defualt values used for patient information')
                # return pid, fne, brt, dte, wat, age
    except:
        # fne = ['Patient Name']
        # pid = ['1234567']
        # dte = [date.today().strftime('%m-%d-%Y')]
        # brt = [brace_select[0]]
        # wat = [walkaid_select[0]]
        # age = 1
        print('Static python file not found or could not be accessed. Defualt values used for patient information')
    return pid, fne, brt, dte, wat, age

class PatientStudyInfo_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid()
    
        # Open top level folder for patient
        self.selected_folder = filedialog.askdirectory(initialdir=main_directory, title="Select a Folder")
        if self.selected_folder == "":
            tk.messagebox.showerror('Exiting Program ', ' No folder was selected! \n Window will close with no data to save')
            tk.Frame.destroy(self)
            sys.exit()
          
        global patient_directory
        patient_directory = f'{self.selected_folder}/**/*.gcd*'
        
        # Get patient info from python file in folder
        [pid, fne, brt, dte, wat, age] = get_PatientInfo_fromPyfile(self.selected_folder, self)
    
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
        
        # grab focus of the top level window so that typing can be done automatically
        self.focus_force()
        
        # Patient Information
        patient_info_frame = tk.LabelFrame(self, text='Patient Information')
        patient_info_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5) # in row 1 column 1 in frame 1

        firstlastname_label = tk.Label(patient_info_frame, text='First and Last Name')
        firstlastname_label.grid(row=0, column=0, padx=5, pady=5) # in row 1 column 1 in label frame 1
        firstlastname_entry = tk.Entry(patient_info_frame, state='normal')
        firstlastname_entry.grid(row=1, column=0, padx=5, pady=5)
        firstlastname_entry.insert(0, fne[0])

        MRN_label = tk.Label(patient_info_frame, text='Medical Record Number')
        MRN_label.grid(row=0, column=1, padx=5, pady=5)
        MRN_entry = tk.Entry(patient_info_frame, state='normal')
        MRN_entry.grid(row=1,column=1, padx=5, pady=5)
        MRN_entry.insert(0, pid[0])
        
        Dx_type = tk.Label(patient_info_frame, text='Diagnosis')
        Dx_type.grid(row=0, column=2, padx=5, pady=5)
        Dx_type_combobox = ttk.Combobox(patient_info_frame, values=dia[0], state='normal')
        Dx_type_combobox['values'] = Dx_select
        Dx_type_combobox.grid(row=1, column=2, padx=5, pady=5)
        dxIDX = Dx_select.index(dia[0])
        Dx_type_combobox.current(dxIDX)
        
        date_label = tk.Label(patient_info_frame, text='Date of Study')
        date_label.grid(row=0, column=3, padx=5, pady=5)
        date_entry = tk.Entry(patient_info_frame, state='normal')
        date_entry.grid(row=1, column=3, padx=5, pady=5)
        date_entry.insert(0,dte[0])

        # pack and scale size of widgets after information has been printed to frames
        for nchild in range(0,4):
            patient_info_frame.grid_rowconfigure(nchild, weight=1)
            patient_info_frame.grid_columnconfigure(nchild, weight=1)        

        # Visit information
        visit_info_frame = tk.LabelFrame(self, text='Visit Information')
        visit_info_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)

        visit_type = tk.Label(visit_info_frame, text='Visit Type')
        visit_type.grid(row=0, column=0, padx=5, pady=5)
        visit_type_combobox = ttk.Combobox(visit_info_frame, values=vis[0], state='normal')
        visit_type_combobox['values'] = visit_select
        visit_type_combobox.grid(row=1, column=0, padx=5, pady=5)
        visIDX = visit_select.index(vis[0])
        visit_type_combobox.current(visIDX)

        condition_type = tk.Label(visit_info_frame, text='Condition')
        condition_type.grid(row=0, column=1, padx=5, pady=5)
        condition_type_combobox = ttk.Combobox(visit_info_frame, values= ['Barefoot','Braced','Foot Model','Best Walk','Walker','Shoes','Lift','Comparison','Other'], state='normal')
        condition_type_combobox.grid(row=1, column=1, padx=5, pady=5)
        condition_type_combobox.current(0)

        brace_type = tk.Label(visit_info_frame, text='Brace Type')
        brace_type.grid(row=0, column=2, padx=5, pady=5)
        brace_type_combobox = ttk.Combobox(visit_info_frame, values=brt[0], state='normal')
        brace_type_combobox['values'] = brace_select
        brace_type_combobox.grid(row=1, column=2, padx=5, pady=5)
        brtIDX = brace_select.index(brt[0])
        brace_type_combobox.current(brtIDX)

        walkaid_type = tk.Label(visit_info_frame, text='Walk Aid Type')
        walkaid_type.grid(row=0, column=3, padx=5, pady=5)
        walkaid_type_combobox = ttk.Combobox(visit_info_frame, values=wat[0], state='normal')
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
        reportplot_info_frame.grid(row=2, sticky='nsew', column=0, padx=10, pady=5)

        report_type = tk.Label(reportplot_info_frame, text='Report Type')
        report_type.grid(row=0, column=0, padx=5, pady=5)
        report_type_combobox = ttk.Combobox(reportplot_info_frame, values=['Quick Check','Consistency Both','Consistency Left','Consistency Right','Working','BF-AFO Comparison','Pre-Post Comparison','Normal vs. Best Walk','Quality Assurance','Other'], state='normal')
        report_type_combobox.grid(row=1, column=0, padx=5, pady=5)
        report_type_combobox.current(0)  
        
        VSTused_type = tk.Label(reportplot_info_frame, text='Select VST Used')
        VSTused_type.grid(row=0, column=1, padx=5, pady=5)
        VSTused_type_combobox = ttk.Combobox(reportplot_info_frame, values=vst[0], state='normal')
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
        save_button.grid(row=1, column=3, sticky='nsew')

        exit_button = tk.Button(reportplot_info_frame, text="Close Window Without Saving", command=lambda: [self.parent.destroy()])        
        exit_button.grid(row=2, column=3, sticky='nsew')

        # pack and scale size of widgets after information has been printed to frames
        for nchild in range(0,9):
            reportplot_info_frame.grid_rowconfigure(nchild, weight=1)
            reportplot_info_frame.grid_columnconfigure(nchild, weight=1)  
            
class SelectData_Page(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.grid()
         
    def build_PlotReportUI(self):
        # Navigation frame
        navigation_frame = tk.LabelFrame(self, text='Navigation')
        navigation_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        back_button = tk.Button(navigation_frame, text="Back", command = lambda: [self.parent.frames[PatientStudyInfo_Page].tkraise(), self.parent.frames[PatientStudyInfo_Page].build_PatientInfoUI(), clear_bookmarks()])
        back_button.grid(row=0, column=0, sticky='nsew', padx=3, pady=5)
        
        save_button = tk.Button(navigation_frame, text="Save PDF", command = lambda: [close_pdf(self)])
        save_button.grid(row=0, column=1, sticky='nsew', padx=3, pady=5)
        
        ghost_label = tk.Label(navigation_frame,text="                                                                                                                  ")        
        ghost_label.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=3, pady=5)
        
        exit_button = tk.Button(navigation_frame,text="Close Window", command=lambda: [self.parent.destroy()])        
        exit_button.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=3, pady=5)
        
        # Plot frame
        plot_frame = tk.LabelFrame(self, text='Plot Options for Selected Files')
        plot_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        button_plotKMT = tk.Button(plot_frame, text="Kinematics", command=lambda: [plot_kinematics(self), plot_FootModel(self)])
        button_plotKMT.grid(row=0, column=0, sticky='nsew', padx=3, pady=3)
        button_plotSaK = tk.Button(plot_frame, text="Kinetics", command=lambda: [plot_sagittalKinetics(self), plot_coronalKinetics(self)])
        button_plotSaK.grid(row=0, column=1, sticky='nsew', padx=3, pady=3)
        button_plotEMG = tk.Button(plot_frame, text="EMG", command=lambda: [plot_EMG(self)])
        button_plotEMG.grid(row=0, column=2, sticky='nsew', padx=3, pady=3)
        button_plotKKB= tk.Button(plot_frame, text="Kinematics\n& Kinetics", command=lambda: [plot_kinematics(self), plot_sagittalKinetics(self), plot_coronalKinetics(self), plot_FootModel(self)])
        button_plotKKB.grid(row=1, column=0, sticky='nsew', padx=3, pady=3)
        button_plotBas = tk.Button(plot_frame, text="Basic Report\n(no EMG)", command=lambda: [plot_kinematics(self), plot_sagittalKinetics(self), plot_coronalKinetics(self), plot_MuscleLengthVel(self), plot_SpatioTemporal(self), plot_FootModel(self)])
        button_plotBas.grid(row=1, column=1, sticky='nsew', padx=3, pady=3)
        button_plotALL = tk.Button(plot_frame, text="Full Report\n(with EMG)", command=lambda: [plot_kinematics(self), plot_sagittalKinetics(self), plot_coronalKinetics(self), plot_MuscleLengthVel(self), plot_EMG(self), plot_SpatioTemporal(self), plot_FootModel(self)])
        button_plotALL.grid(row=1, column=2, sticky='nsew', padx=3, pady=3)
        
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
        
        rowidx = 1
        # global checkboxes
        self.checkboxes = {}
        
        # reverse order of patient folders so most recent comes first
        ordered_patient_folders = selected_patient_folders[::-1]
        
        for curr_session in ordered_patient_folders:
            selectLeft_file_frame = tk.LabelFrame(self, text=f'Select Left {curr_session} files')
            selectLeft_file_frame.grid(row=rowidx, column=0, sticky='nsew', padx=5, pady=5)
           
            selectRight_file_frame = tk.LabelFrame(self, text=f'Select Right {curr_session} files')
            selectRight_file_frame.grid(row=rowidx, column=1, sticky='nsew', padx=5, pady=5)
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
                    self.checkboxes.update({gcdfile+'L': Lvar, gcdfile+'R': Rvar})
                
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

### ------------------ Data Retrieval -----------------------------------------
def get_gcdData(gcd_file, folderfile_name):
    # ----------------------------- Get data ------------------------------
        f = open(folderfile_name +'\\' +gcd_file, 'r+')
        data = f.readlines()
    # ---------------------------- Get headers ----------------------------
        # find index of data headers that start with "!"
        headerIndex = [i for i, e in enumerate(data) if e[0] == "!"]
       
    # ----------------------------- Convert data --------------------------
        data_dict ={}
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
    if age > 2 and age < 8:
        normFile = norm4_7
        EMGnormFile = norm4_7
    elif age > 7 and age < 13:
        normFile = norm8_12
        EMGnormFile = norm8_12
    elif age > 12 and age < 22:
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
    
    try:
        save_path = patient_directory.split("/")
        filename = f'{condition +MRN +report +studydate}.pdf'
        filenamepath =  os.path.join('/'.join(save_path[0:4]), filename)
        pdffile = PdfPages(filenamepath)
    except: 
        tk.messagebox.showerror('Python Error', 'ERROR: \n\nIt appears that the filename you are trying to use already exists and is open in another program. \n\nClose the file and retry, or change patient info to continue.')
        quit()
    
def close_pdf(self):
    try:
        # this will close the already completed pdf file that does not have the bookmarks
        pdffile.close()
        
        # write headers to pdf file
        save_path = patient_directory.split("/")
        filename = f'{condition +MRN +report +studydate}.pdf'
        output_path = os.path.join('/'.join(save_path[0:4]), filename)
        
        # this will open the pdf file and read that pages and add bookmarks from the bookmarks list
        pdf_reader = PyPDF2.PdfReader(output_path)
        pdf_writer = PyPDF2.PdfWriter()
        for numpage in range(0,len(bookmarks)):
            page = pdf_reader.pages[numpage]
            pdf_writer.add_page(page)
            pdf_writer.add_outline_item(bookmarks[numpage][0], bookmarks[numpage][1])
            
        with open (output_path, 'wb') as output_file:
            pdf_writer.write(output_file)
        
        output_file.close()
        tk.messagebox.showinfo("PDF file has been saved", "Go back and pick files for a new report or close the window.")
       
        # Text file export
        if not MRN == '1234567':
            try:
                # get the current date
                date_today = date.today().strftime('%m-%d-%Y')
                
                # specify file path where saved file will go
                # save_path = patient_directory.split("/")
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
                    
                    for file in self.checkboxes:
                        # If the variable is set
                        if self.checkboxes[file].get():
                            f.write(str(f'{file}' + '\n'))
                    
                    f.write(f'END OF REPORT LOG FOR: {date_today} \n\n\n')
            except: 
                tk.messagebox.showerror('Python Error', 'ERROR: \n\nIt appears that the text filename you are trying to use already exists and is open in another program. \n\nClose the file and retry, or change patient info to continue.')
    except:
        print('Window closed, no data to save')
   
### ------------------ Plotting functions -------------------------------------
def plot_Data(self, plot_type, page_settings, is_EMG):
    global bookmarks
    global marknum
    fig = None # sets the fig for figures to None
    
    # xsmall, small, medium, and large font sizes
    xf = 7
    sf = 8
    mf = 10
    lf = 12
    
    # tracking L/R plot numbers, overall plut number, and gcd count
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    
    # count number of gcd files selected in checkboxes
    gcdNum_selected = len([i for i in self.checkboxes if self.checkboxes[i].get()])
    # print(f'number of gcds selected is: {gcdNum_selected}')
    
    for file in self.checkboxes:
        # get set variables from checkboxes
        if self.checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(self.checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0])
            
        # ----------------------------- Set up limb and loop refs -------------
            limb_spec = ['Left','Right']
            plotLimb = file[-1]
            
        # ----------------------------- Check for appropriate data ------------
        # kinetics and foot model data will not plot if data is not present in gcd file
            if plotLimb == 'L':
                plotloop = [0]
                # check for kinetics
                if plot_type in ['Sagittal Kinetics', 'Coronal Kinetics']:
                    data_label = f'{limb_spec[0]}HipFlexExtMoment'
                    if not data_label in data_dict.keys():
                        print(f'{limb_spec[0]} KINETICS were not found in file {gcd_file}')
                        # need to count gcd and left plot number anyway
                        gcd_count += 1 
                        LeftPlotNum += 1 
                        PlotNum = LeftPlotNum
                        continue
                    
                # check for foot kinematics
                if plot_type == 'Barefoot (Foot Model)':
                    data_label = f'{limb_spec[0]}HindFootTilt'
                    if not data_label in data_dict.keys():
                        print(f'{limb_spec[0]} FOOT KINEMATICS were not found in file {gcd_file}')
                        # need to count gcd and left plot number anyway
                        gcd_count += 1 
                        LeftPlotNum += 1 
                        PlotNum = LeftPlotNum
                        continue
                
            elif plotLimb == 'R':
                plotloop = [1]
                # check for kinetics
                if plot_type in ['Sagittal Kinetics', 'Coronal Kinetics']:
                    data_label = f'{limb_spec[1]}HipFlexExtMoment'
                    if not data_label in data_dict.keys():
                        print(f'{limb_spec[1]} KINETICS were not found in file {gcd_file}')
                        # need to count gcd and left plot number anyway
                        gcd_count += 1 
                        RightPlotNum += 1 
                        PlotNum = RightPlotNum
                        continue
                    
                # check for foot kinematics
                if plot_type == 'Barefoot (Foot Model)':
                    data_label = f'{limb_spec[1]}HindFootTilt'
                    if not data_label in data_dict.keys():
                        print(f'{limb_spec[1]} FOOT KINEMATICS were not found in file {gcd_file}')
                        # need to count gcd and left plot number anyway
                        gcd_count += 1 
                        RightPlotNum += 1 
                        PlotNum = RightPlotNum
                        continue
              
        # ----------------------------- Set plot page -------------------------
            if not fig:
                plt.rcParams.update({
                    'font.size': sf,
                    'axes.titlesize': 15,
                    'figure.titlesize': 15
                })
                
                # setting up the plot page
                fig, axes = plt.subplots(6, 3, figsize=(8.5,11))
                fig.tight_layout()
                plt.subplots_adjust(left=0.12, right=0.9, top=0.9, bottom=0.01)
                
                fig.suptitle(f"Shriners Children's - {site_name}, Motion Analysis Center", fontsize=15)
                titlenamestr = f'{plot_type} \n' +condition[0:-1] +' ' +report[0:-1] +' Plots'
                plt.gcf().text(0.5,0.925, titlenamestr, fontsize=sf, color='k', horizontalalignment='center')
        
                # Flatten the axes1 array
                axes = axes.flatten()
        
        # ----------------------------- Get norm data -------------------------
            # ONLY GET and PLOT norm data once 
            if gcd_count == 0:
                isEMG = False
                dataNmean_dict, dataNstd_dict, normFile = get_normData(normfolderfile_name, isEMG, self)
        
        # ----------------------------- Plot data -----------------------------
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
                        print('LEFT Limb data for file {[gcd_file]} has not been plotted')
                        continue   
                if Lnum == 1:
                    try:
                        confRight = [limb_spec[Lnum] + 'PelvicObliquity']
                        cc = plt.cm.autumn(np.linspace(0,1,n)) # right red-->yellow
                        PlotNum = RightPlotNum
                        RightPlotNum += 1
                        datLen = len(data_dict[confRight[0]])
                    except:
                        print('RIGHT Limb data for file {gcd_file} has not been plotted')
                        continue
                        
                # setting plotting parameters
                x = list(range(0,datLen))
                xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
                scaleX = 1.0
                if xts<20:
                    scaleX = 2
                
                plt.rc('font', size=sf)          # controls default text sizes
                plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
                plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
                plt.rc('xtick', labelsize=xf)    # fontsize of the tick labels
                plt.rc('ytick', labelsize=xf)    # fontsize of the tick labels
                plt.rc('legend', fontsize=mf)    # legend fontsize
                plt.rc('figure', titlesize=lf)   # fontsize of the figure title
                
                # ----------------- Call labels and add ------------------------
                
                # Get all attributes that are lists of strings
                page_settings_lists = vars(page_settings)
                
                for key in page_settings_lists.keys():
                    if 'Left' in key and 'Names' in key and Lnum == 0:
                        curve_names = page_settings_lists[key]
                    elif 'Right' in key and 'Names' in key and Lnum == 1:
                        curve_names = page_settings_lists[key]
                    elif 'Titles' in key:
                        titles = page_settings_lists[key]
                    elif 'UnitLabels' in key:
                        unit_labels = page_settings_lists[key]
                    elif 'LowerLimit' in key:
                        lower_limits = page_settings_lists[key]
                    elif 'UpperLimit' in key:
                        upper_limits = page_settings_lists[key]
                    elif 'YLabels' in key:
                        y_Labels = page_settings_lists[key]
                
                # Loop through trajectory names (i.e. subplots)
                for idx, label in enumerate(curve_names):
                    if label == '':
                        continue
                    else:
                        data_label = label.removeprefix('Left').removeprefix('Right')
                        ax = axes[idx]
                        ax.set_facecolor(FaceCol)
                        ax.patch.set_alpha(FaceColAlpha)
                        
                        # set subplot parameters
                        ax.set_title(titles[idx])
                        
                        # set y-labels for left column only
                        if idx % 3 == 0:
                            ax.set_ylabel(unit_labels[int(idx/3)])
                            
                        # set x-axis limits
                        ax.set_xlim([0,datLen])
                        
                        # set x-ticks, blank unless bottom row
                        if idx < 12:
                            ax.set_xticks(list(range(0,datLen,xts)), ['','','','','',''])
                        else:
                            ax.set_xticks(list(range(0,datLen,xts)))
                            ax.set_xlabel('% Gait Cycle')
                            
                        ax.fontsize = sf
                        
                        # y-limits
                        ylower = lower_limits[idx]
                        yupper = upper_limits[idx]
                        ax.set_ylim([ylower, yupper])
                        
                        # norm bands and y-label positions - only plot once
                        if gcd_count == 0: 
                            lowerN = np.subtract(np.array(dataNmean_dict[data_label]), np.array(dataNstd_dict[data_label]))
                            upperN = np.add(np.array(dataNmean_dict[data_label]), np.array(dataNstd_dict[data_label]))
                            ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                            
                            # motion direction text
                            upperstr = (y_Labels[idx].split('-')[0])
                            lowerstr = (y_Labels[idx].split('-')[1])
                            plotxy = ax.get_position().get_points() # The default constructor takes the boundary "points" [[xmin, ymin], [xmax, ymax]].
                            ytickpos = ax.get_yticks()
                            
                            # Convert y-data to display coordinates (pixels)
                            top_two = sorted(ytickpos)[-2:]  # Get top two tick values
                            y_display_1 = ax.transData.transform((0, top_two[0]))[1]
                            y_display_2 = ax.transData.transform((0, top_two[1]))[1]
                    
                            # Convert display coordinates to figure coordinates (0–1)
                            y_fig_1 = fig.transFigure.inverted().transform((0, y_display_1))[1]
                            y_fig_2 = fig.transFigure.inverted().transform((0, y_display_2))[1]
                    
                            # Midpoint in figure coordinates
                            y_top = (y_fig_1 + y_fig_2) / 2
                            
                            bot_two = sorted(ytickpos)[0:2]  # Get top two tick values
                            y_display_3 = ax.transData.transform((0, bot_two[0]))[1]
                            y_display_4 = ax.transData.transform((0, bot_two[1]))[1]
                    
                            # Convert display coordinates to figure coordinates (0–1)
                            y_fig_3 = fig.transFigure.inverted().transform((0, y_display_3))[1]
                            y_fig_4 = fig.transFigure.inverted().transform((0, y_display_4))[1]
                    
                            # Midpoint in figure coordinates
                            y_bot = (y_fig_3 + y_fig_4) / 2
                            
                            # Add text to subplot
                            plt.gcf().text(plotxy[0][0]-0.03, y_top - 0.001, upperstr, fontsize=sf-2, color='k')
                            plt.gcf().text(plotxy[0][0]-0.03, y_bot - 0.001, lowerstr, fontsize=sf-2, color='k')
                            
                        # find knee varus valgus range and flag if 10 degrees or greater
                        if gcdNum_selected <= 2 and 'Kinematics' in plot_type:
                            if 'KneeFlexExt' in data_label:
                                knee_curve = data_dict[limb_spec[Lnum] + data_label]
                                kf_max = knee_curve.index(max(knee_curve))
                                # get minimum, but must occur after max
                                kf_min = knee_curve.index(min(knee_curve[kf_max:]))
                                # print(f'kf max: {kf_max}; kf min: {kf_min}')
                            elif 'KneeValgVar' in data_label:
                                valg_curve = data_dict[limb_spec[Lnum] + data_label]
                                valg_min = round(min(valg_curve[kf_max:kf_min+1]), 2)
                                valg_max = round(max(valg_curve[kf_max:kf_min+1]), 2)
                                valg_range = round(valg_max - valg_min, 2)
                                text_color = 'k'
                                correlation = round(np.corrcoef(knee_curve, valg_curve)[0, 1],2)
                                
                                # print(f'valg range is: {valg_range}')
                                x_pos = 45 # as % gait cycle
                                if Lnum == 0: # left
                                    y_pos = 22
                                    l_string = f'L range: {valg_range} ({correlation})'
                                    if valg_range >= 10:
                                        text_color = 'r'
                                        ax.text(x_pos, y_pos, l_string, fontsize=sf-2, color=text_color,
                                                       bbox=dict(facecolor='yellow', edgecolor='red', boxstyle='round,pad=0.5'),
                                                       ha='left')
                                    else:
                                        ax.text(x_pos, y_pos, l_string, fontsize=sf-2, color=text_color)
                                        
                                    # add min/max horizontal lines
                                    ax.plot([0, 5], [valg_max, valg_max], color='b', linestyle='-', linewidth=0.75)
                                    ax.plot([0, 5], [valg_min, valg_min], color='b', linestyle='-', linewidth=0.75)
                                else:
                                    y_pos = 14
                                    r_string = f'R range: {valg_range} ({correlation})'
                                    if valg_range >= 10:
                                        text_color = 'r'
                                        ax.text(x_pos, y_pos, r_string, fontsize=sf-2, color=text_color,
                                                       bbox=dict(facecolor='yellow', edgecolor='red', boxstyle='round,pad=0.5'),
                                                       ha='left')
                                    else:
                                        ax.text(x_pos, y_pos, r_string, fontsize=sf-2, color=text_color)
                                    
                                    # add min/max horizontal lines
                                    ax.plot([0, 5], [valg_max, valg_max], color='r', linestyle='-', linewidth=0.75)
                                    ax.plot([0, 5], [valg_min, valg_min], color='r', linestyle='-', linewidth=0.75)
                                                    
                        # plot data
                        ax.plot(x,data_dict[limb_spec[Lnum] + data_label], color=cc[PlotNum], linewidth=0.75)
                        
                        # plot timing lines
                        ax.hlines(0, xmin = 0, xmax = datLen, ls='--', color='k', linewidth=0.5)
                        
                        # ipsi foot off lines
                        x1 = data_dict[limb_spec[Lnum] + 'FootOff'][0]/scaleX
                        x2 = x1
                        ax.plot((x1,x2),(ylower,yupper), color=cc[PlotNum], linewidth=0.75)
                        
                        # contra foot off lines
                        x1 = data_dict[limb_spec[Lnum] + 'OppositeFootOff'][0]/scaleX
                        x2 = x1
                        ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum], linewidth=0.75)
                        
                        # contra foot contact lines
                        x1 = data_dict[limb_spec[Lnum] + 'OppositeFootContact'][0]/scaleX
                        x2 = x1
                        ax.plot((x1,x2),(yupper - (yupper - ylower)*0.1,yupper), color=cc[PlotNum], linewidth=0.75)
                    
                # -----------------  Adding patient info & file names ---------
                # call page text function
                plot_pack = {}
                plot_pack['gcd_file']           = gcd_file
                plot_pack['gcd_count']          = gcd_count
                plot_pack['dataNmean_dict']     = dataNmean_dict
                plot_pack['dataNstd_dict']      = dataNstd_dict
                plot_pack['Lnum']               = Lnum
                plot_pack['LeftPlotNum']        = LeftPlotNum
                plot_pack['RightPlotNum']       = RightPlotNum 
                plot_pack['data_dict']          = data_dict
                plot_pack['gcdNum_selected']    = gcdNum_selected
                plot_pack['PlotNum']            = PlotNum
                plot_pack['cc']                 = cc
                
                # call function
                plot_PatientTrialText(self, fig, plot_pack, is_EMG)
                
        if self.checkboxes[file].get():
            gcd_count += 1
            
        # Hide empty subplots if there are fewer graphs than subplots
        if varLR.get() == 0 and gcd_count > 0 and gcd_count%2 == 0 and 'axes' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes[fignum].lines:
                    axes[fignum].axis('off')
        elif (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)) and 'axes' in locals():
            for fignum in range(0,len(fig.get_axes())):
                if not axes[fignum].lines:
                    axes[fignum].axis('off')

    try:
        # Show the plot
        plt.show()
        
        # Save plot as PDF
        pdffile.savefig(fig)
        bookmarks.append((plot_type, marknum))
        marknum += 1
    except:
        print(f'No {plot_type} data have been plotted for file {gcd_file}. Check file to ensure data is present if expected.')

def plot_PatientTrialText(self, fig, plot_pack, is_EMG):
    # small, medium, and large font sizes
    sf = 8
    mf = 10
    
    # bottom of page text settings
    # filename row and column spacing and adjustments
    firstcol = 0.35
    nextcol = 0.635
    rowvec = list([0.105,0.09,0.075,0.06,0.045,0.03, 0.015, 0.0]) # 8 rows
    titleRow = 0.1175
    
    # GCD file name to print
    gcd_file        = plot_pack['gcd_file']
    gcdfilestr      = (f'{gcd_file}')
    gcd_count       = plot_pack['gcd_count']
    dataNmean_dict  = plot_pack['dataNmean_dict']
    dataNstd_dict   = plot_pack['dataNstd_dict']
    cc              = plot_pack['cc']
    
    # only add this info once
    if gcd_count == 0 or is_EMG:
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
        
        # visit, date, and file info
        filenamestr = ('Date')
        plt.gcf().text(firstcol-0.065, titleRow, filenamestr, fontsize=mf, color='k')
        
        filenamestr = ('File Name')
        plt.gcf().text(firstcol+0.03, titleRow, 'Left '+filenamestr, fontsize=mf, color='k')
        plt.gcf().text(nextcol+0.03, titleRow, 'Right '+filenamestr, fontsize=mf, color='k')
        
        # TD data
        plt.gcf().text(firstcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
        plt.gcf().text(nextcol, 0.0175, 'Typically Developing +1SD', fontsize=sf-1, color='k')
        plt.gcf().text(firstcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
        plt.gcf().text(nextcol, 0.0075, 'Typically Developing -1SD', fontsize=sf-1, color='k')
             
        filenamestr = ('GDI')
        plt.gcf().text(firstcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
        plt.gcf().text(nextcol+0.185, titleRow, filenamestr, fontsize=sf-1, color='k')
        
        GDM = 100
        plt.gcf().text(firstcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
        plt.gcf().text(nextcol+0.185, 0.0175, GDM, fontsize=sf-1, color='k')
                  
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
    # unpack data
    Lnum            = plot_pack['Lnum']
    LeftPlotNum     = plot_pack['LeftPlotNum']
    RightPlotNum    = plot_pack['RightPlotNum']
    data_dict       = plot_pack['data_dict']
    gcdNum_selected = plot_pack['gcdNum_selected']
    PlotNum         = plot_pack['PlotNum']
    
    #Left
    if Lnum == 0 and LeftPlotNum < 7:
        try:
            LGD = round(data_dict['LeftGDI'][0],2)
            plt.gcf().text(firstcol+0.185, rowvec[LeftPlotNum-1], LGD, fontsize=sf-1, color='k')
        except:
            print(f'No left GDI found in GCD file {gcd_file}')
        
        LSL = round(data_dict['LeftSpeed'][0]/1000,2)
        plt.gcf().text(firstcol+0.215, rowvec[LeftPlotNum-1], LSL, fontsize=sf-1, color='k')
       
        Lca = round(data_dict['LeftCadence'][0],2)
        plt.gcf().text(firstcol+0.245, rowvec[LeftPlotNum-1], Lca, fontsize=sf-1, color='k')
        
    # Right
    elif (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected >= 14) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 14):
        try:
            RGD = round(data_dict['RightGDI'][0],2)
            plt.gcf().text(nextcol+0.185, rowvec[RightPlotNum-1], RGD, fontsize=sf-1, color='k')
        except:
            print(f'No right GDI found in GCD file {gcd_file}')
        
        RSL = round(data_dict['RightSpeed'][0]/1000,2)
        plt.gcf().text(nextcol+0.215, rowvec[RightPlotNum-1], RSL, fontsize=sf-1, color='k')
        
        Rca = round(data_dict['RightCadence'][0],2)
        plt.gcf().text(nextcol+0.245, rowvec[RightPlotNum-1], Rca, fontsize=sf-1, color='k')
    
        
    # Plot visit info and left file names
    if Lnum == 0 and LeftPlotNum < 7:
        # Add date from static python file - ONLY ON LEFT
        plt.gcf().text(firstcol-0.08, rowvec[LeftPlotNum-1], dte[0], fontsize=sf, color=cc[PlotNum])
        # Add filename making sure to end with trial number
        plt.gcf().text(firstcol+0.03, rowvec[LeftPlotNum-1], gcdfilestr[0:15] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
                    
    # Plot right file names
    if (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected >= 14) or (Lnum == 1 and RightPlotNum < 7 and gcdNum_selected < 14):
        # ADd filename
        plt.gcf().text(nextcol+0.03, rowvec[RightPlotNum-1], gcdfilestr[0:15] +'...' +gcdfilestr[-6:-4], fontsize=sf, color=cc[PlotNum])
    
    if gcdNum_selected >= 14 and gcd_count == 0: 
        textstr = 'Additional file names not shown'
        print(textstr)
        
def plot_kinematics(self):
    page_settings   = kps()
    plot_type       = 'Kinematics'
    is_EMG          = False
   
    plot_Data(self, plot_type, page_settings, is_EMG)
    
def plot_sagittalKinetics(self):
    page_settings   = sps()
    plot_type       = 'Sagittal Kinetics'
    is_EMG          = False
    
    plot_Data(self, plot_type, page_settings, is_EMG)
    
def plot_coronalKinetics(self):
    page_settings   = cps()
    plot_type       = 'Coronal Kinetics'
    is_EMG          = False
   
    plot_Data(self, plot_type, page_settings, is_EMG)
    
def plot_MuscleLengthVel(self):
    page_settings   = mps()
    plot_type       = 'Muscle Length Velocity'
    is_EMG          = False
   
    plot_Data(self, plot_type, page_settings, is_EMG)

def plot_FootModel(self):
    page_settings   = fps()
    plot_type       = 'Barefoot (Foot Model)'
    is_EMG          = False
    
    plot_Data(self, plot_type, page_settings, is_EMG)

def plot_EMG(self):   
    page_settings   = eps()
    global bookmarks
    global marknum
    PlotNum = 0    # used to specify index into colormap from L/R file number
    LeftPlotNum = 0   # used to track left limb files to specify index into blue colormap 
    RightPlotNum = 0   # used to track right limb files to specify index into red colormap
    gcd_count = 0 # used to track total number of gcd files plotted
    gcdNum_selected = len([i for i in self.checkboxes if self.checkboxes[i].get()])
    
    # plotting column index
    colIDX = 0
    
    for file in self.checkboxes:
        
        # If the variable is set
        if self.checkboxes[file].get():
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
            ffnIDX = int(list(self.checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0])
            
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
                    print(f'Data length left: {datLen}')
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
                    print(f'Dat length right: {datLen}')
                except:
                    print('RIGHT EMG data for file {gcd_file} has not been plotted')
                    continue
                     
            # setting plotting parameters
            x = list(range(0,datLen))
            # xts = int(round(datLen,-1)/5) # xtick axis spacing - rounds to 20 with 101 data points or 10 with 51 data points so x-ticks have 6 values from 0:100 or 0:50
            xf = 7
            sf = 8
            mf = 10
            lf = 12
            
            plt.rc('font', size=sf)          # controls default text sizes
            plt.rc('axes', titlesize=sf)     # fontsize of the axes1 title
            plt.rc('axes', labelsize=sf)     # fontsize of the x and y labels
            plt.rc('xtick', labelsize=xf)    # fontsize of the tick labels
            plt.rc('ytick', labelsize=xf)    # fontsize of the tick labels
            plt.rc('legend', fontsize=mf)    # legend fontsize
            plt.rc('figure', titlesize=lf)   # fontsize of the figure title
            
            # ----------------- emg plots ----------------------------
            # Get all attributes that are lists of strings
            page_settings_lists = vars(page_settings)
            
            for key in page_settings_lists.keys():
                if 'Left' in key and 'Names' in key and Lnum == 0:
                    curve_names = page_settings_lists[key]
                elif 'Right' in key and 'Names' in key and Lnum == 1:
                    curve_names = page_settings_lists[key]
                elif 'Envelope' in key:
                    envelope_names = page_settings_lists[key]
                elif 'Titles' in key:
                    titles = page_settings_lists[key]
                elif 'UnitLabels' in key:
                    unit_labels = page_settings_lists[key]
                elif 'LowerLimit' in key:
                    lower_limits = page_settings_lists[key]
                elif 'UpperLimit' in key:
                    upper_limits = page_settings_lists[key]
                elif 'YLabels' in key:
                    y_Labels = page_settings_lists[key]
            
            axIDX = [[0,1,2],
                     [3,4,5],
                     [6,7,8],
                     [9,10,11],
                     [12,13,14]
                     ]
            # loop through curve names
            for idx, data_label in enumerate(curve_names):
                ax = axes1[axIDX[idx][colIDX]]
                ax.set_facecolor(FaceCol)
                ax.patch.set_alpha(FaceColAlpha)
                
                # Get norm data and interpolate to length of collected EMG data
                VariableData = np.array(dataNmean_dict[envelope_names[idx]])
                Norm_EMGTimePoint = np.linspace(0, len(VariableData)-1 , 101)
                x_TimePoint = np.linspace(0, len(VariableData)-1, len(range(0,datLen)))
                upperUnScaleN = np.interp(x_TimePoint, Norm_EMGTimePoint, VariableData)
                
                # Get EMG max absolute value, if data exists
                emg_present = True
                try:
                    Edata = np.array(data_dict[data_label])
                    EdataMean = np.mean(Edata)
                    Edata = Edata - EdataMean
                    ScalFac = max(abs(Edata))
                except:
                    print(f'{limb_spec[Lnum]} {data_label} data not present')
                    ScalFac = max(upperUnScaleN)
                    emg_present  = False
                
                # norm bands
                lowerN = [0] * datLen            
                upperN = (ScalFac / max(upperUnScaleN)) * upperUnScaleN
                ax.fill_between(x, lowerN, upperN, alpha=0.3, color='k')
                
                # plot EMG data 
                if emg_present:
                    ax.plot(x, Edata, color=cc[PlotNum], linewidth=0.5)
                    
                y_limits = ax.get_ylim()
                yupper = upper_limits[idx]
                ylower = lower_limits[idx]
                y_range = yupper - ylower
                # EMG on-off bars
                ax.hlines(ylower + 0.05*y_range, xmin=0, xmax=0.15*datLen, ls='-', color='k', linewidth=2)
                ax.hlines(ylower + 0.05*y_range, xmin=0.55*datLen, xmax=0.7*datLen, ls='-', color='k', linewidth=2)
                ax.hlines(ylower + 0.05*y_range, xmin=0.95*datLen, xmax=datLen, ls='-', color='k', linewidth=2)
                ax.set_ylim([ylower, yupper])
                ax.set_title(limb_spec[Lnum] + f' {titles[idx]} (raw)')
                ax.set_xlim([0,datLen])
                
                # specify x-tick labels
                if idx < 4:
                    ax.set_xticks(np.linspace(0,datLen,6), ['','','','','',''])
                else:
                    ax.set_xticks(np.linspace(0,datLen,6), ['0','20','40','60','80','100'])
                    ax.set_xlabel('% Gait Cycle')
                    
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
            
            # call page text function
            plot_pack = {}
            plot_pack['gcd_file']           = gcd_file
            plot_pack['gcd_count']          = gcd_count
            plot_pack['dataNmean_dict']     = dataNmean_dict
            plot_pack['dataNstd_dict']      = dataNstd_dict
            plot_pack['Lnum']               = Lnum
            plot_pack['LeftPlotNum']        = LeftPlotNum
            plot_pack['RightPlotNum']       = RightPlotNum 
            plot_pack['data_dict']          = data_dict
            plot_pack['gcdNum_selected']    = gcdNum_selected
            plot_pack['PlotNum']            = PlotNum
            plot_pack['cc']                 = cc
            is_EMG                          = True
            
            # call function
            plot_PatientTrialText(self, fig, plot_pack, is_EMG)
                
            if self.checkboxes[file].get():
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
        
        if self.checkboxes[file].get() and varLR.get() == 0 and gcd_count%2 == 0:
            # Show the plot
            plt.show()
            # Save plot as PDF
            pdffile.savefig(fig)
            bookmarks.append((f'EMGfile_{gcd_file[-6:-4]}', marknum))
            marknum += 1
        elif self.checkboxes[file].get() and (varLR.get() == 1 or varLR.get() == 2) and (gcd_count == gcdNum_selected or (gcd_count == 3 and gcdNum_selected > 3)):
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
    gcdNum_selected = len([i for i in self.checkboxes if self.checkboxes[i].get()])
    
    for file in self.checkboxes:
        # If the variable is set
        if self.checkboxes[file].get():
            gcd_file = file[0:-1] # pulling the "L" or "R" off the end that is assigned in checkbox selection
            # Open the .gcd file
            # print(gcd_file)
            
        # ----------------------------- Get patient data ----------------------
            # list(checkboxes).index(gcd_file) pulls the index of the gcd_file in checkboxes to reference appropriate file-path when accessing .gcd files from subfolders
            # gcd_file will have "L" or "R" ending to specify if the file should be plotted for left or right limbs respectively
            ffnIDX = int(list(self.checkboxes).index(gcd_file+'L')/2)
            data_dict = get_gcdData(gcd_file, folderfile_name[::-1][ffnIDX][0])
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
                
        if self.checkboxes[file].get():
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

#Calls the main Function
app = Motion_Report()
app.mainloop()

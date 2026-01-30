- Copy SGMreportGenerator_v3.03.py and PageSettings_SGM.py to local folder

- check requirements.txt file for third party modules to install

- In SGMreportGenerator_v3, change the following lines of code
	line 1  - update to the location of the python.exe file associated with the version of python you use in your IDE
	line 31 - update to the top-level location of your patient directory used in Nexus
	line 32 - update to the location of the TD normative GCD files (\\phl-fs-sh08\MAC Headquarters\_Model code final\Gait\Py3_ShrineGaitModel\NormsGCD_v1.3)
	line 40 - replace with your site name
	
- In Nexus, add a Run Python Operation to your Dynamic processing pipeline
	-Set the path to the SGMreportGenerator_v3 in the Python script file property
	-Under Advanced options, delete the NexusLocalPython.bat file name from the Environment Activation
	-Ensure the Python command is set to python.exe
	
- For best use:
	-Add patient name and DOB information in the "Static Main" main page 
		- this will allow all patient info from the static .py file to be automatically added to the main window and the pdf report that is generated
	-If only left or right trials are desired, the option for "Left Only" or "Right Only" needs to be selected on page 1 - otherwise leave as "Left & Right"
	-Once files are selected, click the button for the specific plot options you want
		- For just lower body kinematics - click "Kinematics". Only lower body kinematics will plot, which includes foot kinematics if foot model data is present
	-When used in Nexus, each page will be plotted in a Nexus window. That window must be closed in order for the next page to be plotted. After all checks have been made and windows closed, be sure to click "Save PDF" button before closing the window or attempting to make another report.
	
- Notes:
	-QA checks for knee flexion/varus cross-talk will only work when one bilateral file is selected - skipped with more than one bilateral file.
	-Drop down options "Diagnosis", "Visit Type", "Condition", "Report Type", and "Select VST Used" need to be manually set for each report - but are all optional
	-"Kinematics" plots lower body Kinematics and Foot Model data if present only
	-"Kinetics" plots only saggital and coronal kinetics, if present in the gcd files
	-"EMG" will plot one page per bilateral .gcd file with EMG data, otherwise it will plot up to 3 gcd files per side, with additional pages of data created if more than 3 gcd files are selected
	-"Kinematics & Kinetics" plots lower body kinematics, foot model data if present, and kinetics data if present in selected gcd files
	-"Basic Report" plots lower body kinematics, foot model data if present, muscle lengths and velocities, and kinetics data if present
	-"Full Report" plots the "Basic Report" in addition to EMG data
	*Note for EMG data - EMG report will be created regardless of whether EMG data was collected
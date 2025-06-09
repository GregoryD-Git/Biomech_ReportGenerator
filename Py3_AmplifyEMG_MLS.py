# -*- coding: utf-8 -*-
"""
Created on Thu May 15 09:59:55 2025

@author: Vicon-OEM
"""

#import Vicon Nexus Subroutines
from viconnexusapi import ViconNexus
vicon = ViconNexus.ViconNexus()

# import other required modules
import numpy as np
import scipy.signal as signal
# import matplotlib.pyplot as plt


def get_dominantFFT(data, SR):
    # 'signal' is the data, 'SR' is the sample rate
    
    # number of samples 
    N = len(data)
    
    # subtract mean to reduce issues with dominant frequency analysis due to strong DC component of the signal
    data = data - np.mean(data)
    
    # computer FFT
    fft_val = np.fft.fft(data)
    freqs = np.fft.fftfreq(N, d=1/SR) # frequency bins
    
    # find dominant frequncy
    dom_idx = np.argmax(np.abs(fft_val[:N//2])) # only positive frequecy values
    dom_frq = freqs[dom_idx]
    
    # code to plot frequency analysis if desired
    # **Optional: Plot Frequency Spectrum**
    # plt.plot(freqs[:N//2], np.abs(fft_val[:N//2]))  # Only positive frequencies
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel("Amplitude")
    # plt.title("Muscle Activity Frequency Spectrum")
    # plt.show()
    
    return dom_frq

def filt_emgSignal(emg_var, SR):
    # Design the Butterworth band-pass filter
    low_cut = 10  # Low cutoff frequency (Hz)
    high_cut = 499  # High cutoff frequency (Hz)
    order = 4  # Filter order
    
    # Get filter coefficients using 'fs' to specify frequency in Hz
    b, a = signal.butter(order, [low_cut, high_cut], btype='band', fs=SR)
    
    # Apply the filter using filtfilt (zero-phase filtering)
    emg_filtered = signal.filtfilt(b, a, emg_var)
    
    return emg_filtered
    
    
def scale_MLSemg(filenamepath):
    
    DeviceIDs = vicon.GetDeviceIDs()
    for DeviceID in DeviceIDs:
        [name, typeID, rate, deviceOutputIDs, forceplate, eyetracker] = vicon.GetDeviceDetails(DeviceID)
        if name == 'EMG':
            SR = rate
            print(f'EMG sample rate extracted is: {SR}')
        
    # initialize dominant frequency list
    dfrq_list = []
    
    # ----------------------------- Get data ------------------------------
    f = open(filenamepath, 'r+')
    data = f.readlines()
    
    # ---------------------------- Get headers ----------------------------
    headerIndex = [idx for idx, line in enumerate(data) if line[0] == '!']
       
    # ----------------------------- Convert data --------------------------
    for idx, num in enumerate(headerIndex):
        # pull keys and asign to temporary variable
        key = data[headerIndex[idx]][1:-1]
        
        if 'Raw' in key and 'Envelope' not in key:
            # pull data associated with given emg data, minus "\n" and convert to float
            try:
                # get all values of data for key associated with headerIndex[num] up to next headerIndex[num+1]
                val = data[headerIndex[idx]+1:headerIndex[idx+1]]
            except:
                # same as above but for the reamining set of data for the last key
                val = data[headerIndex[idx]+1:]
                    
            # convert values to float
            values = []
            
            for i in val:
                try:
                    value = float(i)
                    values.append(value)    
                except:
                    continue
            
            # get and apply scaled emg data
            emg = np.array(values)
            
            if 'SR' not in locals():
                SR = 1000
                print('EMG sample rate not extracted from Vicon, using default sample rate of 1000 Hz')
                
            # frequency analysis            
            dominant_freq = get_dominantFFT(emg, SR)
            print(f'dominant frequency is: {dominant_freq}')
            
            # physiological frequencies should be found in order to justify scaling data
            if dominant_freq > 10 and dominant_freq < 501:
                dfrq_list.append(dominant_freq)
                
                # filter emg signal
                emg_filt = filt_emgSignal(emg, SR)
                
                # scale signal if dominant frequency meets criteria
                scale_val = abs(emg_filt).max()
                emg_scaled = emg_filt * 4 / scale_val
                
                # replace unscaled with scaled data
                datastring = [str(emgstr)+'\n' for emgstr in emg_scaled]            
                data[headerIndex[idx]+1:headerIndex[idx]+1+len(datastring)] = datastring
    
    # close original file
    # print(dfrq_list)
    f.close()
    
    if dfrq_list and min(dfrq_list) > 10 and max(dfrq_list) < 501:
        # save new data over old file
        with open(filenamepath, 'w') as newfile:
            for item in data:
                newfile.write(item)
            
            newfile.close()
    else:
        print('EMG data not scaled, GCD file not updated')

    
# call vicon to get file path and file name for trial of interest
FilePath, FileName = vicon.GetTrialName()
filenamepath= FilePath + "\\" + FileName + '.GCD'

# call function to check and save emg data - should ignore files without EMG data
scale_MLSemg(filenamepath)


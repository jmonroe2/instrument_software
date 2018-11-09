# -*- coding: utf-8 -*-
"""
Created on Tue Oct 30 11:47:14 2018

@author: Fabusers

This script exists as a 0th version test for talking with the VNA
Command list available at https://www.thinksrs.com/downloads/pdfs/manuals/SR810m.pdf
"""
import numpy as np
import matplotlib.pyplot as plt
import time
import pyvisa
import re


global time_const_array 
time_const_array = ["10 us", "30 us", "100 us", "300 us", "1 ms", "3 ms",\
                    "10 ms", "30 ms", "100 ms", "300 ms", "1 s" , "3 s" ,\
                    "10 s" , "30 s" , "100 s" , "300 s" , "1 ks", "3 ks",\
                    "10 ks", "30 ks" ]
global sense_array
sense_array = ["2 nv", "5 nv", "10 nV", "20 nV", "50 nV", "100 nV", "200 nV", "500 nV",\
   "1 uv", "2 uv", "5 uv", "10 uV", "20 uV", "50 uV", "100 uV", "200 uV", "500 uV",\
   "1 mv", "2 mv", "5 mv", "10 mV", "20 mV", "50 mV", "100 mV", "200 mV", "500 mV",\
   "1 V"]

def get_unitFul_number(in_str):
    re_template = "(\d+)\s(\w{1,2})" # 1 or more numbers, white space, 1 or 2 chars
    found = re.findall(re_template, in_str)
    if len(found):
        (num, units) = found[0]
    else:
        raise ValueError("No template matches found in '"+in_str+"'")
    
    units_dict = {'n':1E-9, 'u':1E-6, 'm':1E-3, 'k':1E3, 'M':1E6, 'G':1E9}
    if len(units)>1:
        scale_char = units[0]
        scale = units_dict[scale_char]
    else:
        scale = 1
        
    return float(num)*scale
##END get_unitFul_number


def default_settings(srs_handler):
    '''
    Sets the following default parametersa:
    Time constant: 300 ms
    Sensitivity: 50 uV #@(this should change)
    Phase:  0 deg
    Amplitude: 0.1 V
    Harmonic: 1
    Measure x
    LPF severity: 12 dB
    Sync < 200 Hz
    Source internal
    Signal input: A
    Reserve normal
    AC coupling
    Grounded ground (vs floating ground)
    '''
    
    ## set interface to GPIB
    srs_handler.write("OUTX 1")
    
    ## time constant to 300 ms
    global time_const_array
    index_300ms = time_const_array.index("300 ms")
    srs_handler.write("OFLT "+str(index_300ms))
    
    ## Sensitivity to 50 uV
    global sense_array
    index_50uV = 13 #sensitivity_array.index("50 uV")
    srs_handler.write("SENS "+str(index_50uV))
    
    ## Set phase to zero
    phase = 0.0 # units: deg
    srs_handler.write("PHAS "+str(phase))
    
    ## set amplitude
    amplitude = 0.1 # units: volts
    srs_handler.write("SLVL "+str(amplitude)) # Sine LeVeL
    
    ## measure harmonic number 1
    srs_handler.write("HARM 1")
 
    ## measure in-phase component ('x' not 'r')
    srs_handler.write("DDEF 0,0")
    
    ## low pass filter slope to 12 dB
    srs_handler.write("OFSL 1")
    
    ## Use syncronization for probe freq < 200 Hz
    srs_handler.write("SYNC 1")
    
    ## source internal
    srs_handler.write("FMOD 1")
    
    ## use direct input ('A', not A-B or 'I')
    srs_handler.write("ISRC 0")
       
    ## Reserver mode set to 'normal'
    srs_handler.write("RMOD 1")
    
    ## Set freq to 23.13 Hz (off resonant with 60 Hz)
    freq = 23.13 # units: Hz
    srs_handler.write("FREQ "+str(freq))
    
    ## use AC coupling
    srs_handler.write("ICPL 0")
    
    ## use grounded ground (vs floating)
    srs_handler.write("IGND 1")
##END default_settings


def get_data(srs_handler,num_averages=None,num_discard=0,return_all=False):
    global time_const_array

    ## collected data, averaged or not
    if num_averages:
        time_const_index = srs_handler.query("OFLT ?")
        time_const_str = time_const_array[int(time_const_index)]
        time_const = get_unitFul_number(time_const_str) # units: seconds
        
        ## reset data buffer
        delay_time_sec = num_averages *time_const # units: seconds
        #time.sleep(delay_time_sec) 
        measurements = np.zeros(num_averages)
        srs_handler.write("REST")
        time.sleep(num_discard*time_const)
        for i in range(num_averages):
            m = srs_handler.query("OUTP ? 1")
            measurements[i] =   float(m)  
            time.sleep(time_const)
        out = np.mean(measurements), np.std(measurements)
    else:        
        buffer = srs_handler.query("OUTP ? 1")
        out = float(buffer)
  
    if return_all:
        return out, measurements
    else:
        return out
        
        #print(time_const); return 0;
##END get_data

        
def tune_sensitivity(srs_handler,timeOut = 10):
    global sense_array    

    num_attempts = 0
    while num_attempts<timeOut:
        current_sense_index = int(srs_handler.query("SENS ?"))
        max_range = float(get_unitFul_number(sense_array[current_sense_index]))
        min_range = float(get_unitFul_number(sense_array[current_sense_index-1]))
        
        ## check if current reading is in bounds
        reading = float(srs_handler.query("OUTP ? 1"))
        add = (np.sign(reading-max_range)+1)//2  # if read > max: add +1
        sub = (np.sign(min_range-reading)+1)//2  # if read < min: subtract +1
        srs_handler.write("SENS "+str(current_sense_index+add-sub))
        num_attempts += 1
        if not (add + sub): ## no change
            break
    if num_attempts>=timeOut:
        print("Unable to tune sensitivity")
    
##END tune_sensitivity


def main():
    
    gpib_number = 8
    address = "GPIB0::"+str(gpib_number)+"::INSTR"

    ## start session with srs
    rm = pyvisa.ResourceManager()
    srs_instr = rm.open_resource(address)
    try:
        ## setup srs for data collection
        #default_settings(srs_instr)
        #       tune_sensitivity(srs_instr)
            
        ## dynamically get data from srs
        (voltage, std_err), ms = get_data(srs_instr, \
                    num_averages=8, num_discard=4, return_all=True)
        ## units: volts
        voltage *= 1E6
        std_err *= 1E6
        if std_err <1:
            print(np.round(voltage,1), "+/-", std_err, " uV")
        else:
            print("Noisy measurement",voltage, "+/-", std_err )
        return ms*1E6 ## units volts
    finally:
        srs_instr.close()
##END main()

if __name__ == '__main__':
    ms = main()
    #plt.clf()
    #plt.plot(ms)


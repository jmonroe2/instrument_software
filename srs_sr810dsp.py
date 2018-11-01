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
   "2 uv", "5 uv", "10 uV", "20 uV", "50 uV", "100 uV", "200 uV", "500 uV",\
   "2 mv", "5 mv", "10 mV", "20 mV", "50 mV", "100 mV", "200 mV", "500 mV",\
   "1 V"]

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

def get_data(srs_handler,dynamic=False,average_num=None):
    if not dynamic:
        if not average_num:
            buffer = srs_handler.query("OUTP ? 1")
            return float(buffer)
        else:
            time_const = 
    else:
        current
##END get_data


def main():
    gpib_number = 8
    address = "GPIB0::"+str(gpib_number)+"::INSTR"

    ## start session with srs
    rm = pyvisa.ResourceManager()
    srs_instr = rm.open_resource(address)
    ## setup srs for data collection
    default_settings(srs_instr)
    srs_instr.write("SENS 15")
    
    ## dynamically get data from srs
    num = 20
    xs = np.zeros(num)
    for i in range(num):
        if np.mod(i,10)==0: print(i)
        time.sleep(0.3*3) # seconds
        x = get_data(srs_instr, dynamic=False)    
        xs[i] = x
        
    return xs*1E6
##END main()

if __name__ == '__main__':
    xs = main()
    clipped = xs[10:]
    print(np.round(np.mean(clipped),1), "+/-", np.std(clipped) )


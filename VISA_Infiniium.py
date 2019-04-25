# *********************************************************
# This program illustrates a few commonly-used programming
# features of your Agilent Infiniium Series oscilloscope.
# *********************************************************
import visa
import string
#import struct
import sys
import time
import numpy as np
#------------------------------------------------------------------------------
# globals
#------------------------------------------------------------------------------
inf        = None
debug      = 0
sample     = 500
run_number = 14;
# =========================================================
# Initialize:
# =========================================================
def initialize():
    # Clear status.
    inf.write("*CLS")
    # Get and display the device's *IDN? string.
    idn_string = inf.query("*IDN?")
    print ("Identification string: %s",idn_string)
    # Load the default setup.
    #do_command("*RST")

# =========================================================
# Single Trigger:
# ACQuire:STATE{OFF|ON|RUN|STOP|<NR1>}
#       This command starts or stops acquisitions. When state is
#       set to ON or RUN, a new acquisition will be started. If the
#       last acquisition was a single acquisition sequence, a new
#       single sequence acquisition will be started. If the last acquisition
#       was continuous, a new continuous acquisition will
#       be started.
# EXPort:FILEName "C:\\TekScope\\Data\\xyz.csv"
# EXPort START
# EXPort?
# BUSY? This query--only command returns the status of the oscilloscope.
#       This command allows you to synchronize the operation
#       of the oscilloscope with your application program.
#       RETURNS: 1=wait for trigger, 0=trigger found
# TRIGger:STATE? This query--only command returns the current state of the
#       triggering system. This command is equivalent to viewing
#       the trigger status LEDs on the instrument front--panel.
#       RETURNS: READY=wait for trigger, SAVE=trigger found
# SAVE:WAVEform:FILEFormat  {INTERNal|MATHCad|MATLab|SPREADSHEETCsv|SPREADSHEETTxt}
#       This command specifies or returns the file format for saved
#       waveforms. Waveform header and timing information is
#       included in the resulting file of non--internal formats. The
#       instrument saves DPO and WFMDB waveforms as a
#       500x200 matrix, with the first row corresponding to the
#       most recently acquired data. The values specified by
#       DATa:STARt, DATa:STOP, DATa:FRAMESTARt and
#       DATa:FRAMESTOP determine the range of waveform data
#       to output. In the event that DATa:STOP value is greater
#       than the current record length, the current record length
#       determines the last output value.

#=========================================================
# ACQuire:STATE{OFF|ON|RUN|STOP|<NR1>}
def trigger():
    inf.write("ACQuire:STATE OFF")
    inf.write("ACQuire:STATE ON")
    time.sleep(0.1)
    triggered = '1\n'
    while triggered=='1\n':
        time.sleep(0.5)
        triggered = inf.query("BUSY?")
        
# =========================================================
# Save:     SAVE:WAVEform CH2,"C:\\TekScope\\Data\\abcd.csv"
# =========================================================
def save():
    inf.write("SAVE:WAVEform:FILEFormat SPREADSHEETCsv")  
    cmd = "SAVE:WAVEform CH2,'C:\\TekScope\\Data\\"+ wave_csv_name + ".csv'"
    inf.write(cmd)
    #inf.write("EXPort START") 
   
#-----------------------------------------------------------------------------
# main 
#-----------------------------------------------------------------------------
if __name__ == '__main__':

    rm = visa.ResourceManager()
    print(rm.list_resources())

    inf         = rm.open_resource('GPIB0::1::INSTR')
    inf.timeout = 2000
    inf.term_chars = ""
    inf.clear()
    print (sample)
    print(inf.query("*IDN?"))

    # Initialize the oscilloscope, capture data, and analyze.

    for i in range(0,sample):
        #initialize()
        wave_csv_name = "qdgaas_%04i_%04i"%(run_number,i)
        print(i)
        trigger()
        save()
#------------------------------------------------------------------------------

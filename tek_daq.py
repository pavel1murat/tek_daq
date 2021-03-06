#!/usr/bin/python
# Example that scans a computer for connected instruments that
# are compatible with the VISA communication protocol.
#
# The instrument VISA resource ID for each compatible instrument
# is then listed.
#
#
# Dependencies:
# Python 3.4 32 bit
# PyVisa 1.7
#
# Rev 1: 08302018 JC

import os, sys, time, numpy, argparse
import pyvisa as visa
from datetime import datetime
import os.path

#------------------------------------------------------------------------------
# default parameter values
#------------------------------------------------------------------------------
nevents   = None
wait_time = None
output_fn = None
ofile     = None
header    = None

#------------------------------------------------------------------------------
def init():
#------------------------------------------------------------------------------
# check available resources and print them
#------------------------------------------------------------------------------
    rm  = visa.ResourceManager()
    res = rm.list_resources();

    # this is our scope
    tek = rm.open_resource('GPIB0::1::INSTR')
    q = tek.query("*IDN?");
    ofile.write("%s\n"%q.strip());

    tek.timeout    = 10000000;
    tek.term_chars = " ";
    tek.clear()
#------------------------------------------------------------------------------
# turn acquisition OFF
#------------------------------------------------------------------------------
    tek.write("ACQuire:STATE OFF")
#------------------------------------------------------------------------------
# set HEADER OFF and print to confirm that
#------------------------------------------------------------------------------
    # tek.write("HEADER ON")
    tek.write("HEADER OFF")

    tek.write("DATA:START 1")
    tek.write("DATA:STOP %i"%nSamples)

    result = tek.query("DATA?").strip()
    ofile.write("DATA: result=%s\n"%result);
#------------------------------------------------------------------------------
# print waveform format specifications
# 's' - string
#------------------------------------------------------------------------------
    tek.write("DATA:SOURCE CH1")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH1: %s\n"%result.strip());

    nw = len(result.split(';'));

    nch_read = 0;
    cmd      = None
    if (nw > 5) :
        cmd      = "DATA:SOURCE CH1"
        nch_read = 1

    tek.write("DATA:SOURCE CH2")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH2: %s\n"%result.strip());

    nw = len(result.split(';'));
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH2"
        else            : cmd = cmd+", CH2"
        nch_read = nch_read+1

    tek.write("DATA:SOURCE CH3")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH3: %s\n"%result.strip());

    nw = len(result.split(';'));
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH3"
        else            : cmd = cmd+", CH3"
        nch_read = nch_read+1

    tek.write("DATA:SOURCE CH4")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH4: %s\n"%result.strip());

    nw = len(result.split(';'));
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH4"
        else            : cmd = cmd+", CH4"
        nch_read = nch_read+1

#------------------------------------------------------------------------------
# finally, specify channels to read
#------------------------------------------------------------------------------
    if (cmd) : tek.write(cmd)

    return (tek)

#------------------------------------------------------------------------------
def read_trigger(tek,trigNum):

    ofile.write ("trigger = %i\n"%trigNum)

    header = int(tek.query("HEADER?"));

    tek.write("ACQuire:STATE ON")
    tek.write("ACQuire:STOPAFTER SEQUENCE")
#------------------------------------------------------------------------------
# wait till the end of acquisition
#------------------------------------------------------------------------------
    busy = 1
    while busy == 1:
        time.sleep(0.04)
        result = tek.query("BUSY?").strip();

        if (header == 1) : busy = int(result.split()[1])
        else             : busy = int(result)

        if (debug) : print("result = %s busy=%i"%(result,busy));
#------------------------------------------------------------------------------
# when done, disable further acquisition and read the collected waveform
# read in ascii, didn't validate binary reading yet - that might be much faster
# also, may want to read multiple waveforms at a time - also need to learn how
# to do that
#------------------------------------------------------------------------------
#    tek.write("ACQuire:STATE OFF")

    #    values = tek.query_binary_values('CURV?', is_big_endian=True)
    #    values = tek.query_ascii_values('CURV?',converter='s') # , container=numpy.array)
    values = numpy.array(tek.query_ascii_values('CURV?'));

#    tek.write('CURV?')    # , container=numpy.array)
#    values = tek.read_raw();
#------------------------------------------------------------------------------
# print output in ascii to the screen - will have to convert it into ROOT anyway
# and redirect to a file - this is slow, but good enough
#------------------------------------------------------------------------------
    ip=0;
    for x in values:
        ofile.write("%6i,"%x);  # comma in the end tells not to print "\n"
        ip = ip+1;
        if (ip == 20):
            ofile.write("\n");
            ip = 0

    if (ip != 0): ofile.write("\n");
#------------------------------------------------------------------------------
# end of waiting, return
#------------------------------------------------------------------------------
nSamples  = 500
debug     = None
scope     = None

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nevents"  , type=int   , default = 1   ,
                        help="number of events to process")
    parser.add_argument("-o", "--output_fn"             , default = "/dev/stdout",
                        help="output filename")
    parser.add_argument("-r", "--run_number",  type=int , default = None,
                        help="run number")
    parser.add_argument("-w", "--wait_time" , type=float, default = 0.04,
                        help="wait time")
    parser.add_argument("-p", "--print_freq",type=int   , default = 10,
                        help="print frequency")
    args = parser.parse_args()

    if (args.nevents  )  : nevents   = args.nevents
    if (args.wait_time)  : wait_time = args.wait_time;
    
    # default filename is defined by the run number, but can be overwritten by "-o"
    if (args.run_number) : output_fn = "qdgaas.fnal."+format("%06i"%args.run_number)+".txt"

    if (args.output_fn != "/dev/stdout")  : output_fn = args.output_fn

    if os.path.exists(output_fn) == True:
        confirm = input("The output file already exists. Overwrite? (yes/no)")
        if confirm == 'no':
            sys.exit()

    print_freq = args.print_freq;

    print("~~~~~~~~~~~~~TEK DAQ~~~~~~~~~~~~~")
    print("nevents   : %i"%nevents)
    print("wait_time : %f"%wait_time)
    print("output_fn : %s"%output_fn)

    if not os.path.exists(output_fn) :
        ofile = open(output_fn,"w");
    else:
        response = input("Are you sure you want to overwrite the existing file ? ")
        if (response[0].upper() == "Y") : ofile = open(output_fn,"w")
        else :
            print("ERROR: exiting");
            exit()
#------------------------------------------------------------------------------
# output file is open
#------------------------------------------------------------------------------
    scope = init();

#   write start time to file
    dt = str(datetime.now())
    ofile.write("RUN_START_TIME: %s\n"%dt)
    print("RUN_START_TIME: ",dt)

    q = scope.query("*IDN?");
    print(q.strip());

    for i in range(nevents):
        # print frame number intermittently
        if ((i % print_freq) == 0): print("Event {0}".format(i))
        read_trigger(scope,i)

#   write end time to file
    dt = str(datetime.now())
    ofile.write("RUN_END_TIME: %s\n"%dt)
    print("RUN_END_TIME: ",dt)
#------------------------------------------------------------------------------
# I guess, the following diagnostics is due to something not being formally closed
# but the data file looks OK
#------------------------------------------------------------------------------
# Event 1990
# RUN_END_TIME:  2020-01-29 12:28:21.599908
# libgpib: invalid descriptor
# libgpib: invalid descriptor
# Exception ignored in: <function Gpib.__del__ at 0x7f42c2081560>
# Traceback (most recent call last):
#   File "/usr/lib64/python3.7/site-packages/Gpib.py", line 31, in __del__
#   File "/usr/lib64/python3.7/site-packages/Gpib.py", line 39, in close
# gpib.GpibError: close() failed: One or more arguments to the function call were invalid.

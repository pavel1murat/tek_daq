#!/usr/bin/python
"""
Combination of tek_daq.py and dpo_fastframe.py
"""

import sys, time, argparse
import numpy as np
import pyvisa as visa
from datetime import datetime

# default parameter values
nevents   = None
wait_time = None
output_fn = None
ofile     = None
header    = None


def init():
#------------------------------------------------------------------------------
# check available resources and select our scope
#------------------------------------------------------------------------------
    rm  = visa.ResourceManager()
    res = rm.list_resources()
    tek = rm.open_resource('GPIB0::1::INSTR')
    q = ((tek.query("*IDN?")).strip())
    print(q)
    ofile.write("%s\n"%q)

    tek.timeout    = 100000
    tek.encoding   = 'latin_1'
    tek.term_chars = " "
    tek.clear()

#------------------------------------------------------------------------------
# configure data transfer settings
#------------------------------------------------------------------------------
    tek.write('acquire:state off')
    tek.write('horizontal:fastframe:state on')
    tek.write('header off')
    tek.write('data:encdg fastest')

    recordLength = int(tek.query('horizontal:fastframe:length?').strip())
    tek.write('data:stop {}'.format(recordLength))

    tek.write('wfmoutpre:byt_n 1')

#------------------------------------------------------------------------------
# determine which channels have input
#------------------------------------------------------------------------------
    result = tek.query("DATA?").strip()
    ofile.write("DATA: result=%s\n"%result)
    tek.write("DATA:SOURCE CH1")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI")
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH1: %s\n"%result.strip())

    nw = len(result.split(';'))

    nch_read = 0
    cmd      = None
    if (nw > 5) :
        cmd      = "DATA:SOURCE CH1"
        nch_read = 1

    tek.write("DATA:SOURCE CH2")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI")
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH2: %s\n"%result.strip())

    nw = len(result.split(';'))
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH2"
        else            : cmd = cmd+", CH2"
        nch_read = nch_read+1

    tek.write("DATA:SOURCE CH3")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI")
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH3: %s\n"%result.strip())

    nw = len(result.split(';'))
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH3"
        else            : cmd = cmd+", CH3"
        nch_read = nch_read+1

    tek.write("DATA:SOURCE CH4")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI")
    result = tek.query("WFMOutpre?")
    ofile.write("WFMOutpre:CH4: %s\n"%result.strip())

    nw = len(result.split(';'))
    if (nw > 5) :
        if (cmd == None): cmd = "DATA:SOURCE CH4"
        else            : cmd = cmd+", CH4"
        nch_read = nch_read+1

#------------------------------------------------------------------------------
# finally, specify which channels to read
#------------------------------------------------------------------------------
    if (cmd) : tek.write(cmd)
    print('Data transfer settings configured.')
    return (tek)


def get_waveform_info(startFrame,stopFrame):

    tek.write('horizontal:fastframe:count {}'.format(stopFrame))
    tek.write('data:framestart {}'.format(startFrame))
    tek.write('data:framestop {}'.format(stopFrame))

    tek.write('data:encdg fastest')
    tek.write('acquire:stopafter sequence')
    tek.write('acquire:state on')
    tek.query('*OPC?')
    binaryFormat = tek.query('wfmoutpre:bn_fmt?').rstrip()
    numBytes     = tek.query('wfmoutpre:byt_nr?').rstrip()
    byteOrder    = tek.query('wfmoutpre:byt_or?').rstrip()
    encoding     = tek.query('data:encdg?').rstrip()

    if 'RIB' in encoding or 'FAS' in encoding:
        dType = 'b'
        bigEndian = True
    elif encoding.startswith('RPB'):
        dType = 'B'
        bigEndian = True
    elif encoding.startswith('SRI'):
        dType = 'b'
        bigEndian = False
    elif encoding.startswith('SRP'):
        dType = 'B'
        bigEndian = False
    elif encoding.startswith('FP'):
        dType = 'f'
        bigEndian = True
    elif encoding.startswith('SFP'):
        dType = 'f'
        bigEndian = False
    elif encoding.startswith('ASCI'):
        raise visa.InvalidBinaryFormat('ASCII Formatting.')
    else:
        raise visa.InvalidBinaryFormat

    return dType, bigEndian


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nevents"  , type=int  , default = 1   ,
                        help="number of events to process")
    parser.add_argument("-w", "--wait_time", type=float, default = 0.04,
                        help="wait time")
    parser.add_argument("-o", "--output_fn"            , default = "/dev/stdout",
                        help="output filename")
    parser.add_argument("-r", "--run_number", type=int , default = None  ,
                        help="run number")
    args = parser.parse_args()

    if   (args.nevents  )  : nevents   = args.nevents
    if   (args.wait_time)  : wait_time = args.wait_time
    if   (args.run_number) :
        output_fn = "qdgaas.fnal."+format("%06i"%args.run_number)+".txt"
    elif (args.output_fn)  : output_fn = args.output_fn

    # print("nevents   : {}".format(nevents))
    # print("wait_time : {}".format(wait_time))
    # print("output_fn : {}".format(output_fn))

    ofile = open(output_fn,"w")

    tek = init()

#   write starting datetime to file
    dt = str(datetime.now())
    print("RUN_START_TIME: ",dt)
    ofile.write("RUN_START_TIME: %s\n"%dt)

    print('Acquiring waveforms...')

    i = 0 # number of events taken
    while i < nevents:
        # set how many frames to take in a round
        startFrame = 1
        stopFrame  = 1000 # default number of frames to take each read
        i += stopFrame
        if i > nevents:
            i -= stopFrame
            stopFrame = nevents - i
            i += stopFrame

        # collect and fetch data
#        print('collecting waveforms...')
        dType, bigEndian = get_waveform_info(startFrame,stopFrame)
#        print('transferring waveforms...')
        data = tek.query_binary_values(
            'curve?',datatype=dType,is_big_endian=bigEndian,container=np.array)

        # fetch and write timestamps to file
        # !!! If using channel other than 1, change timestamp query !!!
        allTStamps = tek.query(
            'horizontal:fastframe:timestamp:all:ch1? {0},{1}'.format(startFrame,stopFrame))
        allTStamps = allTStamps.strip()
        allTStamps = allTStamps.replace('"','')
        tstamps = allTStamps.split(",")
        ofile.write('>>>Num_Frames: %i\n'%stopFrame)
        for t in tstamps:
            ofile.write(str(t))
            ofile.write('\n')

        # write data to file
        ip=0;
        for x in data:
            ofile.write("%6i,"%x);
            ip = ip+1;
            if (ip == 20):
                ofile.write("\n");
                ip = 0

        if (ip != 0): ofile.write("\n");
        print('Frame {0} complete'.format(i))

    print('Waveforms acquired.')

#   write ending datetime to file
    dt = str(datetime.now())
    print("RUN_END_TIME:   ",dt)
    ofile.write("RUN_END_TIME: %s"%dt)

#   np.set_printoptions(threshold=sys.maxsize)
#   print(data)

    tek.close()

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
    ofile.write("%s\n"%q.strip())

    tek.timeout    = 100000
    tek.encoding = 'latin_1'
    tek.term_chars = " "
    tek.clear()
#------------------------------------------------------------------------------
# configure data transfer settings
#------------------------------------------------------------------------------
    tek.write("acquire:state off")
    tek.write('horizontal:fastframe:state on')
    tek.write('horizontal:fastframe:count {}'.format(nevents))
    tek.write("header off")

    tek.write('data:encdg fastest')
    tek.write('data:source ch1')       #change this to take channel number from cmd

    recordLength = int(tek.query('horizontal:fastframe:length?').strip())
    tek.write('data:stop {}'.format(recordLength))

    startFrame = 1
    tek.write('data:framestart {}'.format(startFrame))
    tek.write('data:framestop {}'.format(nevents))

    tek.write('wfmoutpre:byt_n 1')

#------------------------------------------------------------------------------
# determine which channels have input
#------------------------------------------------------------------------------
    result = tek.query("DATA?").strip()
    ofile.write("DATA: result=%s\n"%result);
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

    print('Data transfer settings configured.')

    return (tek)

def get_waveform_info()
    header = int(tek.query('HEADER?'))
    tek.write('acquire:stopafter sequence')
    tek.write('acquire:state on')
    tek.query('*OPC?')
    binaryFormat = tek.query('wfmoutpre:bn_fmt?').rstrip()
    numBytes     = tek.query('wfmoutpre:byt_nr?').rstrip()
    byteOrder    = tek.query('wfmoutpre:byt:or?').rstrip()
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
    args = parser.parse_args()

    if (args.nevents  ) : nevents   = args.nevents
    if (args.wait_time) : wait_time = args.wait_time;
    if (args.output_fn) : output_fn = args.output_fn;

    print("nevents   : {}".format(events))
    print("wait_time : {}".format(wait_time))
    print("output_fn : {}".format(output_fn))

    ofile = open(output_fn,"w");

    scope = init();

#   print and write datetime at start of run
    dt = str(datetime.now())
    ofile.write("RUN_START_TIME: %s\n"%dt)

    print('Acquiring waveform.')
    tek.write('acquire:stopafter sequence')
    tek.write('acquire:state on')
    dpo.query('*opc?')
    print('Waveform acquired.')

    dType, bigEndian = get_waveform_info()
    data = tek.query_binary_values('curve?',datatype=dType,is_big_endian=bigEndian,container=np.array)


#   print and write datetime at end of run
    dt = str(datetime.now())
    ofile.write("RUN_END_TIME: %s\n"%dt)

#    print("#-------------- DAQ run ended -------------")

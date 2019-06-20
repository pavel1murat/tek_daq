#!/usr/bin/python
# example from https://github.com/tkzilla/visa_control_examples/blob/master/Python/DPO/dpo_fastframe.py
"""
VISA Control: FastFrame Summary Frame Transfer
Author: Morgan Allison
Updated: 11/2017
Acquires 10 instances of the Probe Compensation signal on the scope
using FastFrame and transfers the summary frame to the computer.
Windows 7 64-bit, TekVISA 4.0.4
Python 3.6.3 64-bit (Anaconda 4.4.0)
NumPy 1.13.3, MatPlotLib 2.0.2, PyVISA 1.8
To get PyVISA: pip install pyvisa
Download Anaconda: http://continuum.io/downloads
Anaconda includes NumPy and MatPlotLib
Tested on DPO5204B, MSO72004, DPO7104C, and MSO58
"""

import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import argparse

def get_waveform_info():
    """Gather waveform transfer information from scope."""
    dpo.write('acquire:stopafter sequence')
    dpo.write('acquire:state on')
    dpo.query('*OPC?')
    binaryFormat = dpo.query('wfmoutpre:bn_fmt?').rstrip()
    numBytes     = dpo.query('wfmoutpre:byt_nr?').rstrip()
    byteOrder    = dpo.query('wfmoutpre:byt_or?').rstrip()
    encoding     = dpo.query('data:encdg?').rstrip()
    print('Encoding: ',encoding)
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


"""############### SEARCH/CONNECT ###############"""
# establish communication with dpo
rm = visa.ResourceManager()
res = rm.list_resources()
dpo = rm.open_resource('GPIB::1::INSTR')
dpo.timeout = 100000
dpo.encoding = 'latin_1'
print((dpo.query('*idn?')).strip())


"""############### CONFIGURE INSTRUMENT ###############"""

"""
dpo.write('*rst')

# variables for individual settings
hScale    =  1e-6    # horizontal scale
nframes =  10      # number of frames
vScale    =  0.5     # vertical scale
vPos      = -0.00125 # vertical position, GS/s
trigLevel =  0.15    # trigger threshold, in volts

# dpo setup
dpo.write('acquire:state off')
dpo.write('horizontal:mode:scale {}'.format(hScale))
dpo.write('horizontal:fastframe:state on')
dpo.write('horizontal:fastframe:count {}'.format(nframes))
dpo.write('ch1:scale {}'.format(vScale))
dpo.write('ch1:position {}'.format(vPos))
dpo.write('trigger:a:level:ch1 {}'.format(trigLevel))
print('Horizontal, vertical, and trigger settings configured.')
"""

# Configure data transfer settings

# set number of frames to capture from command line
parser = argparse.ArgumentParser()
parser.add_argument("-n","--nframes",type=int,default=1,help="number of frames to process")
args = parser.parse_args()
if (args.nframes) : nframes = args.nframes

dpo.write('acquire:state off')
dpo.write('horizontal:fastframe:state on')
dpo.write('horizontal:fastframe:count {}'.format(nframes))
dpo.write('header off')

dpo.write('data:encdg fastest')
dpo.write('data:source ch1')

# record length determines number of waveforms captured
recordLength = int(dpo.query('horizontal:fastframe:length?').strip())
dpo.write('data:stop {}'.format(recordLength))

startFrame = 1
dpo.write('data:framestart {}'.format(startFrame))
dpo.write('data:framestop {}'.format(nframes))

dpo.write('wfmoutpre:byt_n 1')
print('Data transfer settings configured.')

"""###############ACQUIRE DATA###############"""
print('Acquiring waveform.')
dpo.write('acquire:stopafter sequence')
dpo.write('acquire:state on')
dpo.query('*opc?')
print('Waveform acquired.')

# Retrieve vertical and horizontal scaling information
yOffset = float(dpo.query('wfmoutpre:yoff?'))
yMult = float(dpo.query('wfmoutpre:ymult?'))
yZero = float(dpo.query('wfmoutpre:yzero?'))

numPoints = int(dpo.query('wfmoutpre:nr_pt?'))*nframes
print('Record length:',recordLength)
print('Number of frames plotted:',nframes)
print('Number of points:',numPoints)

xIncr = float(dpo.query('wfmoutpre:xincr?'))
xZero = float(dpo.query('wfmoutpre:xzero?'))

dType, bigEndian = get_waveform_info()
data = dpo.query_binary_values(
    'curve?', datatype=dType, is_big_endian=bigEndian, container=np.array)


"""################ ACQUIRE TIMESTAMPS ###############"""

allTStamps = dpo.query('horizontal:fastframe:timestamp:all:ch1? {0},{1}'.format(startFrame,nframes))
allTStamps = allTStamps.strip()
allTStamps = allTStamps.replace('"','')
tstamps = allTStamps.split(",")
print('TIMESTAMPS')
for i in tstamps:
    print(i)


"""############### PLOT DATA ###############"""
# Using the scaling information, rescale the binary data
scaleddata = (data - yOffset) * yMult + yZero  # sets y scale
scaledtime = np.arange(xZero, xZero + (xIncr * numPoints), xIncr)

# plot the figure with correct scaling
plt.subplot(111, facecolor='k')
plt.plot(scaledtime * 1e3, scaleddata, color='y')
plt.ylabel('Voltage (V)')
plt.xlabel('Time (millisec)')
plt.tight_layout()
plt.show()

dpo.close()

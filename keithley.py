#!/usr/bin/python
# see reference manual at https://doc.xdevs.com/docs/Keithley/2231/077100401_Reference manual.pdf
# 
import visa, sys, time, numpy, fileinput, argparse

rm = None;

def parse_arguments():
    parser = argparse.ArgumentParser()
    
    #    parser.add_argument("-n", "--nevents"  , type=int  , default = 1   ,
    #                        help="number of events to process")
    #    parser.add_argument("-o", "--output_fn"            , default = "/dev/stdout",
    #                        help="output filename")
    #    args = parser.parse_args()
    #
    #    if (args.nevents  ) : nevents   = args.nevents
    #    if (args.output_fn) : output_fn = args.output_fn;
    #
    #    print("nevents   : %i"%nevents)
    #    print("output_fn : %s"%output_fn)
#------------------------------------------------------------------------------
# make it a class...
#------------------------------------------------------------------------------
class Keithley2231:

    def __init__(self, dev):   # address like "ASRL/dev/ttyUSB0::INSTR"

        self._dev            = dev;
        self._dev.timeout    = 4000;
        self._dev.term_chars = " ";
        print "emoe, initialized"

    def run_diagnostics(self):
        
        # switch to remote control mode
        self._dev.write("syst:rem");

        res = self._dev.query("*ese?");
        print("*ESE? : %s"%res),   # a fairly idiotic python way of disabling printing the LF

        res = self._dev.query("*idn?");
        print("*IDN? : %s"%res),   # 

        res = self._dev.query("syst:vers?");
        print("SYST:VERS? : %s"%res),   # 

        res = self._dev.query("syst:module?");
        print("SYST:MODU? : %s"%res),   # 

        res = self._dev.query("*sre?");
        print("*SRE? : %s"%res),   # 
        
        res = self._dev.query("*stb?");
        print("*STB? : %s"%res),   # 

        res = self._dev.query("*tst?");
        print("*TST? : %s"%res),   # 

        res = self._dev.write("*rcl 0");

        # enable CH1 output
        self._dev.write("output enable");
        self._dev.write("chan:output 1");

        res = self._dev.query("meas:volt?");
        print("MEAS:VOLT? : %s"%res),   # 

        # switch back to local control mode
        self._dev.write("syst:local");
    

    def run(self):
        # measurement = 0
        voltage = 0
        #     A.write("APPLY CH1," +str(voltage) +",0.1")
        
        #    dev.write("APPLY CH2," +str(voltage) +",0.1")
  
        #    A.write("APPLY CH3," +str(voltage) +",0.1")
        #
        #    voltage=0.40
        #    voltage2=0.50
        #    voltage3=0.60
        #    A.write("OUTP 1")
        #    A.write("APPLY CH1," +str(voltage) +",0.2")
        #
        #    A.write("APPLY CH2," +str(voltage2) +",0.2")
        #    A.write("APPLY CH3," +str(voltage3) +",0.2")
        #    #time.sleep(0.55)
        #    #A.write("MEAS:CURR")
        #    time.sleep(0.78)
        #    for i in range(100):
        #        #A.write("MEAS:CURR")
        #        measurement = A.ask("FETC:CURR? ALL")
        #        print voltage,measurement
        #        voltage = 0
        #        A.write("APPLY CH1," +str(voltage) +",0.1")
        #        A.write("APPLY CH2," +str(voltage) +",0.1")
        #        A.write("APPLY CH3," +str(voltage) +",0.1")

#------------------------------------------------------------------------------
# everything starts here
#------------------------------------------------------------------------------
if __name__ == '__main__':

    parse_arguments();
    
    rm  = visa.ResourceManager()
    res = rm.list_resources();
    dev = rm.open_resource(res[0]);

    # assume only one device active on the USB bus
    ps = Keithley2231(dev);
    
    ps.run_diagnostics()

    ps.run();

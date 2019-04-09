#Example that scans a computer for connected instruments that
#are compatible with the VISA communication protocol.
#
#The instrument VISA resource ID for each compatible instrument
#is then listed.
#
#
#Dependencies:
#Python 3.4 32 bit
#PyVisa 1.7
#
#Rev 1: 08302018 JC

import visa, sys, time, numpy

#------------------------------------------------------------------------------
def init():
    rm  = visa.ResourceManager()
    res = rm.list_resources();
    print(res)
    
    # this is our scope
    tek = rm.open_resource('GPIB0::1::INSTR')
    q = tek.query("*IDN?");
    print(q.strip());

    tek.timeout    = 2000;
    tek.term_chars = " ";
    tek.clear()

    # tek.write("HEADER ON")
    tek.write("HEADER OFF")
    
    header = int(tek.query("HEADER?"));
    print("header = %i"%header);

    tek.write("ACQuire:STATE OFF")

    tek.write("DATA:START 1")
    tek.write("DATA:STOP %i"%nSamples)

    result = tek.query("DATA?").strip()
    print("DATA: result=%s"%result);
#------------------------------------------------------------------------------
# print waveform format specifications
# 's' - string
#------------------------------------------------------------------------------
    tek.write("DATA:SOURCE CH1")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    print("WFMOutpre:CH1: ",result);

    tek.write("DATA:SOURCE CH2")
    tek.write("DATA:ENCdg  ASCII")
    tek.write("WFMO:BN_F RI");
    result = tek.query("WFMOutpre?")
    print("WFMOutpre:CH2: ",result);
#------------------------------------------------------------------------------
# finally, read two channels
#------------------------------------------------------------------------------
    tek.write("ACQuire:STATE OFF")
    tek.write("DATA:SOURCE CH1, CH2")

    return (tek)

#------------------------------------------------------------------------------
def read_trigger(tek,trigNum):

    print ("trigger = %i"%trigNum)

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
        print("%6i,"%x),  # comma in the end tells not to print "\n"
        ip = ip+1;
        if (ip == 20):
            print("");
            ip = 0

    if (ip != 0): print ("");
#------------------------------------------------------------------------------
# end of waiting, return
#------------------------------------------------------------------------------
nSamples = 500
debug    = None
scope    = None

if __name__ == '__main__':

    scope = init();

    q = scope.query("*IDN?");
    print(q);
    
    nevents = int(sys.argv[1]);
    
    for i in range(nevents):
        read_trigger(scope,i)

#    print("#-------------- DAQ run ended -------------")

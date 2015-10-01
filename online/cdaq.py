from PyDAQmx import *
import numpy
import matplotlib.pyplot as plt

# Declaration of variable passed by reference
taskHandle = TaskHandle()
read = int32()
num_samples = 1000
data = numpy.zeros((num_samples,), dtype=numpy.float64)

try:
    # DAQmx Configure Code
    DAQmxCreateTask("",byref(taskHandle))
    DAQmxCreateAIVoltageChan(taskHandle,"emg/ai0","",DAQmx_Val_RSE ,-10.0,10.0,DAQmx_Val_Volts,None)
    #DAQmxCreateAICurrentChan(taskHandle, "emg/ai1", "", DAQmx_Val_Cfg_Default, -5.0 ,5.0, DAQmx_Val_Volts, None)
    DAQmxCfgSampClkTiming(taskHandle,"",1000.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,num_samples)

    # DAQmx Start Code
    condata = None
    count = 0
    DAQmxStartTask(taskHandle)

    #plt.ion()
    #plt.show()
    while count < 5:
        count += 1
        print count
        # DAQmx Read Code
        DAQmxReadAnalogF64(taskHandle,num_samples,10.0,DAQmx_Val_GroupByChannel,data,num_samples,byref(read),None)
        print 'after'

        if condata is None:
            condata = data
        #elif condata.shape[0] == 1000:
        #    condata[:750] = condata[250:]
        #    condata[750:] = data
        else:
            condata = numpy.concatenate((condata, data))
        #    plt.clf()
        #plt.plot(condata)
        #plt.draw()
    plt.plot(condata)
    plt.show()
except DAQError as err:
    print "DAQmx Error: %s"%err
except Exception as err:
    print 'error was : {}'.format(err.message)
finally:
    if taskHandle:
        # DAQmx Stop Code
        DAQmxStopTask(taskHandle)
        DAQmxClearTask(taskHandle)
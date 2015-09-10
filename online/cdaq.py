from PyDAQmx import *
import numpy
import matplotlib.pyplot as plt

# Declaration of variable passed by reference
taskHandle = TaskHandle()
read = int32()
num_samples = 500
data = numpy.zeros((num_samples,2), dtype=numpy.float64)
print 'num samples: {}'.format(data.size)

try:
    # DAQmx Configure Code
    DAQmxCreateTask("",byref(taskHandle))
    DAQmxCreateAIVoltageChan(taskHandle,"emg/ai0, emg/ai2","",DAQmx_Val_RSE ,-5.0,5.0,DAQmx_Val_Volts,None)
    #DAQmxCreateAICurrentChan(taskHandle, "emg/ai1", "", DAQmx_Val_Cfg_Default, -5.0 ,5.0, DAQmx_Val_Volts, None)
    DAQmxCfgSampClkTiming(taskHandle,"",500.0,DAQmx_Val_Rising,DAQmx_Val_ContSamps,data.size)

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
        DAQmxReadAnalogF64(taskHandle,data.shape[0],10.0,DAQmx_Val_GroupByChannel,data,data.size,byref(read),None)
        print 'after', data.shape
        print 'edited'

        if condata is None:
            condata = data
        #elif condata.shape[0] == 1000:
        #    condata[:750] = condata[250:]
        #    condata[750:] = data
        else:
            condata = numpy.row_stack((condata, data))
        #    plt.clf()
        #plt.plot(condata)
        #plt.draw()
        
    fig, axes = plt.subplots(data.shape[1], 1, figsize=(30,12))
    for i in range(data.shape[1]):
        axes[i].set_ylim([-5, 5])
        axes[i].plot(condata[:,i])
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
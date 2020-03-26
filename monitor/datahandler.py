import time
from threading import Thread
import numpy as np
from .databackend import DataBackend, DataBackendHandler

class TimeDataInputManager:
    def __init__(self, arraysize, data_range):
        self.ymin,self.ymax=data_range
        self.arraysize=arraysize
        self.data=np.arange(self.ymin,self.ymax, (self.ymax-self.ymin)/self.arraysize)
    def get_range(self):
        return (self.ymin,self.ymax)

class DataInputs:

    class Handler(DataBackendHandler):
        def __init__(self, parent):
            self.parent=parent

        def update_settings(self, **kwargs):
            if kwargs is not None:
                for key, value in kwargs.iteritems():
                    if(hasattr(selfi.parent,key)):
                        oldval=getattr(self.parent,key)
                        if oldval != value:
                            self.parent.changed=True
                        setattr(self.parent,key,value)
    
        def update_timedata(self,timestamp, pressure, flow, volume):
            self.parent.make_index(timestamp)
            self.parent.pressure.data[self.parent.index]=pressure
            self.parent.flow.data[self.parent.index]=flow
            self.parent.volume.data[self.parent.index]=volume
    
    def __init__(self, xmax, freq):
        Thread.__init__(self)
        self.running=True
        
        self.fio=0
        self.pep=0
        self.fr=0
        self.vm=0.0
        self.vte=0

        self.changed=False
        self.handler = DataInputs.Handler(self)
        
        self.index=0
        self.index_zero_time = 0

        self.xmax=xmax
        self.freq=freq
        self.arraysize=xmax*freq

        self.pressure=TimeDataInputManager(self.arraysize, (-30,105))
        self.flow=TimeDataInputManager(self.arraysize, (-100,100))
        self.volume=TimeDataInputManager(self.arraysize, (0,500))

    
    def settings_changed(self,reset=True):
        val = self.changed
        self.changed=False
        return val

    def get_index(self):
        return self.index

    def make_index(self,timestamp):
        if(timestamp-self.index_zero_time > self.xmax):
            self.index=0
            self.index_zero_time=timestamp
        else:
            diff=timestamp-self.index_zero_time
            self.index=int(diff*self.freq)
    

class DataOutputManager:

    def __init__(self, backend, key, vmin=0, vmax=100, default=0):
        self.vmin=vmin
        self.vmax=vmax
        self.value=default
        self.backend=backend
        self.key=key

    def update(self,value):
        self.value=value
        self.backend.set_setting(self.key,value)


class DataOutputs:

    def __init__(self, backend):
        self.backend=backend
        self.fio2=DataOutputManager(backend,backend.FIO2,default=22)
        self.pep=DataOutputManager(backend,backend.FIO2,default=10)
        self.fr=DataOutputManager(backend,backend.FIO2,default=22)
        self.flow=DataOutputManager(backend,backend.FIO2,0.0,30.0,6.0)
        self.vt=DataOutputManager(backend,backend.FIO2,0,1000,370)

class DataHandler():

    def __init__(self,backend):
        Thread.__init__(self)
        self.backend=backend
        self.inputs=None
        self.outputs=DataOutputs(backend)

    def init_inputs(self, xmax, freq):
        self.inputs=DataInputs(xmax,freq)
        self.backend.set_handler(self.inputs.handler)


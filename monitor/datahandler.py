import time
from threading import Thread
import numpy as np

class DataInputManager:
    def __init__(self, arraysize, data_range):
        self.ymin,self.ymax=data_range
        self.arraysize=arraysize
        self.data=np.arange(self.ymin,self.ymax, (self.ymax-self.ymin)/self.arraysize)
    def get_range(self):
        return (self.ymin,self.ymax)

class DataInputs:
    def __init__(self, xmax, freq, pressure_range, flow_range, volume_range):
        Thread.__init__(self)
        self.running=True
        self.index=0
        self.index_zero_time = 0

        self.xmax=xmax
        self.freq=freq
        self.arraysize=xmax*freq

        self.pressure=DataInputManager(self.arraysize, pressure_range)
        self.flow=DataInputManager(self.arraysize, flow_range)
        self.volume=DataInputManager(self.arraysize, volume_range)

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

    def __init__(self, vmin=0, vmax=100, default=0):
        self.vmin=vmin
        self.vmax=vmax
        self.value=default

    def update(self,value):
        self.value=value


class DataOutputs:

    def __init__(self):
        self.fio2=DataOutputManager(default=22)
        self.pep=DataOutputManager(default=10)
        self.fr=DataOutputManager(default=22)
        self.flow=DataOutputManager(0.0,30.0,6.0)
        self.vt=DataOutputManager(0,1000,370)

class DataHandler(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.inputs=None
        self.outputs=DataOutputs()
        self.running=False

    def stop(self):
        self.running=False

class DataHandlerDummy(DataHandler):

    def run(self):

        self.running=True
        while self.running:
            self.inputs.make_index(time.time())
            time.sleep(1.0/40)
            v = np.random.rand(4)
            if v[3] > 0.03:
                self.inputs.pressure.data[self.inputs.index]=0
                self.inputs.flow.data[self.inputs.index]=0
                self.inputs.volume.data[self.inputs.index]=0
            else:
                self.inputs.pressure.data[self.inputs.index]=self.inputs.pressure.ymax*v[0]
                self.inputs.flow.data[self.inputs.index]=self.inputs.flow.ymax*v[1]
                self.inputs.volume.data[self.inputs.index]=self.inputs.volume.ymax*v[2]

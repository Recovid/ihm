import time
from threading import Thread
import numpy as np

class DataInputManager:
    def __init__(self, arraysize, data_range):
        self.ymin,self.ymax=data_range
        self.arraysize=arraysize
        self.data=np.arange(self.ymin,self.ymax, (self.ymax-self.ymin)/self.arraysize)

class DataHandler(Thread):

    def __init__(self, xmax, freq, pressure_range, flow_range, volume_range):
        Thread.__init__(self)
        self.running=True
        self.index=0
        self.index_zero_time = 0
        
        self.xmax=xmax
        self.freq=freq
        self.arraysize=xmax*freq

        self.pressure_manager=DataInputManager(self.arraysize, pressure_range)
        self.flow_manager=DataInputManager(self.arraysize, flow_range)
        self.volume_manager=DataInputManager(self.arraysize, volume_range)
    
    def get_data(self):
        return [self.pressure_manager.data,self.flow_manager.data,self.volume_manager.data]

    def get_index(self):
        return self.index

    def make_index(self,timestamp):
        if(timestamp-self.index_zero_time > self.xmax):
            self.index=0
            self.index_zero_time=timestamp
        else:
            diff=timestamp-self.index_zero_time
            self.index=int(diff*self.freq)
    def stop(self):
        self.running=False

class DataHandlerDummy(DataHandler):

    def __init__(self, xmax, freq, pressure_range, flow_range, volume_range):
        DataHandler.__init__(self, xmax, freq, pressure_range, flow_range, volume_range)

    def run(self):

        while self.running:
            self.make_index(time.time())
            time.sleep(1.0/40)
            v = np.random.rand(4)
            if v[3] > 0.03:
                self.pressure_manager.data[self.index]=0
                self.flow_manager.data[self.index]=0
                self.volume_manager.data[self.index]=0
            else:
                self.pressure_manager.data[self.index]=self.pressure_manager.ymax*v[0]
                self.flow_manager.data[self.index]=self.flow_manager.ymax*v[1]
                self.volume_manager.data[self.index]=self.volume_manager.ymax*v[2]

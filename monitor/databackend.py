
import time
from threading import Thread
import numpy as np

class DataBackendHandler:
    def update_timedata(self,timestamp, pressure, flow, volume):
        pass

    def update_inputs(self, **kwargs):
        pass


class DataBackend(Thread):
    PEP="pep"
    FIO2="fio2"
    VT="vt"
    FR="fr"
    FLOW="flow"
    TPLAT="tplat"
    VTE="vte"
    PPLAT="pplat"
    PCRETE="pcrete"
    TPLAT="TPLAT"
    VM="VM"

    def __init__(self):
        Thread.__init__(self)

        self.running=False

        self.settings={}
        self.settings[type(self).FIO2]=0
        self.settings[type(self).VT]=0
        self.settings[type(self).FR]=0
        self.settings[type(self).PEP]=0
        self.settings[type(self).FLOW]=0
        self.settings[type(self).TPLAT]=0

    def set_handler(self, handler):
        self.handler=handler

    def set_setting(self, key, value):
        if(key in self.settings):
            self.settings[key]=value
            print(str(key), str(value))

    def stop(self):
        self.running=False

class DataBackendDummy(DataBackend):
   
    def __init__(self, pmax, fmax, vmax):
        DataBackend.__init__(self)
        self.pmax=pmax
        self.fmax=fmax
        self.vmax=vmax


    def run(self):
        self.running=True
        while self.running:
            time.sleep(1.0/40)
            v = np.random.rand(4)
            if v[3] > 0.03:
                self.handler.update_timedata(time.time(),0,0,0)
            else:
                self.handler.update_timedata(time.time(),v[0]*self.pmax,v[1]*self.fmax,v[2]*self.vmax)

    def set_setting(self, key, value):
        if(key in self.settings):
            self.settings[key]=value
            print(str(key), str(value))
            if(key==self.PEP):
                self.handler.update_inputs(**{self.PEP:value})
            elif(key==self.FIO2):
                self.handler.update_inputs(**{self.FIO2:value})
            elif(key==self.VT):
                self.handler.update_inputs(**{self.VTE:value})
            elif(key==self.FR):
                self.handler.update_inputs(**{self.FR:value})
            elif(key==self.FLOW):
                self.handler.update_inputs(**{self.PCRETE:value})
            elif(key==self.TPLAT):
                self.handler.update_inputs(**{self.PPLAT:value})

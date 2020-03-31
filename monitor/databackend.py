
# -*- coding: utf-8 -*-
import time
from threading import Thread
import numpy as np
import re

class DataBackendHandler:
    def update_timedata(self,timestamp, pressure, flow, volume):
        pass

    def update_inputs(self, **kwargs):
        pass


class DataBackend(Thread):
    PEP="pep"
    PEP_ALARM="pep_alarm"
    FIO2="fio2"
    VT="vt"
    FR="fr"
    FLOW="flow"
    TPLAT="tplat"
    VTE="vte"
    VTE_ALARM="vte_alarm"
    VMIN="vmin"
    PPLAT="pplat"
    PCRETE="pcrete"
    PCRETE_ALARM="pcrete_alarm"
    PMAX="pmax"
    PMIN="pmin"
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
        self.settings[type(self).PMIN]=0
        self.settings[type(self).PMAX]=0
        self.settings[type(self).VMIN]=0

    def set_handler(self, handler):
        self.handler=handler

    def set_setting(self, key, value):
        if(key in self.settings):
            self.settings[key]=value
            print(str(key), str(value))

    def stop_exp(self, on):
        print("Pause expi "+str(on))
    def stop_ins(self, on):
        print("Pause inspi "+str(on))

    def stop(self):
        self.running=False

class DataBackendFromFile(DataBackend):
    def __init__(self, inputFile):
        DataBackend.__init__(self)
        self.inputFile = inputFile

    def run(self):
        framePattern = re.compile("DATA msec:(.....) Vol_:(...) Deb_:(....) Paw_:(....) Fi02:(...) Vt__:(....) FR__:(..) PEP_:(..) DebM:(..) CS8_:(..)")
        self.running=True
        prevTimestamp = 0
        toAdd = 0
        with open(self.inputFile, "r") as f:
            line = f.readline()
            while line:
                time.sleep(1.0/40)
                res = framePattern.match(line)
                if res:
                    timestamp = int(res.group(1))
                    if prevTimestamp > timestamp:
                        toAdd += 100
                    self.handler.update_timedata(toAdd + timestamp / 1000, int(res.group(4)), int(res.group(3)), int(res.group(2)))
                    prevTimestamp = timestamp
                line = f.readline()

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
                self.handler.update_inputs(**{self.PEP:value,self.PEP_ALARM:value>10 })
            elif(key==self.FIO2):
                self.handler.update_inputs(**{self.FIO2:value})
            elif(key==self.VT):
                self.handler.update_inputs(**{self.VTE:value, self.VTE_ALARM:value<100})
            elif(key==self.FR):
                self.handler.update_inputs(**{self.FR:value})
            elif(key==self.FLOW):
                self.handler.update_inputs(**{self.PCRETE:value,self.PCRETE_ALARM:value>80})
            elif(key==self.TPLAT):
                self.handler.update_inputs(**{self.PPLAT:value})

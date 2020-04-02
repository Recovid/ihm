
# -*- coding: utf-8 -*-
import time
from threading import Thread
import numpy as np
import re
from .communication import *
from .data import Data
#import serial

class DataBackendHandler:
    def update_timedata(self,timestamp, pressure, flow, volume):
        pass

    def update_inputs(self, **kwargs):
        pass


class DataBackend(Data, Thread):
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

    def stop_exp(self, time):
        print("Pause expi "+str(time))
    def stop_ins(self, time):
        print("Pause inspi "+str(time))

    def stop(self):
        self.running=False

class DataBackendFromFile(DataBackend):
    def __init__(self, inputFile):
        DataBackend.__init__(self)
        self.inputFile = inputFile

    def run(self):
        self.running=True
        prevTimestamp = 0
        toAdd = 0
        with open(self.inputFile, "r") as f:
            for line in f:
                msg = parse_msg(line)
                if isinstance(msg, DataMsg):
                    timestamp = msg.timestamp_ms
                    if prevTimestamp > timestamp:
                        toAdd += 100
                    else: # do not wait when the timestamp overflow
                        time.sleep((timestamp - prevTimestamp)/1000)
                    self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                    prevTimestamp = timestamp
                elif isinstance(msg, RespMsg):
                    self.handler.update_inputs(**{
                        self.FIO2: msg.fio2_pct,
                        self.VT: msg.vt_ml,
                        self.FR: msg.fr_pm,
                        self.PEP: msg.pep_mbar,
                        self.PCRETE: msg.pep_mbar,
                        self.PPLAT: msg.pplat_mbar,
                    })

    def set_setting(self, key, value):
        pass # settings do nothing for a trace file

class SerialPortMock(DataBackend):
    def __init__(self, inputPipe, outputPipe):
        DataBackend.__init__(self)
        self.inputPipe = inputPipe
        self.outputPipe = open(outputPipe, "w")

    def run(self):
        self.running=True
        prevTimestamp = 0
        toAdd = 0
        with open(self.inputPipe, "r") as f:
            for line in f:
                msg = parse_msg(line)
                if isinstance(msg, DataMsg):
                    timestamp = msg.timestamp_ms
                    if prevTimestamp > timestamp:
                        toAdd += 100
                    self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                    prevTimestamp = timestamp
                elif isinstance(msg, RespMsg):
                    self.handler.update_inputs(**{
                        self.FIO2: msg.fio2_pct,
                        self.VT: msg.vt_ml,
                        self.FR: msg.fr_pm,
                        self.PEP: msg.pep_mbar,
                        self.PCRETE: msg.pep_mbar,
                        self.PPLAT: msg.pplat_mbar,
                    })

    def set_setting(self, key, value):
        msg = SetMsg(key, value)
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

'''
class SerialPort(DataBackend):
    def __init__(self, tty):
        DataBackend.__init__(self)
        self.serialPort = serial.Serial(tty, 9600)

        serialPort.write(test_string)
        serialPort.read(bytes_sent)

    def run(self):
        self.running=True
        prevTimestamp = 0
        toAdd = 0
        for line in serial: # replace with serial.readline() if it fails
            msg = parse_msg(line)
            if isinstance(msg, DataMsg):
                timestamp = msg.timestamp_ms
                if prevTimestamp > timestamp:
                    toAdd += 100
                self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                prevTimestamp = timestamp
            elif isinstance(msg, RespMsg):
                self.handler.update_inputs(**{
                    self.FIO2: msg.fio2_pct,
                    self.VT: msg.vt_ml,
                    self.FR: msg.fr_pm,
                    self.PEP: msg.pep_mbar,
                    self.PCRETE: msg.pep_mbar,
                    self.PPLAT: msg.pplat_mbar,
                })

    def set_setting(self, key, value):
        msg = SetMsg(key, value)
        self.serial.write(serialize_msg(msg))
        self.serial.flush()
'''

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

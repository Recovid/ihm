
# -*- coding: utf-8 -*-
import time
from threading import Thread
import numpy as np
import re
from .communication import *
from .data import Data, SETTINGS
import serial
from datetime import datetime
from pathlib import Path
import tkinter as tk

class DataBackendHandler:
    def update_timedata(self,timestamp, pressure, flow, volume):
        pass

    def update_inputs(self, **kwargs):
        pass
    
    def received_setting(self, key, value):
        pass

class DataBackend(Data, Thread):
    def __init__(self):
        Thread.__init__(self)

        self.running=False
        self.settings = {setting.key: None for setting in SETTINGS.values()}

    def set_handler(self, handler):
        self.handler = handler

    def set_setting(self, key, value):
        if(key in self.settings):
            self.settings[key]=value
            print(str(key), str(value))

    def stop_exp(self, time_ms):
        print("Pause expi "+str(time_ms))
    def stop_ins(self, time_ms):
        print("Pause inspi "+str(time_ms))
    def pause_bip(self, time_ms):
        print("Pause bip "+str(time_ms))

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
                if not self.running:
                    break
                msg = parse_msg(line)
                if isinstance(msg, DataMsg):
                    timestamp = msg.timestamp_ms
                    if prevTimestamp > timestamp:
                        toAdd += 1000
                    else: # do not wait when the timestamp overflow
                        time.sleep((timestamp - prevTimestamp)/1000)
                    self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                    prevTimestamp = timestamp
                elif isinstance(msg, RespMsg):
                    self.handler.update_inputs(**{
                        self.IE: msg.ie_ratio,
                        self.FR: msg.fr_pm,
                        self.VTE: msg.vte_ml,
                        self.PCRETE: msg.pcrete_cmH2O,
                        self.VM: msg.vm_lpm,
                        self.PPLAT: msg.pplat_cmH2O,
                        self.PEP: msg.pep_cmH2O,
                    })
                elif isinstance(msg, SetMsg):
                    self.handler.received_setting(msg.setting, int(msg.value))
                elif isinstance(msg, InitMsg):
                    # do we need to reset some settings ?
                    pass

    def set_setting(self, key, value):
        pass # settings do nothing for a trace file

class SerialPortMock(DataBackend):
    def __init__(self, inputPipe, outputPipe):
        DataBackend.__init__(self)
        self.inputPipe = inputPipe
        self.outputPipe = open(outputPipe, "w")
        msg = InitMsg("RecovidIHMV2")
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

    def run(self):
        self.running=True
        prevTimestamp = 0
        toAdd = 0
        with open(self.inputPipe, "r") as f:
            for line in f:
                if not self.running:
                    break
                msg = parse_msg(line)
                if isinstance(msg, DataMsg):
                    timestamp = msg.timestamp_ms
                    if prevTimestamp > timestamp:
                        toAdd += 1000
                    self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                    prevTimestamp = timestamp
                elif isinstance(msg, RespMsg):
                    self.handler.update_inputs(**{
                        self.IE: msg.ie_ratio,
                        self.FR: msg.fr_pm,
                        self.VTE: msg.vte_ml,
                        self.PCRETE: msg.pcrete_cmH2O,
                        self.VM: msg.vm_lpm,
                        self.PPLAT: msg.pplat_cmH2O,
                        self.PEP: msg.pep_cmH2O,
                    })
                elif isinstance(msg, SetMsg):
                    self.handler.received_setting(msg.setting, int(msg.value))
                elif isinstance(msg, InitMsg):
                    # do we need to reset some settings ?
                    pass

    def stop_exp(self, time_ms):
        msg = PauseExpMsg(time_ms)
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

    def stop_ins(self, time_ms):
        msg = PauseInsMsg(time_ms)
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

    def pause_bip(self, time_ms):
        msg = PauseBipMsg(time_ms)
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

    def set_setting(self, key, value):
        msg = SetMsg(key, value)
        self.outputPipe.write(serialize_msg(msg))
        self.outputPipe.flush()

def readTSI(self, dev, bdrate, startTime, tsiFile):
    samplesNb = 1000
    periodMs = 10
    ser = serial.Serial(dev, bdrate, timeout=10)
    command = "SSR" + str(periodMs).zfill(4)
    ser.write(command.encode())
    ser.write(b'\r')
    line = str(ser.readline())[2:][:-5]
    if line != 'OK':
        print("ERROR : TSI DIDN'T ACK COMMAND SET PERIOD TO", periodMs)
        return
    writeBuffer = b''
    while self.running:
        command = "DCFxx" + str(samplesNb).zfill(4)
        ser.write(command.encode())
        ser.write(b'\r')
        line = str(ser.readline())[2:][:-5]
        if line != 'OK':
            print("ERROR : TSI DIDN'T ACK COMMAND START MEASUREMENT")
            return
        if len(writeBuffer) > 20000:
            tsiFile.write(writeBuffer)
            writeBuffer = b''
        for counter in range(0, samplesNb):
            if not self.running:
                tsiFile.write(writeBuffer)
                tsiFile.flush()
                writeBuffer = b''
                print("End TSI Thread")
                return
            line = str(ser.readline())
            if len(line) > 0:
                Fslm_Tsi = float(line[2:][:-5])
                millis = int(round(time.time() * 1000) - startTime)
                writeBuffer += (str(millis) + "\t" + str(Fslm_Tsi) + "\n").encode("ascii")

class SimpleWDG(Thread):
    def __init__(self, trig_time, func):
        Thread.__init__(self)
        self.trig_time=trig_time
        self.func = func
        self.running = False
        self.start_time = None

    def run(self):
        self.running = True
        while self.running:
            if self.start_time is not None:
                if time.time()-self.start_time > self.trig_time:
                    self.func()
                    self.start_time=None
            time.sleep(self.trig_time/10.0)

    def stop(self):
        self.running = False

    def reset(self):
        self.start_time = time.time()

class SerialPort(DataBackend):
    def __init__(self, tty, app):
        DataBackend.__init__(self)
        self.serialPort = serial.Serial(tty, 115200, timeout=1)
        msg = InitMsg("RecovidIHMV2")
        try:
            self.serialPort.write(serialize_msg(msg).encode("ascii"))
            self.serialPort.flush()
        except:
            print("Exception when writting init message on the serial port")
        self.app = app

    def run(self):
        self.running=True
        self.wdg = SimpleWDG(5,lambda: self.handler.alarmPerteCtrl(True))
        self.wdg.start()
        prevTimestamp = 0
        toAdd = 0
        writeBuffer = b''
        basename = str(Path.home()) + datetime.now().strftime("/%Y%m%d_%H%M%S")
        startTime = int(round(time.time() * 1000))
        tsiFound = Path('/dev/ttyUSB0').exists()
        if tsiFound:
           tsiFile = open(basename + "_tsi.log", "wb")
           thread_tsi = Thread(target=readTSI, args=(self, '/dev/ttyUSB0', 38400, startTime, tsiFile))
           thread_tsi.start()


        with open(basename + ".log", "wb") as logFile:
            while self.running:
                line = self.serialPort.readline()
                if len(line)>0 :
                    if len(writeBuffer) > 20000:
                        logFile.write(writeBuffer)
                        writeBuffer = b''
                    millis = int(round(time.time() * 1000) - startTime)
                    writeBuffer += (str(millis) + "\t").encode("ascii") + (line)
                    try:
                        line = line.decode("ascii")
                    except:
                        print("Exception when decoding the line in the serial port")
                    else :
                        self.handler.alarmPerteCtrl(False)
                        msg = parse_msg(line)
                        self.wdg.reset()
                        if isinstance(msg, DataMsg):
                            timestamp = msg.timestamp_ms
                            if prevTimestamp > timestamp:
                                toAdd += 1000
                            self.handler.update_timedata(toAdd + timestamp / 1000, msg.paw_mbar, msg.debit_lpm, msg.volume_ml)
                            prevTimestamp = timestamp
                        elif isinstance(msg, RespMsg):
                            self.handler.update_inputs(**{
                                self.IE: msg.ie_ratio,
                                self.FR: msg.fr_pm,
                                self.VTE: msg.vte_ml,
                                self.PCRETE: msg.pcrete_cmH2O,
                                self.VM: msg.vm_lpm,
                                self.PPLAT: msg.pplat_cmH2O,
                                self.PEP: msg.pep_cmH2O,
                            })
                        elif isinstance(msg, SetMsg):
                            self.handler.received_setting(msg.setting, int(msg.value))
                        elif isinstance(msg, AlarmMsg):
                            self.handler.received_alarm(msg.getAlarms())
                        elif isinstance(msg, InitMsg):
                            # do we need to reset some settings ?
                            pass
            logFile.write(writeBuffer)
            logFile.flush()
            writeBuffer = b''
        self.wdg.stop()
        self.wdg.join()
        if tsiFound:
            thread_tsi.join()
        print("fin thread serial")

    def stop_exp(self, time_ms):
        msg = PauseExpMsg(time_ms)
        try:
            self.serialPort.write(serialize_msg(msg).encode("ascii"))
            self.serialPort.flush()
        except:
            print("Exception when writting Pause exp message on the serial port")

    def stop_ins(self, time_ms):
        msg = PauseInsMsg(time_ms)
        try:
            self.serialPort.write(serialize_msg(msg).encode("ascii"))
            self.serialPort.flush()
        except: 
            print("Exception when writting Pause insp message on the serial port")

    def pause_bip(self, time_ms):
        msg = PauseBipMsg(time_ms)
        try:
            self.serialPort.write(serialize_msg(msg).encode("ascii"))
            self.serialPort.flush()
        except:
            print("Exception when writting Pause bip message on the serial port")

    def set_setting(self, key, value):
        msg = SetMsg(key, value)
        try:
            self.serialPort.write(serialize_msg(msg).encode("ascii"))
            self.serialPort.flush()
        except:
            print("Exception when writting Set setting message on the serial port")

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
            elif(key==self.VT):
                self.handler.update_inputs(**{self.VTE:value, self.VTE_ALARM:value<100})
            elif(key==self.FR):
                self.handler.update_inputs(**{self.FR:value})
            elif(key==self.FLOW):
                self.handler.update_inputs(**{self.PCRETE:value,self.PCRETE_ALARM:value>80})
            elif(key==self.IE):
                self.handler.update_inputs(**{self.IE:value})

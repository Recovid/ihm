# -*- coding: utf-8 -*-
import time
import numpy as np
from .databackend import DataBackend, DataBackendHandler
from .data import SETTINGS
from collections import deque
from copy import deepcopy
from .alarms import AlarmType

class TimeDataInputManager:
    def __init__(self, arraysize, data_range):
        self.ymin,self.ymax=data_range
        self.arraysize=arraysize
        self.data=np.arange(self.ymin,self.ymax, (self.ymax-self.ymin)/self.arraysize)
    def get_range(self):
        return (self.ymin,self.ymax)

class DataInputs:
   
    def __init__(self, xmax, freq):
        self.running=True
        
        self.inputs = {}
        self.inputs[DataBackend.MAXPAW]=0
        self.inputs[DataBackend.TIME]=0
        self.inputs[DataBackend.IE]=0
        self.inputs[DataBackend.PEP]=0
        self.inputs[DataBackend.PEP_ALARM]=False
        self.inputs[DataBackend.FR]=0
        self.inputs[DataBackend.PPLAT]=0
        self.inputs[DataBackend.VM]=0
        self.inputs[DataBackend.PCRETE]=0
        self.inputs[DataBackend.PCRETE_ALARM]=False
        self.inputs[DataBackend.VTE]=0
        self.inputs[DataBackend.VTE_ALARM]=False

        self.changed=False
        
        self.index=0
        self.index_zero_time = 0
        self.freeze=False
        self.unfreeze=False
        self.xmax=xmax
        self.freq=freq
        self.arraysize=xmax*freq

        self.pressure=TimeDataInputManager(self.arraysize, (-20,100))
        self.flow=TimeDataInputManager(self.arraysize, (-80,80))
        self.volume=TimeDataInputManager(self.arraysize, (0,600))

    
    def settings_changed(self,reset=True):
        val = self.changed
        self.changed=False
        return val

    def get_index(self):
        return self.index

    def make_index(self,timestamp):
        if(timestamp-self.index_zero_time >= self.xmax or self.unfreeze):
            self.index=0
            self.index_zero_time=timestamp
            self.unfreeze=False
        else:
            diff=timestamp-self.index_zero_time
            self.index=int(diff*self.freq)
    def timedata_freeze(self, freeze=True):
        self.freeze=freeze
        self.unfreeze=True

class SettingManager():

    def __init__(self, controller, setting):
        self.vmin = setting.vmin
        self.vmax = setting.vmax
        self.step = setting.step
        self.bigStep = setting.bigStep
        self.default = setting.default
        self.key = setting.key
        self.value = setting.default
        self.controller = controller
        self.synchronized = False
        self.widget=None

    def change(self, value):
        # NB: go through the controller to ensure correct data management
        self.controller.change_setting(self.key, value)

    def sync(self):
        if(self.widget is not None):
            self.widget.refresh()

class DataController:

    class Handler(DataBackendHandler):
        def __init__(self, parent):
            self.parent=parent

        def update_inputs(self, **kwargs):
            self.parent.lastControllerDataTime = time.time()
            if kwargs is not None:
                for key, value in kwargs.items():
                    if(key in self.parent.inputs.inputs):
                        oldval=self.parent.inputs.inputs[key]
                        if oldval != value:
                            self.parent.inputs.changed=True
                            self.parent.inputs.inputs[key]=value
            # Assume that this function is only called when RESP is received/treated
            # (Only wrong with DatabackendDummy now)
            if len(self.parent.historyDataQueue) == 8:
                self.parent.historyDataQueue.popleft()
            self.parent.historyDataQueue.append(deepcopy(self.parent.inputs))
            self.parent.inputs.inputs[DataBackend.MAXPAW] = 0
            self.parent.checkHistoryForAlarms()
    
        def update_timedata(self,timestamp, pressure, flow, volume):
            self.parent.lastControllerDataTime = time.time()
            if pressure > self.parent.inputs.inputs[DataBackend.MAXPAW]:
                self.parent.inputs.inputs[DataBackend.MAXPAW] = pressure
            if not self.parent.inputs.freeze:
                prevIndex = self.parent.inputs.index
                prevPressure = self.parent.inputs.pressure.data[self.parent.inputs.index]
                prevFlow = self.parent.inputs.flow.data[self.parent.inputs.index]
                prevVolume = self.parent.inputs.volume.data[self.parent.inputs.index]

                self.parent.inputs.inputs[DataBackend.TIME] = timestamp
                self.parent.inputs.make_index(timestamp)

                index = self.parent.inputs.index
                dataLen = len(self.parent.inputs.pressure.data)
                if self.parent.inputs.index < prevIndex:
                    index += len(self.parent.inputs.pressure.data)
                # linear interpolation between prev and current index
                for idx in range(prevIndex + 1, index + 1):
                    coeff = (idx - prevIndex) / (self.parent.inputs.index - prevIndex)
                    self.parent.inputs.pressure.data[idx % dataLen] = coeff * pressure + (1 - coeff) * prevPressure
                    self.parent.inputs.flow.data[idx % dataLen] = coeff * flow + (1 - coeff) * prevFlow
                    self.parent.inputs.volume.data[idx % dataLen] = coeff * volume + (1 - coeff) * prevVolume

        def received_setting(self, key, value):
            self.parent.lastControllerDataTime = time.time()
            if key in self.parent.settings:
                if (key == DataBackend.IE):
                    value /= 10
                self.parent.settings[key].value = value
                self.parent.settings[key].synchronized = True
                self.parent.settings[key].sync()

        def received_alarm(self, alarmTab):
            if( isinstance(alarmTab, list)):
                for i in alarmTab:
                    self.parent.activeAlarms[i] = alarmTab[i]

        def alarmPerteCtrl(self, isActive):
            self.parent.activeAlarms[AlarmType.LOST_CPU] = isActive

 
    def __init__(self, backend, mainLoop):
        self.backend=backend
        self.mainLoop = mainLoop
        self.inputs=None
        self.repost_stop_exp = False
        self.repost_stop_ins = False
        self.repost_stop_exp_posted = False
        self.repost_stop_ins_posted = False
        self.historyDataQueue = deque()
        #calculate alarms are just to display the background of Mesure in red
        # 8 is to use the enum alarmtype
        self.calculateAlarms = [False] * 8
        self.activeAlarms = [False] * 16
        self.lastControllerDataTime = 0
        self.controllerAlarm = None

        self.reset_settings()

    def reset_settings(self):
        self.settings = {setting.key: SettingManager(self, setting) for setting in SETTINGS.values()}

    def init_inputs(self, xmax, freq):
        self.inputs=DataInputs(xmax,freq)
        self.handler = DataController.Handler(self)
        self.backend.set_handler(self.handler)
    
    def post_stop_exp(self, time_ms):
        # repost 100 msec before timeout end to avoid breath restart
        if self.repost_stop_exp:
            self.backend.stop_exp(500)
            self.mainLoop.after(time_ms - 100, self.post_stop_exp, time_ms)
        else:
            self.repost_stop_exp_posted = False

    def stop_exp(self, on):
        if (on):
            self.repost_stop_exp = True
            self.backend.stop_exp(500)
            if self.repost_stop_exp_posted == False: # if we don't already have a running timer
                self.repost_stop_exp_posted = True
                self.mainLoop.after(400, self.post_stop_exp, 500)
        else:
            self.backend.stop_exp(0)
            self.repost_stop_exp = False

    def post_stop_ins(self, time_ms):
        # repost 100 msec before timeout end to avoid breath restart
        if self.repost_stop_ins:
            self.backend.stop_ins(500)
            self.mainLoop.after(time_ms - 100, self.post_stop_ins, time_ms)
        else:
            self.repost_stop_ins_posted = False

    def stop_ins(self, on):
        if (on):
            self.repost_stop_ins = True
            self.backend.stop_ins(500)
            if self.repost_stop_ins_posted == False: # if we don't already have a running timer
                self.repost_stop_ins_posted = True
                self.mainLoop.after(400, self.post_stop_ins, 500)
        else:
            self.backend.stop_ins(0)
            self.repost_stop_ins = False

    def pause_bip(self):
        self.backend.pause_bip(120 * 1000)

    def change_setting(self, key, value):
        setting = self.settings[key]
        if setting.vmin <= value <= setting.vmax:
            setting.value = value
            setting.synchronized = False
            if (key == DataBackend.IE):
                value = int(value * 10)
            self.backend.set_setting(key, value)

    def get_setting(self, key):
        """
        Returns the local value of a setting and whether it is synchronized
        with the controller as a pair (value, synchronized). Values might be
        desynchronized during connection or when a new change is not acked yet.
        """
        return (self.settings[key].value, self.settings[key].value == self.backend.setings[key])

    def checkHistoryForAlarms(self):
        ## check the 8 last cycles data, from last one to older one
        ## switch to 0 when no need to check in older cycles
        Pmax_cycles = 2
        Pmin_startFailing = -1
        VTmin_cycles = 3
        VTmax_cycles = 3
        VMmin_cycles = 3
        PEPmax_cycles = 3
        PEPmin_cycles = 3
        for inp in reversed(self.historyDataQueue):
            if Pmax_cycles != 0:
                if inp.inputs[DataBackend.MAXPAW] >= max(self.settings[DataBackend.PMAX].value, inp.inputs[DataBackend.PEP] + 10):
                    Pmax_cycles -= 1
                    if Pmax_cycles == 0:
                        self.calculateAlarms[AlarmType.PRESSION_MAX] = True
                else:
                    Pmax_cycles = 0
                    self.calculateAlarms[AlarmType.PRESSION_MAX] = False
            if Pmin_startFailing != 0:
                if inp.inputs[DataBackend.PCRETE] <= max(self.settings[DataBackend.PMIN].value, inp.inputs[DataBackend.PEP] + 2):
                    if Pmin_startFailing == -1:
                        Pmin_startFailing = inp.inputs[DataBackend.TIME]
                    else:
                        if Pmin_startFailing - inp.inputs[DataBackend.TIME] > 15:
                            self.activeAlarms[AlarmType.PRESSION_MIN] = True
                else:
                    Pmin_startFailing = 0
                    self.calculateAlarms[AlarmType.PRESSION_MIN] = False
            if VTmin_cycles != 0:
                if inp.inputs[DataBackend.VTE] <= self.settings[DataBackend.VTMIN].value:
                    VTmin_cycles -= 1
                    if VTmin_cycles == 0:
                        self.calculateAlarms[AlarmType.VOLUME_COURANT_MIN] = True
                else:
                    VTmin_cycles = 0
                    self.calculateAlarms[AlarmType.VOLUME_COURANT_MIN] = False
            if VTmax_cycles != 0:
                if inp.inputs[DataBackend.VTE] >= self.settings[DataBackend.VTMAX].value:
                    VTmax_cycles -= 1
                    if VTmax_cycles == 0:
                        self.calculateAlarms[AlarmType.VOLUME_COURANT_MAX] = True
                else:
                    VTmax_cycles = 0
                    self.calculateAlarms[AlarmType.VOLUME_COURANT_MAX] = False
            if VMmin_cycles != 0:
                if inp.inputs[DataBackend.VM] <= self.settings[DataBackend.VMMIN].value:
                    VMmin_cycles -= 1
                    if VMmin_cycles == 0:
                        self.calculateAlarms[AlarmType.VOLUME_MINUTE] = True
                else:
                    VMmin_cycles = 0
                    self.calculateAlarms[AlarmType.VOLUME_MINUTE] = False
            if PEPmax_cycles != 0:
                if inp.inputs[DataBackend.PEP] >= self.settings[DataBackend.PEP].value + 2:
                    PEPmax_cycles -= 1
                    if PEPmax_cycles == 0:
                        self.calculateAlarms[AlarmType.PEP_MAX] = True
                else:
                    PEPmax_cycles = 0
                    self.calculateAlarms[AlarmType.PEP_MAX] = False
            if PEPmin_cycles != 0:
                if inp.inputs[DataBackend.PEP] <= self.settings[DataBackend.PEP].value - 2:
                    PEPmin_cycles -= 1
                    if PEPmin_cycles == 0:
                        self.calculateAlarms[AlarmType.PEP_MIN] = True
                else:
                    PEPmin_cycles = 0
                    self.calculateAlarms[AlarmType.PEP_MIN] = False

    def GetAlarmState(self, alarmtype):
        return self.activeAlarms[alarmtype]

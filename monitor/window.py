# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datacontroller import DataController
from .databackend import DataBackend, DataBackendDummy, DataBackendFromFile, SerialPortMock
from .userinputs import OneValueDialog, LockScreen, PowerSettingsDialog
from .knob import Knob
from .mesure import Mesure
from .button import Button2, ButtonPR
from .alarms import AlarmType, AlarmState, AlarmLevel, Alarm, AlarmManager
from .data import Data
import config


class Scope:
    def __init__(self, ax, title, ylabel, xlim, xstep, handler):

        self.handler=handler
        self.xstep=xstep
        self.ax=ax
        self.ax.set_ylabel(title+'\n'+ylabel)
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(self.handler.get_range())

        self.tdata=np.arange(xlim[0], xlim[1], xstep)

        self.line_a = matplotlib.lines.Line2D(self.tdata, self.handler.data)
        self.line_b = matplotlib.lines.Line2D(self.tdata, self.handler.data)
        self.ax.add_line(self.line_a)
        self.ax.add_line(self.line_b)

        self.marker_ann = self.ax.text(0,0,'')
        
        self.line_m = matplotlib.lines.Line2D([0,0], self.handler.get_range())
        self.ax.add_line(self.line_m)

    def update(self, index, delta_marker=None):
        self.iterator=index
        self.line_a.set_data(self.tdata[0:self.iterator], self.handler.data[0:self.iterator])
        diff = len(self.tdata) - self.iterator
        if diff > 10:
            indx_b = self.iterator + 10
        else:
            indx_b = len(self.tdata)-1
        self.line_b.set_data(self.tdata[indx_b:len(self.tdata)-1], self.handler.data[indx_b:len(self.tdata)-1])
       
        index_marker=0
        refresh_marker=False
        if delta_marker is not None:
            refresh_marker=True
            index_marker=index-delta_marker
            self.marker_ann.set_position((index_marker*self.xstep,self.handler.data[index_marker]))
            self.marker_ann.set_text("%.2f" % self.handler.data[index_marker])
        elif self.marker_ann.get_text() != '':
            refresh_marker=True
            self.marker_ann.set_text('')
        if refresh_marker:
            self.line_m.set_data([index_marker*self.xstep,index_marker*self.xstep], self.handler.get_range())
            return self.line_a, self.line_b, self.line_m, self.marker_ann
        else:
            return self.line_a, self.line_b

class Window:
    
    def __init__(self, fullscreen = False, mock = False):
        self.timewindow=15
        self.freq=50
        self.timeresolution=1.0/self.freq

        self.app = tk.Tk()

        self.app.protocol("WM_DELETE_WINDOW", self.app.quit)
        if(fullscreen):
            self.app.attributes("-fullscreen", True)
        self.ws = 800
        self.hw = 480
        self.app.geometry("%dx%d"% (self.ws , self.hw))
        
        print('ws:',self.ws,' hw:',self.hw)

        self.app.wm_title("Recovid")
        for i in range(6):
            tk.Grid.rowconfigure(self.app, i, weight=1, minsize=self.hw/6 if i>0 else self.hw/6/2)
        for i in range(9):
            tk.Grid.columnconfigure(self.app, i, weight=1, minsize=self.ws/9)
        
        #self.data_backend = DataBackendDummy(100,100,500)
        if (mock):
            self.data_backend = SerialPortMock("in", "out")
        else:
            self.data_backend = DataBackendFromFile("tests/nominal_cycle.txt")
        self.data_controller = DataController(self.data_backend, self.app)
        self.data_controller.init_inputs(self.timewindow,self.freq)
        
        #TITLE
        self.title_frame = tk.Frame(self.app, \
            bg='#4E69AB').grid(row=0,column=0,columnspan=9)
        self.title = tk.Label(self.title_frame, font=("Helvetica", -int(self.hw*0.05)),text='RECOVID', \
            anchor='n', fg='white',bg='#4E69AB').grid(row=0,column=0, columnspan=2, sticky="news")
        
        self.alarm_text = tk.StringVar()
        self.alarm_text.set("Some Alarm message text")
        self.alarmMgr = AlarmManager()
        self.alarm_msg = tk.Label(self.title_frame, font=("Helvetica", -int(self.hw*0.05)), textvariable = self.alarm_text, \
            anchor='n', fg='white',bg='#4E69AB').grid(row=0, column=2, columnspan=7, sticky="news")


        #VALEURS A Droite
 
        self.m_ie = Mesure(self.app,0, 'I/E', is_frac=True)
        self.m_ie.grid(row=1, column=6, sticky="senw", padx=2, pady=2)

        self.m_pep = Mesure(self.app,0,'PEP','cmH2O')
        self.m_pep.grid(row=1,column=7, sticky="senw", padx=2, pady=2)

        self.m_fr = Mesure(self.app,0,'FR','/min', dmin=self.data_controller.settings[Data.FRMIN])
        self.m_fr.grid(row=2,column=6, sticky="senw", padx=2, pady=2)

        self.m_pplat = Mesure(self.app,0,'Pplat','cmH2O')
        self.m_pplat.grid(row=2,column=7, sticky="senw", padx=2, pady=2)

        self.m_vm = Mesure(self.app,0,'VM','L/min', dmin=self.data_controller.settings[Data.VMMIN])
        self.m_vm.grid(row=3,column=6, sticky="senw", padx=2, pady=2)
        
        self.m_pcrete = Mesure(self.app,0,'Pcrete','cmH2O', dmin=self.data_controller.settings[Data.PMIN], dmax=self.data_controller.settings[Data.PMAX])
        self.m_pcrete.grid(row=3,column=7, sticky="senw", padx=2, pady=2)

        self.m_vte = Mesure(self.app,0,'VTe','mL', dmin=self.data_controller.settings[Data.VTMIN])
        self.m_vte.grid(row=4,column=6, sticky="senw", padx=2, pady=2)

        #BOUTONS EN BAS
        self.leftside = tk.Frame(self.app, height=200)
        self.leftside.grid(row=1, column=0,rowspan=7, columnspan = 6,sticky="news")

        self.knob_frame = tk.Frame(self.leftside,bg='#c9d2e5',width=int(self.ws*0.1),\
            height=int(self.hw*0.9))
        self.knob_frame.pack(side=tk.BOTTOM, fill=tk.X,expand=1)

        tk.Grid.rowconfigure(self.knob_frame, 1, weight=1)
        for column_index in range(5):
            tk.Grid.columnconfigure(self.knob_frame, column_index, weight=1)
            if(column_index == 0 ):
                self.k_vt = Knob(self.knob_frame, self.data_controller.settings[Data.VT],'ml','VT', '100', '600')
                self.k_vt.canvas.grid(row=1,column=column_index, sticky="news")
            if(column_index == 1  ):
                self.k_fr = Knob(self.knob_frame, self.data_controller.settings[Data.FR],'bpm','FR', '12', '35')
                self.k_fr.canvas.grid(row=1,column=column_index, sticky="news")
            if(column_index == 2):
                self.k_pep = Knob(self.knob_frame, self.data_controller.settings[Data.PEP],'cmH2O','PEP', '5','20')
                self.k_pep.canvas.grid(row=1,column=column_index, sticky="news")
            if(column_index == 3):
                self.k_flow = Knob(self.knob_frame, self.data_controller.settings[Data.FLOW],'L/min','Debit Max', '20', '60')
                self.k_flow.canvas.grid(row=1,column=column_index, sticky="news")
            if(column_index == 4):
                self.k_tplat = Knob(self.knob_frame, self.data_controller.settings[Data.TPLAT],'','Tplat','0,1', '1,0')
                self.k_tplat.canvas.grid(row=1,column=column_index, sticky="news")

        #Boutons Droite
        
        #Frame utilisé pour coloriser le backgroud de la colonne 8
        self.btn_frame = tk.Frame(self.app,bg='#c9d2e5',width=int(self.ws*0.1),\
            height=int(self.hw*0.9)).grid(column=8,row=1,rowspan=5,sticky="news")

        self.bt_Alarm = Button2(self.app,"monitor/Alarms_Icon/Icon_High_Priority.png")
        self.bt_Alarm.grid(row=1, column=8, sticky="news", padx=4, pady=2)
        self.bt_Alarm.bind('<ButtonRelease-1>', self.event_bt_Alarm, '+')

        self.bt_si = Button2(self.app,"Pause Inspi")
        self.bt_si.grid(row=2,column=8, sticky="senw", padx=4, pady=2)
        self.bt_si.bind('<ButtonPress-1>',self.stop_ins_event,'+')
        self.bt_si.bind('<ButtonRelease-1>',self.stop_ins_event,'+')

        self.bt_se = Button2(self.app ,"Pause Expi")
        self.bt_se.grid(row=3,column=8, sticky="senw", padx=4, pady=2)
        self.bt_se.bind('<ButtonPress-1>',self.stop_exp_event,'+')
        self.bt_se.bind('<ButtonRelease-1>',self.stop_exp_event,'+')
       
        self.bt_pset=Button2(self.app, "monitor/Alarms_Icon/power_settings.png")
        self.bt_pset.grid(row=4,column=8)
        self.bt_pset.bind('<ButtonPress-1>', self.pset_event, '+')
        self.bt_pset.bind('<ButtonRelease-1>', self.pset_event, '+')
        
        self.bt_freeze = ButtonPR(self.app,"Geler\ncourbes", "Resume")
        self.bt_freeze.grid(row=5,column=8,sticky="news", padx=4, pady=2)
        self.bt_freeze.bind('<Button-1>', self.event_bt_freeze,'+')

        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=4,column=7)
        self.app.bind('<Control-q>', lambda event: self.app.quit())

        #Graph Init 

        self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1,figsize=(3,4))
        self.fig_graph.tight_layout()
        self.xlim=(0,self.timewindow)
        self.scope_pressure=Scope(self.ax_pressure,"Pression","cmH2O",self.xlim, self.timeresolution, self.data_controller.inputs.pressure)
        self.scope_flow=Scope(self.ax_flow,"Débit","L/min",self.xlim, self.timeresolution, self.data_controller.inputs.flow)
        self.scope_volume=Scope(self.ax_volume,"Volume","mL",self.xlim, self.timeresolution, self.data_controller.inputs.volume)
        self.ax_pressure.get_xaxis().set_visible(False)
        self.ax_flow.get_xaxis().set_visible(False)

        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.leftside)
        self.canvas_graph.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.animation = matplotlib.animation.FuncAnimation(self.fig_graph, self.update, interval=self.timeresolution * 1000,blit=True)

        self.freeze_time=False
        self.delta_marker=None
        
        self.arrows_frame=tk.Frame(self.app) 
        self.arrows_string = ['<<','<','>','>>']
        self.arrows = []
        for i in range(4):
            self.arrows.append(Button2(self.arrows_frame, self.arrows_string[i]))
            self.arrows[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            self.arrows[i].bind('<1>', self.arrows_event,'+')
        self.arrows_frame.grid(row=5,column=6,columnspan=2, sticky="news")
        self.arrows_frame.grid_forget()

        self.updateAlarmDisplay()
        #just here for test
        self.test_cnt = 0
    
    def freeze_curve(self, freeze):
        if freeze:
            self.freeze_time=True
            self.data_controller.inputs.timedata_freeze(self.freeze_time)
            self.arrows_frame.grid(row=5,column=6,columnspan=2, sticky="news")
            self.delta_marker=0
        else:
            self.freeze_time=False
            self.data_controller.inputs.timedata_freeze(self.freeze_time)
            self.arrows_frame.grid_forget()
            self.delta_marker=None

    def arrows_event(self, event):
        inc=0
        if(event.widget==self.arrows[0]):
            inc=10
        elif(event.widget==self.arrows[1]):
            inc=1
        elif(event.widget==self.arrows[2]):
            inc=-1
        elif(event.widget==self.arrows[3]):
            inc=-10
        self.delta_marker=self.delta_marker+inc
        if(self.delta_marker<0):
            self.delta_marker=0

    def event_bt_freeze(self,e):
        self.freeze_curve(not self.freeze_time)

    def pset_event(self, event):
        if(event.type==tk.EventType.ButtonPress):
            self.pset_timer=self.app.after(5000, self.pset_opendialog)
        if(event.type==tk.EventType.ButtonRelease):
            self.app.after_cancel(self.pset_timer)

    def pset_opendialog(self):
        PowerSettingsDialog(self.app)
        self.bt_pset.config(activebackground=config.button['btn_background'])

    def stop_ins_event(self, e):
        if(e.type==tk.EventType.ButtonPress):
            self.data_controller.stop_ins(True)
        elif(e.type==tk.EventType.ButtonRelease):
            self.data_controller.stop_ins(False)
    
    def stop_exp_event(self, e):
        if(e.type==tk.EventType.ButtonPress):
            self.data_controller.stop_exp(True)
        elif(e.type==tk.EventType.ButtonRelease):
            self.data_controller.stop_exp(False)

    def update(self, frame):
        index = self.data_controller.inputs.get_index()
        lp = self.scope_pressure.update(index,self.delta_marker)
        lf = self.scope_flow.update(index,self.delta_marker)
        lv = self.scope_volume.update(index,self.delta_marker)
        if(self.data_controller.inputs.changed):
            self.m_ie.update(self.data_controller.inputs.inputs[DataBackend.IE])
            self.m_pep.update(self.data_controller.inputs.inputs[DataBackend.PEP], self.data_controller.activeAlarms[AlarmType.PEP_MAX] or self.data_controller.activeAlarms[AlarmType.PEP_MIN])
            self.m_fr.update(self.data_controller.inputs.inputs[DataBackend.FR], self.data_controller.activeAlarms[AlarmType.FREQUENCE_RESPIRATOIRE])
            self.m_pplat.update(self.data_controller.inputs.inputs[DataBackend.PPLAT])
            self.m_vm.update(self.data_controller.inputs.inputs[DataBackend.VM], self.data_controller.activeAlarms[AlarmType.VOLUME_MINUTE])
            self.m_pcrete.update(self.data_controller.inputs.inputs[DataBackend.PCRETE], self.data_controller.activeAlarms[AlarmType.PRESSION_MAX] or self.data_controller.activeAlarms[AlarmType.PRESSION_MIN])
            self.m_vte.update(self.data_controller.inputs.inputs[DataBackend.VTE], self.data_controller.activeAlarms[AlarmType.VOLUME_COURANT])

        #check if an alarm has been activated
        if( self.data_controller.GetAlarmState(AlarmType.PRESSION_MAX)):
            alarm = Alarm(AlarmType.PRESSION_MAX, AlarmType.PRESSION_MAX.isHighLevel(AlarmType.PRESSION_MAX))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.PRESSION_MIN)):
            alarm = Alarm(AlarmType.PRESSION_MIN, AlarmType.PRESSION_MIN.isHighLevel(AlarmType.PRESSION_MIN))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.VOLUME_COURANT)):
            alarm = Alarm(AlarmType.VOLUME_COURANT, AlarmType.VOLUME_COURANT.isHighLevel(AlarmType.VOLUME_COURANT))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.FREQUENCE_RESPIRATOIRE)):
            alarm = Alarm(AlarmType.FREQUENCE_RESPIRATOIRE, AlarmType.FREQUENCE_RESPIRATOIRE.isHighLevel(AlarmType.FREQUENCE_RESPIRATOIRE))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.VOLUME_MINUTE)):
            alarm = Alarm(AlarmType.VOLUME_MINUTE, AlarmType.VOLUME_MINUTE.isHighLevel(AlarmType.VOLUME_MINUTE))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.PEP_MAX)):
            alarm = Alarm(AlarmType.PEP_MAX, AlarmType.PEP_MAX.isHighLevel(AlarmType.PEP_MAX))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.PEP_MIN)):
            alarm = Alarm(AlarmType.PEP_MIN, AlarmType.PEP_MIN.isHighLevel(AlarmType.PEP_MIN))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.LOW_BATTERY)):
            alarm = Alarm(AlarmType.LOW_BATTERY, AlarmType.LOW_BATTERY.isHighLevel(AlarmType.LOW_BATTERY))
            self.alarmMgr.ActivateAlarm(alarm)
        if( self.data_controller.GetAlarmState(AlarmType.FAILSAFE)):
            alarm = Alarm(AlarmType.FAILSAFE, AlarmType.FAILSAFE.isHighLevel(AlarmType.FAILSAFE))
            self.alarmMgr.ActivateAlarm(alarm)
        self.updateAlarmDisplay()
        return (*lp,*lf,*lv)

    def run(self):
        self.data_backend.start()
        self.app.mainloop()
        self.app.destroy()
        self.data_backend.stop()

    def updateAlarmDisplay(self):
        if( self.alarmMgr.GetActivAlarmNb() == 0):
            self.alarm_text.set("")
            self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_No_Alarm.png",bg='#4E69AB')
        else :
            self.alarm_text.set(self.alarmMgr.GetCurrentMessageToDisplay())
            if(self.alarmMgr.GetCurrentMessageLevel() == AlarmLevel.MEDIUM_PRIORITY):
                self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_Medium_Priority.png",bg='yellow')
            elif(self.alarmMgr.GetCurrentMessageLevel() == AlarmLevel.HIGH_PRIORITY):
                self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_High_Priority.png", bg='red')
            else:
                #unknown case
                self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_No_Alarm.png",bg='#4E69AB')


    #note Boris: note sure if this function will be usefull
    #def updateAlarmText(self, newText):
        #self.alarm_text.set(newText)




    #see what we need to do with this button in function in function of the implementation of alarm system
    def event_bt_Alarm(self, e):
        print("event_bn_alarm pressed")
        #just for test
        if(self.test_cnt == 0):
            #do something
            alarm1 = Alarm(AlarmType.PRESSION_MAX, AlarmLevel.MEDIUM_PRIORITY)
            self.alarmMgr.ActivateAlarm(alarm1)
            self.updateAlarmDisplay()
        elif(self.test_cnt == 1):
            #do other things
            alarm2 = Alarm(AlarmType.PRESSION_MIN, AlarmLevel.HIGH_PRIORITY)
            self.alarmMgr.ActivateAlarm(alarm2)
            self.updateAlarmDisplay()

        elif(self.test_cnt == 2):
            #do other things
            alarm2 = Alarm(AlarmType.PRESSION_MIN, AlarmLevel.HIGH_PRIORITY)
            self.alarmMgr.ActivateAlarm(alarm2)
            self.updateAlarmDisplay()

        elif(self.test_cnt == 3):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()

        elif(self.test_cnt == 4):
            #do other things
            alarm4 = Alarm(AlarmType.LOW_BATTERY, AlarmLevel.MEDIUM_PRIORITY)
            self.alarmMgr.ActivateAlarm(alarm4)
            self.updateAlarmDisplay()
            #KO parce que s'il n'y a pas de HIGH_PRIORITY on veut pas insérer en queue

        elif(self.test_cnt == 5):
            #do other things
            self.updateAlarmDisplay()
            alarm5 = Alarm(AlarmType.PEP_MAX, AlarmLevel.HIGH_PRIORITY)
            self.alarmMgr.ActivateAlarm(alarm5)
            self.updateAlarmDisplay()

        elif(self.test_cnt == 6):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()

        elif(self.test_cnt == 7):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()
        elif(self.test_cnt == 8):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()
        elif(self.test_cnt == 9):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()

        elif(self.test_cnt == 10):
            #do other things
            self.alarmMgr.DeActivateCurrentAlarm()
            self.updateAlarmDisplay()

        self.test_cnt += 1

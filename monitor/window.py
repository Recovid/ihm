# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datacontroller import DataController
from .databackend import DataBackend, DataBackendDummy, DataBackendFromFile, SerialPortMock
from .userinputs import OneValueDialog, NewPatientDialog
from .knob import Knob
from .mesure import Mesure
from .button import Button, Button2, ButtonPR


class Scope:
    def __init__(self, ax, title, ylabel, xlim, xstep, handler):

        self.handler=handler
        self.xstep=xstep
        self.ax=ax
        # self.ax.set_title(title,loc='left')
        #self.ax.set_title(title, x=0.46, y=1.0)
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
    
    def __init__(self):
        self.timewindow=15
        self.freq=20
        self.timeresolution=1.0/self.freq

        self.app = tk.Tk()

        #self.app.attributes("-fullscreen", True)
        self.ws = 800
        self.hw = 480
        self.app.geometry("%dx%d"% (self.ws , self.hw))
        #self.ws = self.app.winfo_width()
        #self.hw = self.app.winfo_height()
        self.alarm_text = tk.StringVar()
        self.alarm_text.set("Some Alarm message text")
        
        print('ws:',self.ws,' hw:',self.hw)

        self.app.wm_title("Graphe Matplotlib dans Tkinter")
        for i in range(6):
            tk.Grid.rowconfigure(self.app, i, weight=1, minsize=self.hw/6 if i>0 else self.hw/6/2)
        for i in range(9):
            tk.Grid.columnconfigure(self.app, i, weight=1, minsize=self.ws/9)
        
        #self.data_backend = DataBackendDummy(100,100,500)
        self.data_backend = DataBackendFromFile("tests/nominal_cycle.txt")
        #self.data_backend = SerialPortMock("in", "out")
        self.data_controller = DataController(self.data_backend, self.app)
        self.data_controller.init_inputs(self.timewindow,self.freq)
        
        stickyall=tk.N+tk.S+tk.E+tk.W
        #TITLE
        self.title_frame = tk.Frame(self.app, \
            bg='#4E69AB').grid(row=0,column=0,columnspan=9)
        self.title = tk.Label(self.title_frame, font=("Helvetica", -int(self.hw*0.05)),text='RECOVID', \
            anchor='n', fg='white',bg='#4E69AB').grid(row=0,column=0, columnspan=2, sticky=stickyall)
        self.alarm_msg = tk.Label(self.title_frame, font=("Helvetica", -int(self.hw*0.05)), textvariable = self.alarm_text, \
            anchor='n', fg='white',bg='#4E69AB').grid(row=0, column=2, columnspan=6, sticky=stickyall)

        self.bt_Alarm = Button2(self.app,"monitor/Alarms_Icon/Icon_High_Priority.png")
        self.bt_Alarm.set_background('#4E69AB')
        self.bt_Alarm.grid(self.title_frame, row=0, column=8, sticky=stickyall)
        self.bt_Alarm.bind('<ButtonRelease-1>', self.event_bt_Alarm, '+')

        #VALEURS A Droite
 
        #self.m_fio2 = Mesure(self.app,0,'%','FiO2')
        #self.m_fio2.grid(row=1,column=6, sticky="senw")
        #self.m_fio2.canvas.grid(row=1,column=6, sticky="senw")

        self.m_ie = Mesure(self.app,0, 'I/E')
        self.m_ie.canvas.grid(row=1, column=6, sticky="senw")

        self.m_pep = Mesure(self.app,0,'PEP','cmH2O')
        self.m_pep.canvas.grid(row=1,column=7, sticky="senw")

        self.m_fr = Mesure(self.app,0,'FR','/min', dmin=self.data_controller.outputs[DataBackend.FRMIN])
        self.m_fr.canvas.grid(row=2,column=6, sticky="senw")

        self.m_pplat = Mesure(self.app,0,'Pplat','cmH2O')
        self.m_pplat.canvas.grid(row=2,column=7, sticky="senw")

        self.m_vm = Mesure(self.app,0,'VM','L/min', dmin=self.data_controller.outputs[DataBackend.VMMIN])
        self.m_vm.canvas.grid(row=3,column=6, sticky="senw")
        
        self.m_pcrete = Mesure(self.app,0,'Pcrete','cmH2O', dmin=self.data_controller.outputs[DataBackend.PMIN], dmax=self.data_controller.outputs[DataBackend.PMAX])
        self.m_pcrete.canvas.grid(row=3,column=7, sticky="senw")

        self.m_vte = Mesure(self.app,0,'VTe','mL', dmin=self.data_controller.outputs[DataBackend.VTMIN])
        self.m_vte.canvas.grid(row=4,column=6, sticky="senw")

        #BOUTONS EN BAS
 
        self.k_vt = Knob(self.app, self.data_controller.outputs[DataBackend.VT],'ml','VT')
        self.k_vt.canvas.grid(row=5,column=0, sticky="senw")

        self.k_fr = Knob(self.app, self.data_controller.outputs[DataBackend.FR],'bpm','FR')
        self.k_fr.canvas.grid(row=5,column=1, sticky="senw")

        self.k_pep = Knob(self.app, self.data_controller.outputs[DataBackend.PEP],'cmH2O','PEP')
        self.k_pep.canvas.grid(row=5,column=2, sticky="senw")

        self.k_flow = Knob(self.app, self.data_controller.outputs[DataBackend.FLOW],'L/min','Debit Max')
        self.k_flow.canvas.grid(row=5,column=3, sticky="senw")

        self.k_tplat = Knob(self.app, self.data_controller.outputs[DataBackend.TPLAT],'','Tplat')
        self.k_tplat.canvas.grid(row=5,column=4, sticky="senw")

        #Boutons Pause
        self.btn_frame = tk.Frame(self.app,bg='#c9d2e5',width=int(self.ws*0.1),\
            height=int(self.hw*0.9)).grid(column=8,row=1,rowspan=5,sticky=stickyall)

        self.bt_new = Button2(self.app,"Nouveau\nPatient")
        self.bt_new.grid(row=1,column=8,sticky=stickyall)
        self.bt_new.bind('<Button-1>', self.event_bt_new,'+')
        
        self.bt_freeze = ButtonPR(self.app,"Geler courbes", "Resume")
        self.bt_freeze.grid(row=2,column=8,sticky=stickyall)
        self.bt_freeze.bind('<Button-1>', self.event_bt_freeze,'+')

        self.bt_si = Button2(self.app,"Pause Inspi")
        self.bt_si.grid(row=3,column=8, sticky="senw")
        self.bt_si.bind('<ButtonPress-1>',self.stop_ins_event,'+')
        self.bt_si.bind('<ButtonRelease-1>',self.stop_ins_event,'+')

        self.bt_se = Button2(self.app ,"Pause Expi")
        self.bt_se.grid(row=4,column=8, sticky="senw")
        self.bt_se.bind('<ButtonPress-1>',self.stop_exp_event,'+')
        self.bt_se.bind('<ButtonRelease-1>',self.stop_exp_event,'+')
       


        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=5,column=8)
        self.app.bind('<Control-q>', lambda event: self.app.quit())

        #Graph Init 

        self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1,figsize=(3,4))
        #self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1)
        self.fig_graph.tight_layout()
        self.xlim=(0,self.timewindow)
        self.scope_pressure=Scope(self.ax_pressure,"Pression","cmH2O",self.xlim, self.timeresolution, self.data_controller.inputs.pressure)
        self.scope_flow=Scope(self.ax_flow,"Débit","L/min",self.xlim, self.timeresolution, self.data_controller.inputs.flow)
        self.scope_volume=Scope(self.ax_volume,"Volume","mL",self.xlim, self.timeresolution, self.data_controller.inputs.volume)
        
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.app)
        self.canvas_graph.get_tk_widget().grid(row=1, column=0, rowspan=4,columnspan=6, sticky=tk.N+tk.S+tk.E+tk.W)
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

    def event_bt_new(self,e):
        NewPatientDialog(self.app, self.data_controller)
        
        self.k_vt.refresh()
        self.k_fr.refresh()
        self.k_pep.refresh()
        self.k_flow.refresh()
        self.k_tplat.refresh()

    def event_bt_freeze(self,e):
        self.freeze_curve(not self.freeze_time)

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
            #self.m_fio2.update(self.data_controller.inputs.inputs[DataBackend.FIO2])

            #recalcul de la valeur de I/E

            self.m_pep.update(self.data_controller.inputs.inputs[DataBackend.PEP], self.data_controller.inputs.inputs[DataBackend.PEP_ALARM])
            self.m_fr.update(self.data_controller.inputs.inputs[DataBackend.FR])
            self.m_pplat.update(self.data_controller.inputs.inputs[DataBackend.PPLAT])
            self.m_vm.update(self.data_controller.inputs.inputs[DataBackend.VM])
            self.m_pcrete.update(self.data_controller.inputs.inputs[DataBackend.PCRETE], self.data_controller.inputs.inputs[DataBackend.PCRETE_ALARM])
            self.m_vte.update(self.data_controller.inputs.inputs[DataBackend.VTE], self.data_controller.inputs.inputs[DataBackend.VTE_ALARM])
        return (*lp,*lf,*lv)

    def run(self):
        self.data_backend.start()
        self.app.mainloop()
        self.app.destroy()
        self.data_backend.stop()

    #note Boris: note sure if this function will be usefull
    def updateAlarmText(self, newText):
        self.alarm_msg.set_text(newText)

    #see what we need to do with this button in function in function of the implementation of alarm system
    def event_bt_Alarm(self, e):
        print("event_bn_alarm pressed")
        #just for test
        self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_Medium_Priority.png")
        #self.bt_Alarm.set_content("monitor/Alarms_Icon/Icon_No_Alarm.png")


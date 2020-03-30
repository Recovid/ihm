# -*- coding: utf-8 -*-
import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datacontroller import DataController
from .databackend import DataBackend, DataBackendDummy, DataBackendFromFile
from .userinputs import KeyboardUserInputManager, UserInputHandler, ButtonUserInputManager
from .knob import Knob
from .mesure import Mesure
from .button import Button


class Scope:
    def __init__(self, ax, title, ylabel, xlim, xstep, handler):

        self.handler=handler
        self.xstep=xstep
        self.ax=ax
        # self.ax.set_title(title,loc='left')
        self.ax.set_title(title, x=0.46, y=1.0)
        self.ax.set_ylabel(ylabel)
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

class RangeSetter:
    def __init__(self, app, value, label, handler):
        self.handler=handler
        self.scale=tk.Scale(app, variable=value, label=label, from_=handler.vmin, to=handler.vmax, command=self.update)
        self.scale.set(handler.value)

    def update(self,value):
        self.handler.update(value)


class Window:
    class UIHandler(UserInputHandler):

        def __init__(self, parent):
            self.parent=parent

        def minus_handler(self,big=False):
            if(self.parent.freeze_time):
                inc = 10 if big else 1
                self.parent.delta_marker=self.parent.delta_marker+inc
        def plus_handler(self, big=False):
            if(self.parent.freeze_time and self.parent.delta_marker>0):
                inc = 10 if big else 1
                self.parent.delta_marker=self.parent.delta_marker-inc
    
    def __init__(self):

        

        self.timewindow=15
        self.freq=20
        self.timeresolution=1.0/self.freq

        self.app = tk.Tk()

        self.app.attributes("-fullscreen", True)

        self.ws = self.app.winfo_screenwidth()
        self.hw = self.app.winfo_screenheight()
        # self.ws = 600
        # self.hw = 400
        
        print('ws:',self.ws,' hw:',self.hw)

        self.app.wm_title("Graphe Matplotlib dans Tkinter")
        tk.Grid.rowconfigure(self.app, 6, weight=1)
        tk.Grid.columnconfigure(self.app, 12, weight=1)
        
        # Bouton --/-/+/++
        self.userinputs = ButtonUserInputManager(self.app)
        self.userinputs.canvas.grid(row=5,column=9,columnspan=2)
        
        self.uihandler = Window.UIHandler(self)

        self.data_backend = DataBackendDummy(100,100,500)
        #self.data_backend = DataBackendFromFile("tests/nominal_cycle.txt")
        self.data_controller = DataController(self.data_backend)
        self.data_controller.init_inputs(self.timewindow,self.freq)
        
        #TITLE
        self.title_frame = tk.Frame(self.app,height=int(self.hw*0.1),width=self.ws, \
            bg='#4E69AB').grid(row=0,column=0,columnspan=12)
        self.title = tk.Label(self.title_frame, font=("Helvetica", 22),text='RECOVID', \
            anchor='nw', fg='white',bg='#4E69AB').grid(row=0,column=5)

        #VALEURS A Droite
 
        self.m_fio2 = Mesure(self.app,0,'%','FiO2')
        self.m_fio2.canvas.grid(row=1,column=9)

        self.m_pep = Mesure(self.app,0,'cmH2O','PEP')
        self.m_pep.canvas.grid(row=1,column=10)

        self.m_fr = Mesure(self.app,0,'/min','FR')
        self.m_fr.canvas.grid(row=2,column=9)

        self.m_pplat = Mesure(self.app,0,'cmH2O','Pplat')
        self.m_pplat.canvas.grid(row=2,column=10)

        self.m_vm = Mesure(self.app,0,'L/min','VM')
        self.m_vm.canvas.grid(row=3,column=9)
        
        self.m_pcrete = Mesure(self.app,0,'cmH2O','Pcrete', amin=self.data_controller.outputs[DataBackend.PMIN], amax=self.data_controller.outputs[DataBackend.PMAX], userinputs=self.userinputs)
        self.m_pcrete.canvas.grid(row=3,column=10)

        self.m_vte = Mesure(self.app,0,'mL','VTe', amin=self.data_controller.outputs[DataBackend.VMIN], userinputs=self.userinputs)
        self.m_vte.canvas.grid(row=4,column=9)

        #BOUTONS EN BAS
     
        btn1 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.FIO2], '%','FiO2')
        btn1.canvas.grid(row=5,column=2)
        
        btn2 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.VT],'ml','VT/vte')
        btn2.canvas.grid(row=5,column=3)

        btn3 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.FR],'bpm','FR')
        btn3.canvas.grid(row=5,column=4)

        btn4 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.PEP],'cmH2O','PEP')
        btn4.canvas.grid(row=5,column=5)

        btn5 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.FLOW],'L/min','Debit')
        btn5.canvas.grid(row=5,column=6)

        btn6 = Knob(self.app, self.userinputs, self.data_controller.outputs[DataBackend.TPLAT],'','Tplat')
        btn6.canvas.grid(row=5,column=7)

        #Boutons Pause
        self.btn_frame = tk.Frame(self.app,bg='#c9d2e5',width=int(self.ws*0.1),\
            height=int(self.hw*0.9)).grid(column=11,row=1,rowspan=5)

        self.bt_freeze = Button(self.app,0,"Geler courbes", "Resume")
        self.bt_freeze.canvas.grid(row=1,column=11)
        

        self.bt_si = Button(self.app,1,"Pause Inspi")
        self.bt_si.canvas.grid(row=2,column=11)

        self.bt_se = Button(self.app ,2,"Pause Expi")
        self.bt_se.canvas.grid(row=3,column=11)

        self.bt_freeze.canvas.bind('<Button-1>', self.event_bt_freeze)
        self.bt_freeze.canvas.bind('<ButtonRelease-1>', None)

        self.bt_si.canvas.bind('<ButtonPress-1>',self.stop_ins_event,'+')
        self.bt_si.canvas.bind('<ButtonRelease-1>',self.stop_ins_event,'+')

        self.bt_se.canvas.bind('<ButtonPress-1>',self.stop_exp_event,'+')
        self.bt_se.canvas.bind('<ButtonRelease-1>',self.stop_exp_event,'+')

        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=5,column=11)


        #Graph Init 

        self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1)
        self.fig_graph.tight_layout()
        self.xlim=(0,self.timewindow)
        self.scope_pressure=Scope(self.ax_pressure,"Pression","cmH2O",self.xlim, self.timeresolution, self.data_controller.inputs.pressure)
        self.scope_flow=Scope(self.ax_flow,"Débit","L/min",self.xlim, self.timeresolution, self.data_controller.inputs.flow)
        self.scope_volume=Scope(self.ax_volume,"Volume","mL",self.xlim, self.timeresolution, self.data_controller.inputs.volume)
        
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.app)
        self.canvas_graph.get_tk_widget().grid(row=1, column=0, rowspan=4,columnspan=8, sticky=tk.N+tk.S+tk.E+tk.W)
        matplotlib.animation.FuncAnimation(self.fig_graph, self.update, interval=self.timeresolution,blit=True)

        self.freeze_time=False
        self.delta_marker=None

    def freeze_curve(self, freeze):
        if freeze:
            self.freeze_time=True
            self.data_controller.inputs.timedata_freeze(self.freeze_time)
            self.userinputs.select(self.uihandler, arrows=True)
            self.delta_marker=0
            self.bt_freeze.push()
        else:
            self.freeze_time=False
            self.data_controller.inputs.timedata_freeze(self.freeze_time)
            self.userinputs.select(None)
            self.delta_marker=None
            self.bt_freeze.release()

    def event_bt_freeze(self,e):
        self.freeze_curve(not self.freeze_time)

    def stop_ins_event(self, e):
        if(e.type==tk.EventType.ButtonPress):
            self.data_backend.stop_ins(True)
        elif(e.type==tk.EventType.ButtonRelease):
            self.data_backend.stop_ins(False)
    
    def stop_exp_event(self, e):
        if(e.type==tk.EventType.ButtonPress):
            self.data_backend.stop_exp(True)
        elif(e.type==tk.EventType.ButtonRelease):
            self.data_backend.stop_exp(True)

    def update(self, frame):
        index = self.data_controller.inputs.get_index()
        lp = self.scope_pressure.update(index,self.delta_marker)
        lf = self.scope_flow.update(index,self.delta_marker)
        lv = self.scope_volume.update(index,self.delta_marker)
        if(self.data_controller.inputs.changed):
            self.m_fio2.update(self.data_controller.inputs.inputs[DataBackend.FIO2])
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


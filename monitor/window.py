import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datahandler import DataHandler
from .databackend import DataBackendDummy
from .knob import Knob


class Scope:
    def __init__(self, ax, title, ylabel, xlim, xstep, handler):

        self.handler=handler
        self.xstep=xstep
        self.ax=ax
        self.ax.set_title(title,loc='left')
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

    def __init__(self):

        self.timewindow=15
        self.freq=20
        self.timeresolution=1.0/self.freq

        self.app = tk.Tk()
        self.app.wm_title("Graphe Matplotlib dans Tkinter")
        self.app.bind('<Key>',self.keyinput)
        tk.Grid.rowconfigure(self.app, 6, weight=1)
        tk.Grid.columnconfigure(self.app, 12, weight=1)


        #TITLE
        self.title_frame = tk.Frame(self.app,height=50,width=1024, \
            bg='white').grid(row=0,column=0,columnspan=11)
        self.title = tk.Label(self.title_frame, font=("Helvetica", 22),text='RECOVID', \
            anchor='nw', fg='blue',bg='white').grid(row=0,column=5)

        #VALEURS A GAUCHE
        self.values1_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=1,column=9)
        tk.Label(self.values1_frame, font=("Helvetica", 22),text='FiO2 Vol%\n 250 ', \
            anchor='nw', fg='blue',bg='white').grid(row=1,column=9)
        self.values2_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=1,column=10)
        tk.Label(self.values2_frame, font=("Helvetica", 22),text='PEP mbar\n 5.0 ', \
            anchor='nw', fg='blue',bg='white').grid(row=1,column=10)
        self.values3_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=2,column=9)
        tk.Label(self.values3_frame, font=("Helvetica", 22),text='FR/min\n 35 ', \
            anchor='nw', fg='blue',bg='white').grid(row=2,column=9)
        self.values4_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=2,column=10)
        tk.Label(self.values4_frame, font=("Helvetica", 22),text='Pplat mbar\n 0 ', \
            anchor='nw', fg='blue',bg='white').grid(row=2,column=10)
        self.values5_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=3,column=9)
        tk.Label(self.values5_frame, font=("Helvetica", 22),text='VM l/min\n 0.45 ', \
            anchor='nw', fg='blue',bg='white').grid(row=3,column=9)
        self.values6_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=3,column=10)
        tk.Label(self.values5_frame, font=("Helvetica", 22),text='Pcrete mbar\n 0.45 ', \
            anchor='nw', fg='blue',bg='white').grid(row=3,column=10)
        self.values7_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=4,column=9)
        tk.Label(self.values5_frame, font=("Helvetica", 22),text='VTe mL\n 463 ', \
            anchor='nw', fg='blue',bg='white').grid(row=4,column=9)
        self.values8_frame = tk.Frame(self.app,borderwidth=3, \
            bg='blue').grid(row=4,column=10)
        tk.Label(self.values5_frame, font=("Helvetica", 22),text='', \
            anchor='nw', fg='blue',bg='white').grid(row=4,column=10)

        #BOUTONS EN BAS
     
        btn1 = Knob(self.app, 0, 100,0,'FiO2 %')
        btn1.canvas.grid(row=5,column=1)

        btn2 = Knob(self.app, 0, 100,1,'VT')
        btn2.canvas.grid(row=5,column=2)

        btn3 = Knob(self.app, 0, 100,2,'FR')
        btn3.canvas.grid(row=5,column=3)

        btn4 = Knob(self.app, 0, 100,3,'PEP')
        btn4.canvas.grid(row=5,column=4)

        btn5 = Knob(self.app, 0, 100,4,'Debit')
        btn5.canvas.grid(row=5,column=5)

        #Boutons Pause
        #btn_frame = tk.Frame(self.app,bg='res').grid(column=11)
        # tk.Button(btn_frame,text ="geler courbes", font=("Helvetica", 22)).grid(row=1,column=11)
        # tk.Button(btn_frame,text ="pause inspi", font=("Helvetica", 22)).grid(row=2,column=11)
        # tk.Button(btn_frame,text ="pause exspi", font=("Helvetica", 22)).grid(row=3,column=11)

        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=5,column=9)
        #Graph Init 
        self.data_backend = DataBackendDummy(100,100,500);
        self.data_handler = DataHandler(self.data_backend)
        self.data_handler.init_inputs(self.timewindow,self.freq)

        self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1)
        self.xlim=(0,self.timewindow)
        self.scope_pressure=Scope(self.ax_pressure,"Pression","mBar",self.xlim, self.timeresolution, self.data_handler.inputs.pressure)
        self.scope_flow=Scope(self.ax_flow,"Débit","L/min",self.xlim, self.timeresolution, self.data_handler.inputs.flow)
        self.scope_volume=Scope(self.ax_volume,"Volume","mL",self.xlim, self.timeresolution, self.data_handler.inputs.volume)
        
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.app)
        self.canvas_graph.get_tk_widget().grid(row=1, column=0, rowspan=4,columnspan=8, sticky=tk.N+tk.S+tk.E+tk.W)
        matplotlib.animation.FuncAnimation(self.fig_graph, self.update, interval=self.timeresolution,blit=True)

        self.freeze_time=False
        self.delta_marker=None

    def keyinput(self,event):
        #print(event)
        if(event.keysym=='space'):
            self.freeze_time= not self.freeze_time
            self.data_handler.inputs.timedata_freeze(self.freeze_time)
            if self.freeze_time:
                self.delta_marker=0
            else:
                self.delta_marker=None
        elif(event.keysym=="Left"):
            if(self.freeze_time):
                self.delta_marker=self.delta_marker+1
        elif(event.keysym=="Right"):
            if(self.freeze_time and self.delta_marker>0):
                self.delta_marker=self.delta_marker-1
    def update(self, frame):
        index = self.data_handler.inputs.get_index()
        lp = self.scope_pressure.update(index,self.delta_marker)
        lf = self.scope_flow.update(index,self.delta_marker)
        lv = self.scope_volume.update(index,self.delta_marker)
        return (*lp,*lf,*lv)

    def run(self):
        self.data_backend.start()
        self.app.mainloop()
        self.app.destroy()
        self.data_backend.stop()


import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datahandler import DataHandler
from .databackend import DataBackendDummy
from .knob import Knob
from .mesure import Mesure


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
            bg='#4E69AB').grid(row=0,column=0,columnspan=12)
        self.title = tk.Label(self.title_frame, font=("Helvetica", 22),text='RECOVID', \
            anchor='nw', fg='white',bg='#4E69AB').grid(row=0,column=5)

        #VALEURS A GAUCHE
 
        m1 = Mesure(self.app,0,'%','FiO2 %')
        m1.canvas.grid(row=1,column=9)
        m2 = Mesure(self.app,0,'mbar','PEP')
        m2.canvas.grid(row=1,column=10)

        m3 = Mesure(self.app,0,'/min','FR')
        m3.canvas.grid(row=2,column=9)
        m4 = Mesure(self.app,0,'mbar','Pplat')
        m4.canvas.grid(row=2,column=10)

        m5 = Mesure(self.app,0,'L/min','VM')
        m5.canvas.grid(row=3,column=9)
        m6 = Mesure(self.app,0,'mbar','Pcrete')
        m6.canvas.grid(row=3,column=10)

        m7 = Mesure(self.app,0,'mL','VTe')
        m7.canvas.grid(row=4,column=9)
    

        #BOUTONS EN BAS
     
        btn1 = Knob(self.app, 0, 100,0,'%','FiO2 %')
        btn1.canvas.grid(row=5,column=2)

        btn2 = Knob(self.app, 0, 1000,1,'ml','VT')
        btn2.canvas.grid(row=5,column=3)

        btn3 = Knob(self.app, 0, 50,2,'bpm','FR')
        btn3.canvas.grid(row=5,column=4)

        btn4 = Knob(self.app, 0, 30,3,'cmH2O','PEP')
        btn4.canvas.grid(row=5,column=5)

        btn5 = Knob(self.app, 0, 100,4,'L/min','Debit')
        btn5.canvas.grid(row=5,column=6)

        btn6 = Knob(self.app, 0, 100,4,'','Tplat')
        btn6.canvas.grid(row=5,column=7)

        #Boutons Pause
        btn_frame = tk.Frame(self.app,bg='#c9d2e5',width=150,height=600).grid(column=11,row=1,rowspan=5)

        tk.Button(btn_frame,text ="geler courbes",font=("Helvetica", 18)).grid(row=1,column=11)
        tk.Button(btn_frame,text ="pause inspi", font=("Helvetica", 18)).grid(row=2,column=11)
        tk.Button(btn_frame,text ="pause exspi", font=("Helvetica", 18)).grid(row=3,column=11)

        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=5,column=11)

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


import numpy as np
import matplotlib
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
from .datahandler import DataHandlerDummy, DataInputs


class Scope:
    def __init__(self, ax, title, ylabel, xlim, xstep, handler):

        self.handler=handler
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

    def update(self, index):
        self.iterator=index
        self.line_a.set_data(self.tdata[0:self.iterator], self.handler.data[0:self.iterator])
        diff = len(self.tdata) - self.iterator
        if diff > 10:
            indx_b = self.iterator + 10
        else:
            indx_b = len(self.tdata)-1
        self.line_b.set_data(self.tdata[indx_b:len(self.tdata)-1], self.handler.data[indx_b:len(self.tdata)-1])

        return self.line_a, self.line_b,

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
        tk.Grid.rowconfigure(self.app, 0, weight=1)
        tk.Grid.columnconfigure(self.app, 0, weight=1)
        tk.Button(self.app, text='Quitter', command=self.app.quit).grid(row=3,column=0)
        #Graph Init 
        self.data_handler = DataHandlerDummy()
        self.data_handler.inputs=DataInputs(self.timewindow,self.freq,(-30,105),(-100,100),(0,500))

        self.fig_graph, (self.ax_pressure, self.ax_flow, self.ax_volume) = plt.subplots(3, 1)
        self.xlim=(0,self.timewindow)
        self.scope_pressure=Scope(self.ax_pressure,"Pression","mBar",self.xlim, self.timeresolution, self.data_handler.inputs.pressure)
        self.scope_flow=Scope(self.ax_flow,"Débit","L/min",self.xlim, self.timeresolution, self.data_handler.inputs.flow)
        self.scope_volume=Scope(self.ax_volume,"Volume","mL",self.xlim, self.timeresolution, self.data_handler.inputs.volume)
        self.canvas_graph = FigureCanvasTkAgg(self.fig_graph, self.app)
        self.canvas_graph.get_tk_widget().grid(row=0, column=0, rowspan=3, sticky=tk.N+tk.S+tk.E+tk.W)
        matplotlib.animation.FuncAnimation(self.fig_graph, self.update, interval=self.timeresolution,blit=True)

        self.range_fio2=RangeSetter(self.app, tk.IntVar(), "FiO2", self.data_handler.outputs.fio2)
        self.range_fio2.scale.grid(row=0, column=1)

        self.range_pep=RangeSetter(self.app, tk.IntVar(), "PEP", self.data_handler.outputs.pep)
        self.range_pep.scale.grid(row=0, column=2)

        self.range_fr=RangeSetter(self.app, tk.IntVar(), "FR", self.data_handler.outputs.fr)
        self.range_fr.scale.grid(row=1, column=1)

        self.range_flow=RangeSetter(self.app, tk.IntVar(), "Debit", self.data_handler.outputs.flow)
        self.range_flow.scale.grid(row=1, column=2)

        self.range_vt=RangeSetter(self.app, tk.IntVar(), "VT", self.data_handler.outputs.vt)
        self.range_vt.scale.grid(row=2, column=1)

    def update(self, frame):
        index = self.data_handler.inputs.get_index()
        sp_in_a,sp_in_b = self.scope_pressure.update(index)
        sp_fl_a,sp_fl_b = self.scope_flow.update(index)
        sp_vl_a,sp_vl_b = self.scope_volume.update(index)
        return sp_in_a,sp_in_b,sp_fl_a,sp_fl_b,sp_vl_a,sp_vl_b,

    def run(self):
        self.data_handler.start()
        self.app.mainloop()
        self.app.destroy()
        self.data_handler.stop()


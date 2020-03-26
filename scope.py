import numpy as np
import matplotlib
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tkinter import *
from tkinter.ttk import *
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time


class Monitor:
    def __init__(self):
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, sharey=True)

        self.scope_pressure = Scope(self.ax1)
        self.scope_flow = Scope(self.ax2)
        self.scope_volume = Scope(self.ax3)

    def update(self, inputs):

        sp_in = inputs[0]
        sp_fl = inputs[1]
        sp_vl = inputs[2]
        sp_in_a,sp_in_b = self.scope_pressure.update(sp_in)
        sp_fl_a,sp_fl_b = self.scope_flow.update(sp_fl)
        sp_vl_a,sp_vl_b = self.scope_volume.update(sp_vl)

        return sp_in_a,sp_in_b,sp_fl_a,sp_fl_b,sp_vl_a,sp_vl_b,



class Scope:
    def __init__(self, ax):
        print("DEBUG C")
        self.st = time.time()
        self.x_sec = 15
        self.ax = ax
        self.tdata = [0]
        self.ydata = [0]
        for i in range(0,10*self.x_sec):
            self.tdata.append(i+1)
            self.ydata.append(0.0)

        self.line_a = Line2D(self.tdata, self.ydata)
        self.line_b = Line2D(self.tdata, self.ydata)
        self.props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

        self.ax.add_line(self.line_a)
        self.ax.add_line(self.line_b)
        self.ax.set_ylim(-.1, 1.1)
        self.ax.set_xlim(0, 10*15)
        self.first_loop = True
        self.iterator = 0
        self.textstr = ''

    def update(self, y):

        

        if self.iterator < len(self.tdata):
            self.ydata[self.iterator] = y
        else:
            self.iterator = 0
            t = time.time()
            print(str(t-self.st))
            self.st=t
            # self.ax.figure.canvas.draw()
        
 
        self.iterator+=1
        
        self.line_a.set_data(self.tdata[0:self.iterator], self.ydata[0:self.iterator])
        diff = len(self.tdata) - self.iterator
        if diff > 10:
            indx_b = self.iterator + 10
        else:
            indx_b = self.iterator - diff
        self.line_b.set_data(self.tdata[indx_b:len(self.tdata)-1], self.ydata[indx_b:len(self.tdata)-1])
   
        # self.textstr = '\n'.join((
        #     r'$\mathrm{value}=%.2f$' % (y, ),))

        # self.ax.text(0.85, 0.85, self.textstr, transform=self.ax.transAxes, fontsize=8,
        #     verticalalignment='top', bbox=self.props)

        return self.line_a, self.line_b,


def emitter(p=0.03):
    """Return a random value in [0, 1) with probability p, else 0."""
    while True:
        v = np.random.rand(1)
        if v > p:
            yield (0.,0.,0.)
        else:
            yield (np.random.rand(1)[0],np.random.rand(1)[0],np.random.rand(1)[0])




root = Tk()

monitor = Monitor()

canvas = FigureCanvasTkAgg(monitor.fig, root)
canvas.get_tk_widget().grid(row=0, column=0)


animation.FuncAnimation(monitor.fig, monitor.update, emitter, interval=100,blit=True)

root.mainloop()
# plt.show()

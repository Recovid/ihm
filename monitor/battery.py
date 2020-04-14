
# -*- coding: utf-8 -*-

import config
import tkinter as tk
import tkinter.font as tkfont
import time

class BatteryDisplay():
    def __init__(self, app, id):
        #tk.Frame.__init__(self, app, bg='white')
        self.app = app
        self.value = tk.IntVar()
        self.value.set(0)
        self.id = id
        self.color = 'green'

        self.width = int(app.winfo_screenwidth()*config.mesure['ratio_width'])
        self.height = self.width
        self.canvas = tk.Canvas(app, height=self.height, width=self.width)
        coord = int(self.width*0.3), int(self.height*0.1), int(self.width*0.7), int(self.height*0.9)
        self.grey_rec = self.canvas.create_rectangle(coord, fill='grey')
        self.top_grey_rec = self.canvas.create_rectangle(int(self.width*0.45), 2, int(self.width*0.55), int(self.height*0.1), fill='grey')
        self.lvl_rec = self.canvas.create_rectangle(int(self.width*0.3-1), int(self.height*0.1-1), int(self.width*0.55-1), int(self.height*0.1-1), fill=self.color)


        self.font_size_unit = int(self.height*config.knob['font_ratio_unit'])#10
        self.text = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
            font=(config.knob['font_family'], self.font_size_unit),\
            fill='white', text="30%", tags='text_percent')

        self.canvas.bind('<Configure>', self.configure)

    def configure(self, event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())

        print(self.width)
        print(self.height)

        coord = int(self.width*0.3), int(self.height*0.1), int(self.width*0.7), int(self.height*0.9)
        self.canvas.coords(self.grey_rec, coord)

        coord2 = int(self.width*0.45), 2, int(self.width*0.55), int(self.height*0.1)
        self.canvas.coords(self.top_grey_rec, coord2)
        batterylvl = int(self.value.get())
        coord3 = int(self.width*0.3+1), int(self.height*(0.1 + 0.8*(100-batterylvl)/100)+1), int(self.width*0.7-1), int(self.height*0.9-1)
        self.canvas.coords(self.lvl_rec, coord3)

        font_size = int(self.width*config.knob['font_ratio_title'])
        self.canvas.coords(self.text,(int(self.width*0.5), int(self.height*0.5)))
        self.canvas.itemconfig(self.text,font=(config.knob['font_family'],font_size))


    def update(self, value):
        self.value.set(value)
        batteryLevel = int(self.value.get())
        #print(batteryLevel)
        if( batteryLevel > config.batteryDisplay['green_thresh']):
            self.color = 'green'
        elif( (batteryLevel< config.batteryDisplay['green_thresh']) and (batteryLevel > config.batteryDisplay['yellow_thresh'])):
            self.color = 'yellow'
        else:
            self.color = 'red'

        item_txt = self.canvas.find_withtag('text_percent')
        self.canvas.itemconfigure(item_txt, text = str(self.value.get()) + '%')

        coord3 = int(self.width*0.3+1), int(self.height*(0.1 + 0.8*(100-batteryLevel)/100)+1), int(self.width*0.7-1), int(self.height*0.9-1)
        self.canvas.coords(self.lvl_rec, coord3)
        self.canvas.itemconfig(self.lvl_rec, fill=self.color)

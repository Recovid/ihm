
# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.font as tkfont
import time
from .userinputs import UserInputHandler

class AlarmValue(UserInputHandler):
    def __init__(self, mesure, datamanager, userinputs, anchor="sw"):
        
        self.selected=False
        self.mesure=mesure
        self.datamanager=datamanager
        self.userinputs=userinputs
        font = tkfont.Font(family="Helvetica", size=self.mesure.font_size_unit, weight="normal")
        th = font.metrics('linespace')
        tw = font.measure(str(self.datamanager.value))
        rs=0.25
        rect_coord=(0,int(self.mesure.height*(1-rs)), int(self.mesure.width*rs), int(self.mesure.height))
        if(anchor=='se'):
            rect_coord=(int(self.mesure.width*(1-rs)),int(self.mesure.height*(1-rs)), int(self.mesure.width), int(self.mesure.height))
        text_coord=((int((self.mesure.width*rs)-tw)/2), int(self.mesure.height-(self.mesure.height*rs-th)/2))
        if(anchor=='se'):
            text_coord=((int(self.mesure.width-(self.mesure.width*rs-tw)/2)), int(self.mesure.height-(self.mesure.height*rs-th)/2))
        self.rect = self.mesure.canvas.create_rectangle(rect_coord,tags=anchor, fill='blue')
        self.text = self.mesure.canvas.create_text(text_coord, anchor=anchor, \
        		font=font,fill='black', text=str(self.datamanager.value), tags=anchor)
        self.mesure.canvas.tag_bind(anchor,'<1>', self.click)
        self.value=datamanager.value

    def click(self,e):
        if(not self.selected):
            self.userinputs.select(self)
        elif(self.selected):
            self.datamanager.update(self.value)
            self.userinputs.select(None)
    def selected_handler(self):
        self.selected=True
        self.mesure.canvas.itemconfig(self.rect,fill='red')
    def unselected_handler(self):
        self.selected=False
        self.mesure.canvas.itemconfig(self.rect,fill='blue')
        self.value=self.datamanager.value
        self.update()

    def plus_handler(self, big=False):
        inc = 10 if big else 1
        self.value=self.value+self.datamanager.step*inc
        self.update()
    def minus_handler(self, big=False):
        inc = 10 if big else 1
        self.value=self.value-self.datamanager.step*inc
        self.update()

    def update(self):
        self.mesure.canvas.itemconfig(self.text, text=str(self.value))
        self.mesure.canvas.update_idletasks()


class Mesure:
    def __init__(self,app,id,unit,title,amin=None, amax=None, userinputs=None):
        self.value = tk.IntVar()
        self.value.set(0)
        self.state = 0
        self.id = id
        self.unit = unit
        self.title = title
        self.userinputs=userinputs

        self.width = int(app.winfo_screenwidth()*0.09)
        self.height = int(app.winfo_screenwidth()*0.09)
        # self.width = int(800*0.09)
        # self.height = int(600*0.09)

        self.font_size_value = int(self.height*0.4)
        self.font_size_unit = int(self.height*0.1)

        self.canvas = tk.Canvas(app, height=self.height, width=self.width,bg="#edf0f6")
        
        self.canvas.create_text(int(self.width*0.1), int(self.height*0.1), anchor='w', \
        		font=("Helvetica", self.font_size_unit),fill='black', text=self.title +" "+self.unit)
        self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
        		font=("Helvetica", self.font_size_value),fill='black', text=self.value.get(),tags='text'+str(self.id))
        if(amin is not None):
            self.amin=AlarmValue(self, amin,userinputs)
        if(amax is not None):
            self.amax=AlarmValue(self, amax,userinputs,'se')


    def update(self,value):
        self.value.set(value)
        self.canvas.itemconfigure('text'+str(self.id), text=self.value.get())
        self.canvas.update_idletasks()


# app = tk.Tk()
# app.wm_title("Graphe Matplotlib dans Tkinter")

# btn1 = Mesure(app,0,'MLrfr','VT')
# btn2 = Mesure(app, 0, 'MLrfr','VT')
# btn3 = Mesure(app, 0, 'MLrfr','VT')
# btn1.canvas.pack()
# btn2.canvas.pack()
# btn3.canvas.pack()

# for i in range(0,400):
#     print('debug:',i)
#     btn1.update(i)
#     btn2.update(i)
#     btn3.update(i)
#     time.sleep(0.1)
# app.mainloop()

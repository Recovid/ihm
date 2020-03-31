
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
        self.font = tkfont.Font(family="Helvetica", size=int(self.mesure.height*0.1), weight="normal")
        font_title = tkfont.Font(family="Helvetica", size=int(self.mesure.height*0.08), weight="normal")
        th = self.font.metrics('linespace')
        tw = self.font.measure(str(self.datamanager.value))
        th_title = font_title.metrics('linespace')
        tw_title = font_title.measure('max')
        rs_h=0.25
        self.rs_w=0.30
        text_value = "min"
        self.rect_coord=(0,int(self.mesure.height*(1-rs_h)), int(self.mesure.width*self.rs_w), int(self.mesure.height))
        if(anchor=='se'):
            self.rect_coord=(int(self.mesure.width*(1-(self.rs_w))),int(self.mesure.height*(1-rs_h)), int(self.mesure.width), int(self.mesure.height))
            text_value = "max"
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), self.rect_coord[3])
        text_title_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw_title)/2), self.rect_coord[1])
        self.rect = self.mesure.canvas.create_rectangle(self.rect_coord,tags=anchor, fill='#c16666')
        self.text_title = self.mesure.canvas.create_text( \
                text_title_coord, \
                anchor='nw', \
        		font=font_title,fill='black', text=text_value, tags=anchor)
        self.text = self.mesure.canvas.create_text(\
                text_coord, \
                anchor='sw', \
        	font=self.font,fill='black', text=str(self.datamanager.value), tags=anchor)
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
        self.mesure.canvas.itemconfig(self.rect,fill='#c16666')
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
        tw = self.font.measure(str(self.value))
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), self.rect_coord[3])
        self.mesure.canvas.coords(self.text, text_coord)
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
        self.alarm=False
        self.alarm_switch=False

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


    def update(self,value, alarm=False):
        self.value.set(value)
        self.canvas.itemconfigure('text'+str(self.id), text=self.value.get())
        self.canvas.update_idletasks()
        if(self.alarm!=alarm):
            self.set_alarm(alarm)

    def set_alarm(self, on):
        self.alarm=on
        if on:
            self.canvas.configure(background="#ff2026")
            self.alarm_switch=False
            self.update_alarm()
        else:
            self.canvas.configure(background="#edf0f6")
            self.canvas.after_cancel(self.alarm_id)
        self.canvas.update_idletasks()

    def update_alarm(self):
        self.alarm_switch = not self.alarm_switch
        self.canvas.configure(background=  "#ff2026" if self.alarm_switch else "#edf0f6")
        self.canvas.update_idletasks()
        self.alarm_id=self.canvas.after(1000 if self.alarm_switch else 500,self.update_alarm)

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

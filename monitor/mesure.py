
# -*- coding: utf-8 -*-
import tkinter as tk
import tkinter.font as tkfont
import time
from .userinputs import UserInputHandler, MinMaxDialog

class AlarmValue(UserInputHandler):
    def __init__(self, mesure, datamanager, userinputs, anchor="sw"):
        
        self.selected=False
        self.mesure=mesure
        self.datamanager=datamanager
        self.value=datamanager.value
        self.userinputs=userinputs
        self.anchor=anchor
        self.font = tkfont.Font(family="Helvetica", size=int(self.mesure.height*0.1), weight="normal")
        th = self.font.metrics('linespace')
        tw = self.font.measure(str(self.datamanager.value))
        self.rs_h=0.25
        self.rs_w=0.30
        self.rect_coord=(0,int(self.mesure.height*(1-self.rs_h)), int(self.mesure.width*self.rs_w), int(self.mesure.height))
        if(self.anchor=='se'):
            self.rect_coord=(int(self.mesure.width*(1-(self.rs_w))),int(self.mesure.height*(1-self.rs_h)), int(self.mesure.width), int(self.mesure.height))
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), self.rect_coord[3])
        self.rect = self.mesure.canvas.create_rectangle(self.rect_coord,tags=self.anchor, fill='#c16666')
        self.text = self.mesure.canvas.create_text(\
                text_coord, \
                anchor='sw', \
        	font=self.font,fill='black', text=str(self.datamanager.value), tags=self.anchor)
        #self.mesure.canvas.tag_bind(anchor,'<1>', self.click)
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
        self.rect_coord=(0,int(self.mesure.height*(1-self.rs_h)), int(self.mesure.width*self.rs_w), int(self.mesure.height))
        if(self.anchor=='se'):
            self.rect_coord=(int(self.mesure.width*(1-(self.rs_w))),int(self.mesure.height*(1-self.rs_h)), int(self.mesure.width), int(self.mesure.height))
        self.mesure.canvas.coords(self.rect,self.rect_coord)

        self.font = tkfont.Font(family="Helvetica", size=int(self.mesure.height*0.1), weight="normal")
        tw = self.font.measure(str(self.value))
        th = self.font.metrics('linespace')
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), int(self.rect_coord[3]-(self.mesure.height*self.rs_h-th)/2))
        self.mesure.canvas.coords(self.text, text_coord)
        self.mesure.canvas.itemconfig(self.text, text=str(self.value), font=self.font)
        self.mesure.canvas.update_idletasks()


class Mesure:
    def __init__(self,app,id,unit,title,dmin=None, dmax=None, userinputs=None):
        self.app=app
        self.value = tk.IntVar()
        self.value.set(0)
        self.state = 0
        self.id = id
        self.unit = unit
        self.title = title
        self.userinputs=userinputs
        self.alarm=False
        self.alarm_switch=False
        self.dmin=dmin
        self.dmax=dmax
        self.amin=None
        self.amax=None

        self.width = int(app.winfo_screenwidth()*0.009)
        self.height = int(app.winfo_screenwidth()*0.009)
        #self.width = 1
        #self.height = 1

        self.font_size_value = int(self.height*0.4)
        self.font_size_unit = int(self.height*0.15)
        self.font_family = "Helvetica"

        self.canvas = tk.Canvas(app, height=self.height, width=self.width,bg="#edf0f6")
        self.canvas.bind('<Configure>',self.configure)
        
        self.title_textid = self.canvas.create_text(int(self.width/2), int(self.height*0.05), anchor='n', \
        		font=("Helvetica", self.font_size_unit),fill='black', text=self.title+' ('+self.unit+')')
        self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
        		font=("Helvetica", self.font_size_value),fill='black', text=self.value.get(),tags='text'+str(self.id))
        if(dmin is not None):
            self.amin=AlarmValue(self, dmin,userinputs)
        if(dmax is not None):
            self.amax=AlarmValue(self, dmax,userinputs,'se')

        if(self.dmin is not None or self.dmax is not None):
            self.canvas.bind('<1>', self.click)

    def click(self,event):
        MinMaxDialog(self.app,self.title+' ('+self.unit+')',self.dmin, self.dmax)
        if(self.dmin is not None):
            self.amin.value=self.dmin.value
            self.amin.update()
        if(self.dmax is not None):
            self.amax.value=self.dmax.value
            self.amax.update()


    def configure(self,event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())
        self.font_size= int(self.height*0.35)
        self.title_font_size= int(self.height*0.1)
        self.canvas.coords(self.textid,(int(self.width/2),int(self.height/2)))
        self.canvas.itemconfig(self.textid, font=("Helvetica",self.font_size))
        self.canvas.coords(self.title_textid,(int(self.width/2),int(self.height*0.05)))
        self.canvas.itemconfig(self.title_textid, font=("Helvetica",self.title_font_size))
        if(self.amin is not None):
            self.amin.update()
        if(self.amax is not None):
            self.amax.update()

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

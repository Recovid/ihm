
# -*- coding: utf-8 -*-
import config
import tkinter as tk
import tkinter.font as tkfont
import time
from .userinputs import MinMaxDialog

class AlarmValue():
    def __init__(self, mesure, datamanager, anchor="sw"):
        
        self.selected=False
        self.mesure=mesure
        self.datamanager=datamanager
        self.value=datamanager.value
        self.anchor=anchor
        self.font = tkfont.Font(family=config.alarmValue['font_family'], \
            size=int(self.mesure.height*config.alarmValue['unit_value']), \
            weight="normal")
        th = self.font.metrics('linespace')
        tw = self.font.measure(str(self.datamanager.value))
        self.rs_h=config.alarmValue['height_ratio']
        self.rs_w=config.alarmValue['width_ratio']
        self.rect_coord=(0,int(self.mesure.height*(1-self.rs_h)), \
            int(self.mesure.width*self.rs_w), int(self.mesure.height))
        if(self.anchor=='se'):
            self.rect_coord=(int(self.mesure.width*(1-(self.rs_w))), \
                int(self.mesure.height*(1-self.rs_h)), \
                int(self.mesure.width), \
                int(self.mesure.height))
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), self.rect_coord[3])
        self.rect = self.mesure.canvas.create_rectangle(self.rect_coord,tags=self.anchor, fill=config.alarmValue['background'])
        self.text = self.mesure.canvas.create_text(\
                text_coord, \
                anchor='sw', \
        	font=self.font,fill=config.alarmValue['color_text'], text=str(self.datamanager.value), tags=self.anchor)
        self.value=datamanager.value
        
        self.datamanager.widget=self.mesure

    def selected_handler(self):
        self.selected=True
        self.mesure.canvas.itemconfig(self.rect, \
            fill=config.alarmValue['background_selected'])
    def unselected_handler(self):
        self.selected=False
        self.mesure.canvas.itemconfig(self.rect, \
            fill=config.alarmValue['background'])
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

        self.font = tkfont.Font(family=config.alarmValue['font_family'], size=int(self.mesure.height*0.1), weight="normal")
        tw = self.font.measure(str(self.value))
        th = self.font.metrics('linespace')
        text_coord = (int(self.rect_coord[0]+(self.mesure.width*self.rs_w-tw)/2), \
            int(self.rect_coord[3]-(self.mesure.height*self.rs_h-th)/2))
        self.mesure.canvas.coords(self.text, text_coord)
        self.mesure.canvas.itemconfig(self.text, text=str(self.value), font=self.font, fill=config.mesure['color_text_sync'] if self.datamanager.synchronized else config.mesure['color_text_unsync'])
        self.mesure.canvas.update_idletasks()


class Mesure:
    def __init__(self,app,id,title, unit=None ,dmin=None, dmax=None, is_frac=False ):
        self.app=app
        self.value = tk.IntVar()
        self.value.set(0)
        self.state = 0
        self.id = id
        self.unit = unit
        self.title = title
        self.sync=False
        self.alarm=False
        self.alarm_switch=False
        self.dmin=dmin
        self.dmax=dmax
        self.is_frac=is_frac
        self.amin=None
        self.amax=None

        self.width = int(app.winfo_screenwidth()*config.mesure['ratio_width'])
        self.height = self.width

        self.font_size_value = int(self.height*(config.mesure['font_ratio_value_frac'] if self.is_frac else config.mesure['font_ratio_value']))
        self.font_size_unit = int(self.height*config.mesure['font_ratio_title'])
        self.font_family = config.mesure['font_family']

        self.canvas = tk.Canvas(app, height=self.height, width=self.width,bg=config.mesure['background'])
        self.canvas.bind('<Configure>',self.configure)
        
        self.title_textid = self.canvas.create_text(int(self.width/2), int(self.height*0.05), anchor='n', \
        		font=(self.font_family, self.font_size_unit),\
                fill=config.mesure['color_text_sync'], text=self.title)
        coord_text = int(self.width*0.5), int(self.height*0.5)
        if(self.is_frac):
            coord_text = int(self.width*0.6), int(self.height*0.6)
            coord_line = (int(self.width*0.2),int(self.height*0.8),int(self.width*0.8),int(self.height*0.2))
            self.frac_line = self.canvas.create_line(coord_line, fill=config.mesure['color_text_sync'],width=3)
            self.text_one_id = self.canvas.create_text(int(self.width*0.3), int(self.height*0.3), anchor='c', \
                    font=(self.font_family, self.font_size_value),\
                    fill=config.mesure['color_text_sync'], text="1")
        self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
                font=(self.font_family, self.font_size_value),\
                fill=config.mesure['color_text_unsync'], text=self.value.get(),tags='text'+str(self.id))
        self.unit_textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.1), anchor='n', \
                font=(self.font_family, self.font_size_unit),\
                fill=config.mesure['color_text_sync'], text=self.unit)

        if(dmin is not None):
            self.amin=AlarmValue(self, dmin)
        if(dmax is not None):
            self.amax=AlarmValue(self, dmax,'se')

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
        # self.font_size= int(self.height*0.35)
        # self.title_font_size= int(self.height*0.1)
        self.font_size_value = int(self.height*(config.mesure['font_ratio_value_frac'] if self.is_frac else config.mesure['font_ratio_value']))
        self.title_font_size= int(self.height*config.mesure['font_ratio_title'])
        self.unit_font_size= int(self.height*config.mesure['font_ratio_unit'])
        coord_text = int(self.width*0.5), int(self.height*0.5)
        if(self.is_frac):
            coord_text = int(self.width*0.6), int(self.height*0.6)
            coord_line = (int(self.width*0.3),int(self.height*0.7),int(self.width*0.6),int(self.height*0.3))
            self.canvas.coords(self.frac_line, coord_line)
            coord_one_text = int(self.width*0.3), int(self.height*0.4)
            self.canvas.itemconfig(self.text_one_id, font=(config.mesure['font_family'],self.font_size_value))
            self.canvas.coords(self.text_one_id,coord_one_text)
        self.canvas.coords(self.textid,coord_text)
        self.canvas.itemconfig(self.textid, font=(config.mesure['font_family'],self.font_size_value))
        self.canvas.coords(self.title_textid,(int(self.width/2),int(self.height*0.05)))
        self.canvas.itemconfig(self.title_textid, font=(config.mesure['font_family'],self.title_font_size))
        self.canvas.coords(self.unit_textid,int(self.width/2),int(self.height*(1-config.mesure['height_ratio_unit'])))
        self.canvas.itemconfig(self.unit_textid, font=(config.mesure['font_family'], self.unit_font_size))


        if(self.amin is not None):
            self.amin.update()
        if(self.amax is not None):
            self.amax.update()

    def update(self,value, alarm=False):
        if(not self.sync):
            self.sync=True
            self.canvas.itemconfigure(self.textid, fill=config.mesure['color_text_sync'])

        self.value.set(value)
        self.canvas.itemconfigure('text'+str(self.id), text=self.value.get())
        self.canvas.update_idletasks()
        if(self.alarm!=alarm):
            self.set_alarm(alarm)

    def set_alarm(self, on):
        self.alarm=on
        if on:
            self.canvas.configure(background=config.mesure['background_alarmOn'])
            self.alarm_switch=False
            self.update_alarm()
        else:
            self.canvas.configure(background=config.mesure['background'])
            self.canvas.after_cancel(self.alarm_id)
        self.canvas.update_idletasks()

    def update_alarm(self):
        self.alarm_switch = not self.alarm_switch
        self.canvas.configure(background=config.mesure['background_alarmOn'] if self.alarm_switch else config.mesure['background'])
        self.canvas.update_idletasks()
        self.alarm_id=self.canvas.after(1000 if self.alarm_switch else 500,self.update_alarm)

    def refresh(self):
        if(self.amin is not None):
            self.amin.value=self.dmin.value
            self.amin.update()
        if(self.amax is not None):
            self.amax.value=self.dmax.value
            self.amax.update()


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

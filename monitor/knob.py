# -*- coding: utf-8 -*-
import config
import tkinter as tk
import time
from .userinputs import OneValueDialog, VTDialog
from .databackend import DataBackend

class Knob():
    def __init__(self,app, setting ,unit,title, min=None, max=None, is_frac=False):
        self.app=app
        self.setting = setting
        self.setting.widget=self
        self.value = setting.value
        self.selected = False
        self.unit = unit
        self.title = title
        self.is_frac = is_frac
        self.min = min
        self.max = max

      
        self.width = config.knob['width']
        self.height = config.knob['height']

        self.font_size_value = int(self.height*config.knob['font_ratio_value'])#22
        self.font_size_unit = int(self.height*config.knob['font_ratio_unit'])#10
        self.font_size_title = int(self.height*config.knob['font_ratio_title'])#15

        self.canvas = tk.Canvas(app, height=self.height, width=self.width)
        coord = int(self.width*0.1), int(self.height*0.1), int(self.width*0.9), int(self.height*0.9)
        self.arc_green = self.canvas.create_arc(coord, start=-45, extent=270, fill=config.knob['color_arc'])

        self.arc_grey = self.canvas.create_arc(coord, start=-45, extent=270, fill=config.knob['background'],tags='knob_value')

        coord = int(self.width*0.2), int(self.height*0.2), int(self.width*0.8), int(self.height*0.8)
        self.circle = self.canvas.create_oval(coord, fill=config.knob['background'], width=2,tags='knob_circle')

        self.title_textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.05), anchor='n', \
                font=(config.knob['font_family'], self.font_size_title),\
                fill=config.knob['background'], text=self.title)

        self.unit_textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.80), anchor='s', \
                font=(config.knob['font_family'], self.font_size_unit),\
                fill=config.knob['background'], text=self.unit)

        if( self.is_frac):
            self.min_textid = self.canvas.create_text(int(self.width*0.2), int(self.height*0.85), anchor='s', \
                font=("Helvetica", 12, "bold"), fill='grey', text= '1/'+ self.min)
            self.max_textid = self.canvas.create_text(int(self.width*0.8), int(self.height*0.85), anchor='s', \
                font=("Helvetica", 12, "bold"),fill='grey', text='1/' + self.max)
            
            self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.58), anchor='c', \
                    font=(config.knob['font_family'], int(self.font_size_value*0.7)),\
                    fill=config.knob['color_text_unsync'], text='2.0',tags='knob_value_text')

            coord_line = (int(self.width*0.31),int(self.height*0.47),int(self.width*0.73),int(self.height*0.47))
            self.frac_line = self.canvas.create_line(coord_line, fill=config.mesure['color_text_unsync'],width=3, tag='knob_value_frac_line')
            self.text_one_id = self.canvas.create_text(int(self.width*0.5), int(self.height*0.38), anchor='c', \
                    font=(config.knob['font_family'], int(self.font_size_value*0.7)),\
                    fill=config.mesure['color_text_unsync'], text="1", tag='knob_value_one')
        else:
            self.min_textid = self.canvas.create_text(int(self.width*0.2), int(self.height*0.85), anchor='s', \
                    font=("Helvetica", 12, "bold"),fill='grey', text=self.min)
            self.max_textid = self.canvas.create_text(int(self.width*0.8), int(self.height*0.85), anchor='s', \
                    font=("Helvetica", 12, "bold"),fill='grey', text=self.max)
            self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.4), anchor='c', \
                    font=(config.knob['font_family'], self.font_size_value),\
                    fill=config.knob['color_text_unsync'], text=str(0),tags='knob_value_text')
        
        self.canvas.bind('<Configure>',self.configure)
        self.canvas.bind('<ButtonPress-1>',self.onClick)

        self.update(self.value)
    
    def configure(self,event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())

        coordHeight = self.height
        coordWidth = self.width

        if(self.width > self.height ):
            coordWidth = coordHeight
        else:
            coordHeight = coordWidth

        centerx = int(self.width*0.5)
        centery = int(self.height*0.5)

        coord = int(centerx - coordWidth*0.4), int(centery -coordHeight*0.4), int(centerx + coordWidth*0.4), int(centery + coordHeight*0.4)
        self.canvas.coords(self.arc_green,coord)
        self.canvas.coords(self.arc_grey,coord)
        coord = int(centerx - coordWidth*0.3), int(centery -coordHeight*0.3), int(centerx + coordHeight*0.3), int(centery + coordHeight*0.3)
        self.canvas.coords(self.circle,coord)


        
        font_size = int(self.width*config.knob['font_ratio_unit'])
        self.canvas.coords(self.unit_textid,(int(self.width*0.5),int(self.height*0.90)))
        self.canvas.itemconfig(self.unit_textid, font=(config.knob['font_family'],font_size))
        

        font_size = int(self.width*config.knob['font_ratio_title'])
        self.canvas.coords(self.title_textid,(int(self.width*0.5), int(self.height*0.04)))
        self.canvas.itemconfig(self.title_textid,font=(config.knob['font_family'],font_size))

        if( self.is_frac):
            self.canvas.coords(self.min_textid,(int(self.width*0.15), int(self.height*0.95)))
            self.canvas.itemconfig(self.min_textid,font=(config.knob['font_family'],font_size, "bold"))

            self.canvas.coords(self.max_textid,(int(self.width*0.85), int(self.height*0.95)))
            self.canvas.itemconfig(self.max_textid,font=(config.knob['font_family'],font_size, "bold"))

            font_size = int(self.width*config.knob['font_ratio_value'])
            self.canvas.coords(self.textid,(int(self.width*0.50),int(self.height*0.58)))
            self.canvas.itemconfig(self.textid, font=(config.knob['font_family'],int(self.font_size_value*0.7)))
        else:
            self.canvas.coords(self.min_textid,(int(self.width*0.15), int(self.height*0.95)))
            self.canvas.itemconfig(self.min_textid,font=(config.knob['font_family'],font_size, "bold"))

            self.canvas.coords(self.max_textid,(int(self.width*0.85), int(self.height*0.95)))
            self.canvas.itemconfig(self.max_textid,font=(config.knob['font_family'],font_size, "bold"))

            font_size = int(self.width*config.knob['font_ratio_value'])
            self.canvas.coords(self.textid,(int(self.width*0.5),int(self.height*0.5)))
            self.canvas.itemconfig(self.textid, font=(config.knob['font_family'],self.font_size_value))



    def minus_handler(self, big=False):
        inc = 10 if big else 1
        self.update(self.value-self.setting.step*inc)
    def plus_handler(self, big=False):
        inc = 10 if big else 1
        self.update(self.value+self.setting.step*inc)
    def selected_handler(self):
        self.selected = True
        self.canvas.itemconfigure('knob_circle', fill=config.knob['background_selected'])
    def unselected_handler(self):
        self.selected = False
        self.canvas.itemconfigure('knob_circle', fill=config.knob['background'])



    def update(self,value,synchronized=False):
        if value >= self.setting.vmin and value <= self.setting.vmax:
            self.value = value
            self.value_norm = 270 - ((self.value-self.setting.vmin)/(self.setting.vmax - self.setting.vmin)*270)
            item_txt = self.canvas.find_withtag("knob_value")
            self.canvas.itemconfigure(self.arc_grey,extent=self.value_norm)
            item_txt = self.canvas.find_withtag("knob_value_text")
            self.canvas.itemconfigure(item_txt,text=str(value), fill=config.knob['color_text_sync'] if synchronized else config.knob['color_text_unsync'])
            self.canvas.update_idletasks()
            if( self.is_frac):
                item_txt = self.canvas.find_withtag("knob_value_one")
                self.canvas.itemconfigure(item_txt,fill=config.knob['color_text_sync'] if synchronized else config.knob['color_text_unsync'])
                item_txt = self.canvas.find_withtag("knob_value_frac_line")
                self.canvas.itemconfigure(item_txt,fill=config.knob['color_text_sync'] if synchronized else config.knob['color_text_unsync'])

            # TODO: display the value as (un)synchronized (given as argument)

    def onClick(self,event):
        # NB: self.app actually stores the knob parent (knob_frame) bug dialogs
        # expect the root window as first arg
        if self.setting.key == DataBackend.VT:
            VTDialog(self.app.master, self.setting)
        else:
            OneValueDialog(self.app.master,self.title+' ('+self.unit+')', self.setting)
        self.refresh()

    def refresh(self):
        self.update(self.setting.value, self.setting.synchronized)


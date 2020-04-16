
# -*- coding: utf-8 -*-

import config
import tkinter as tk
import tkinter.font as tkfont
from PIL import Image, ImageTk
import time

class BatteryDisplay():
    def __init__(self, app, id):
        self.app = app
        self.value = tk.IntVar()
        self.value.set(0)
        self.sector = False
        self.id = id
        self.color = 'green'

        self.width = int(app.winfo_screenwidth()*config.mesure['ratio_width'])
        self.height = self.width

        self.canvas = tk.Canvas(app, height=self.height, width= self.width)

        self.sector_img = Image.open("monitor/Alarms_Icon/Icon_Sector.png")
        self.loading_img = Image.open("monitor/Alarms_Icon/Icon_Loading.png")
        self.no_bat_img = Image.open("monitor/Alarms_Icon/Icon_batt_1.png")
        self.full_bat_img = Image.open("monitor/Alarms_Icon/Icon_batt_4.png")
        self.low_bat_img = Image.open("monitor/Alarms_Icon/Icon_batt_3.png")
        self.mid_bat_img = Image.open("monitor/Alarms_Icon/Icon_batt_2.png")

        self.sector_pimg = ImageTk.PhotoImage(self.sector_img)
        self.loading_pimg = ImageTk.PhotoImage(self.loading_img)
        self.no_bat_pimg = ImageTk.PhotoImage(self.no_bat_img)
        self.full_bat_pimg = ImageTk.PhotoImage(self.full_bat_img)
        self.low_bat_pimg = ImageTk.PhotoImage(self.low_bat_img)
        self.mid_bat_pimg = ImageTk.PhotoImage(self.mid_bat_img)

        self.full_icon = tk.Label(self.app, image=self.full_bat_pimg)
        self.low_icon = tk.Label(self.app, image=self.low_bat_pimg)
        self.mid_icon = tk.Label(self.app, image=self.mid_bat_pimg)
        self.no_bat_icon = tk.Label(self.app, image=self.no_bat_pimg)
        self.sector_icon = tk.Label(self.app, image=self.sector_pimg)
        self.loading_icon = tk.Label(self.app, image=self.loading_pimg)

        self.current_window1 = self.canvas.create_window(int(self.height/2), int(self.width/4), window=self.sector_icon)
        self.current_window2 = self.canvas.create_window(int(self.height/2), int(self.width*3/4), window=self.loading_icon)
        self.canvas.bind('<Configure>',self.configure)


    def configure(self, event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())
        self.disp_batt_loading()

    def disp_batt_loading(self):
        if( self.current_window1 is not None):
            self.canvas.delete(self.current_window1)
        if( self.current_window2 is not None):
            self.canvas.delete(self.current_window2)
        self.current_window1 = self.canvas.create_window(int(self.height/2), int(self.width/4), window=self.sector_icon)
        self.current_window2 = self.canvas.create_window(int(self.height/2), int(self.width*3/4), window=self.loading_icon)

    def disp_batt_full(self):
        if( self.current_window1 is not None):
            self.canvas.delete(self.current_window1)
        if( self.current_window2 is not None):
            self.canvas.delete(self.current_window2)
        self.canvas.create_window(int(self.height/2), int(self.width/2), window=self.full_icon)

    def disp_batt_mid(self):
        if( self.current_window1 is not None):
            self.canvas.delete(self.current_window1)
        if( self.current_window2 is not None):
            self.canvas.delete(self.current_window2)
        self.canvas.create_window(int(self.height/2), int(self.width/2), window=self.mid_icon)

    def disp_batt_low(self):
        if( self.current_window1 is not None):
            self.canvas.delete(self.current_window1)
        if( self.current_window2 is not None):
            self.canvas.delete(self.current_window2)
        self.canvas.create_window(int(self.height/2), int(self.width/2), window=self.low_icon)

    def disp_no_batt(self):
        if( self.current_window1 is not None):
            self.canvas.delete(self.current_window1)
        if( self.current_window2 is not None):
            self.canvas.delete(self.current_window2)
        self.canvas.create_window(int(self.height/2), int(self.width/2), window=self.no_bat_icon)


    def update(self, value, sector):
        self.value.set(value)

        if( sector):
            self.disp_batt_loading()
        else:
            if(value == 'A'):
                self.disp_batt_full()
            elif(value == 'B'):
                self.disp_batt_mid()
            elif(value == 'C'):
                self.disp_batt_low()
            else:
                self.disp_no_batt()


# -*- coding: utf-8 -*-
import config
import tkinter as tk
from .helpers import Dialog
from .button import Button2, ButtonPR
from PIL import Image, ImageTk

class LockScreen(tk.Canvas):
    def __init__(self,master, timer):
        tk.Canvas.__init__(self, master, width=800, height=480)
        self.timer=timer
        self.imgpath="monitor/Alarms_Icon/transparent.png"
        img = ImageTk.PhotoImage(file="monitor/Alarms_Icon/transparent.png")
        self.imgid = self.create_image(0, 0, image=img, anchor=tk.NW)
        self.bind('<Configure>', self.resize)
        
        self.textid = self.create_text(int(self.winfo_width()/2), int(self.winfo_height()/2), anchor='c', \
        		font=config.lockScreen['font_timer'],text=str(self.timer))
        self.title_textid = self.create_text(int(self.winfo_width()/2), int(self.winfo_height()*0.3), anchor='c', \
                font=config.lockScreen['font_title'],text="Dévérrouillage dans:")
        self.after(1000, self.update)
    
    def resize(self, event):
        img = Image.open(self.imgpath).resize(
            (event.width, event.height), Image.ANTIALIAS
        )
        self.img = ImageTk.PhotoImage(img)
        self.itemconfig(self.imgid,image=self.img)
        self.coords(self.textid,(int(self.winfo_width()/2), int(self.winfo_height()/2)))
        self.coords(self.title_textid,(int(self.winfo_width()/2), int(self.winfo_height()*0.2)))

    def update(self):
        self.timer=self.timer-1
        if(self.timer>0):
            self.itemconfig(self.textid,text=str(self.timer))
            self.after(1000, self.update)
        else:
            self.destroy()

class SettingsQuitDialog(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title("Quitter")

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        btquit = Button2(body,"Quitter")
        btquit.config(bg=config.powerSettings['bg_quit'], fg=config.powerSettings['fg'], font=config.powerSettings['font'])
        btquit.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)
        btquit.bind('<1>',self.quitapp,'+')
        
        btcancel = Button2(body,"Annuler")
        btcancel.config(fg=config.powerSettings['fg'], font=config.powerSettings['font'])
        btcancel.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)
        btcancel.bind('<1>', lambda e : self.cancel(),'+')
        
        body.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)

        self.wait_visibility()
        self.grab_set()


        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("%dx%d" % (config.valueDialog['width'],config.valueDialog['height']))
        
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.wait_window(self)
   
    def quitapp(self, event):
        self.withdraw()
        self.update_idletasks()
        self.parent.quit()
        self.destroy()

    def cancel(self):
        self.destroy()


class SettingsLockDialog(tk.Toplevel):

    def __init__(self, parent):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        self.title("Verrouiller")

        self.parent = parent

        self.result = None

        body = tk.Frame(self)
        
        btlock = Button2(body,"Verrouiller")
        btlock.config(bg=config.powerSettings['bg_lock'], fg=config.powerSettings['fg'], font=config.powerSettings['font'])
        btlock.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)
        btlock.bind('<1>', self.lock,'+')
        
        btcancel = Button2(body,"Annuler")
        btcancel.config(fg=config.powerSettings['fg'], font=config.powerSettings['font'])
        btcancel.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)
        btcancel.bind('<1>', lambda e : self.cancel(),'+')
        
        body.pack(padx=5, pady=5,fill=tk.BOTH, expand=1)

        self.wait_visibility()
        self.grab_set()


        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("%dx%d" % (config.valueDialog['width'],config.valueDialog['height']))
        
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.wait_window(self)
   
    def lock(self, event):
        self.withdraw()
        self.update_idletasks()

        LockScreen(self.parent,5).grid(row=0,column=0,columnspan=9,rowspan=6, sticky="news")
        
        self.destroy()

    def cancel(self):
        self.destroy()

class OneValueDialog(Dialog):

    def __init__(self, master, title, setting):
        self.setting = setting
        self.value = setting.value
        Dialog.__init__(self, master, title)


    def body(self, master):


        self.geometry("%dx%d" % (config.valueDialog['width'],config.valueDialog['height']))

        tk.Label(master, text=self.title()).pack(fill=tk.X)
        self.value_var=tk.StringVar()
        self.value_var.set(str(self.value))
        self.label = tk.Label(master, font=(config.valueDialog['font_family'], config.valueDialog['font_size_value']), textvariable=self.value_var).pack(fill=tk.X)

        self.signs = ['--','-','+','++']
        self.buttons = []
        self.frame_buttons=tk.Frame(master)
        for i in range(4):
            self.buttons.append(Button2(self.frame_buttons,content=self.signs[i]))
            self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            self.buttons[i].config(font=config.button['font_big'])
            self.buttons[i].bind('<1>',self.click,'+')
        self.frame_buttons.pack(fill=tk.BOTH, expand=1)



        return self.label # initial focus

    def click(self, event):
        inc=0
        if(event.widget==self.buttons[0]):
            inc=-10
        elif(event.widget==self.buttons[1]):
            inc=-1
        elif(event.widget==self.buttons[2]):
            inc=1
        elif(event.widget==self.buttons[3]):
            inc=10
        val = self.value+self.setting.step*inc
        if isinstance(val, float):
           val = round(val,1)
        if val >= self.setting.vmax:
            val = self.setting.vmax
        elif val <= self.setting.vmin:
            val = self.setting.vmin
        self.value = val
        self.value_var.set(self.value)


    def apply(self):
        self.setting.change(self.value)

class MinMaxDialog(Dialog):

    def __init__(self, master, title, dmin, dmax):
        self.dmin=dmin
        self.dmax=dmax
        Dialog.__init__(self, master, title)

    def body(self, master):
        self.geometry("%dx%d" % (config.minMaxDialog['width'],config.minMaxDialog['height']))

        tk.Label(master, text=self.title()).pack(fill=tk.X)

        fm = tk.Frame(master)
        fm.pack(fill=tk.X,expand=1)
        fv = tk.Frame(master)
        fv.pack(fill=tk.X,expand=1)

        self.signs = ['-Min','+Min','-Max','+Max']
        self.buttons = [None,None, None, None]
        self.frame_buttons=tk.Frame(master)
        self.frame_buttons.pack(fill=tk.BOTH, expand=1)


        if(self.dmin is not None):
            tk.Label(fm, text="Min").pack(side=tk.LEFT,fill=tk.X,expand=1)
            self.vmin_var=tk.IntVar()
            self.vmin_var.set(self.dmin.value)
            self.label = tk.Label(fv, font=(config.minMaxDialog['font_family'],config.minMaxDialog['font_size']), textvariable=self.vmin_var).pack(side=tk.LEFT,fill=tk.X,expand=1)
            for i in [0,1]:
                self.buttons[i]=Button2(self.frame_buttons, content=self.signs[i])
                self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
                self.buttons[i].config(font=config.button['font_big'])
                self.buttons[i].bind('<1>',self.click, '+')
        if(self.dmax is not None):
            tk.Label(fm, text="Max").pack(side=tk.LEFT,fill=tk.X,expand=1)
            self.vmax_var=tk.IntVar()
            self.vmax_var.set(self.dmax.value)
            self.label = tk.Label(fv, font=(config.minMaxDialog['font_family'], config.minMaxDialog['font_size']), textvariable=self.vmax_var).pack(side=tk.LEFT,fill=tk.X,expand=1)
            for i in [2,3]:
                self.buttons[i]=Button2(self.frame_buttons, content=self.signs[i])
                self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
                self.buttons[i].config(font=config.button['font_big'])
                self.buttons[i].bind('<1>',self.click, '+')

        return self.label # initial focus

    def click(self, event):
        if(event.widget==self.buttons[0]):
            val = self.vmin_var.get()-1*self.dmin.step
            if val >= self.dmin.vmin:
                self.vmin_var.set(val)
        elif(event.widget==self.buttons[1]):
            val = self.vmin_var.get()+1*self.dmin.step
            if val <= self.dmin.vmax and (self.dmax is None or val < self.vmax_var.get()):
                self.vmin_var.set(val)
        elif(event.widget==self.buttons[2]):
            val = self.vmax_var.get()-1*self.dmax.step
            if val >= self.dmax.vmin and (self.dmin is None or val > self.vmin_var.get()):
                self.vmax_var.set(val)
        elif(event.widget==self.buttons[3]):
            val = self.vmax_var.get()+1*self.dmax.step
            if val <= self.dmax.vmax:
                self.vmax_var.set(val)

    def apply(self):
        if(self.dmin is not None):
            self.dmin.change(self.vmin_var.get())
        if(self.dmax is not None):
            self.dmax.change(self.vmax_var.get())

class VTDialog(Dialog):

    def __init__(self, master, setting):
        self.setting = setting
        Dialog.__init__(self, master, 'VT')

    def body(self, master):
        self.geometry("%dx%d" % (config.minMaxDialog['width'],config.minMaxDialog['height']))

        tk.Label(master, text=self.title()).pack(fill=tk.X)
        
        tk.Label(master, text="Genre").pack(fill=tk.X)

        fg = tk.Frame(master)
        self.w_button = ButtonPR(fg,"Femme")
        self.w_button.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        self.w_button.push()
        self.w_button.bind('<1>',self.wm_switch,'+')
        self.h_button = ButtonPR(fg,"Homme")
        self.h_button.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        self.h_button.bind('<1>',self.wm_switch,'+')
        fg.pack(fill=tk.X,expand=1)
        
        tk.Label(master, text="Taille").pack(fill=tk.X)
        
        self.size_var=tk.IntVar()
        self.size_var.set(180)
        self.size_label = tk.Label(master, font=(config.newPatientDialog['font_family'], config.newPatientDialog['font_size_size']), textvariable=self.size_var).pack(fill=tk.X)
        
        fsb = tk.Frame(master)
        self.s_minus = Button2(fsb,"-")
        self.s_minus.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        self.s_minus.config(font=(config.newPatientDialog['font_family'], config.newPatientDialog['font_size_button']))
        self.s_minus.bind('<1>',self.size_change,'+')
        self.s_plus = Button2(fsb,"+")
        self.s_plus.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        self.s_plus.config(font=(config.newPatientDialog['font_family'], config.newPatientDialog['font_size_button']))
        self.s_plus.bind('<1>',self.size_change,'+')

        fsb.pack(fill=tk.BOTH,expand=1)
        
        return self # initial focus

    def wm_switch(self, event):
        if(event.widget==self.w_button):
            if(self.w_button.pushed):
                self.h_button.release()
            else:
                self.h_button.push()
                self.h_button.focus_set()
        elif(event.widget==self.h_button):
            if(self.h_button.pushed):
                self.w_button.release()
            else:
                self.w_button.push()
                self.w_button.focus_set()
    def size_change(self,event):
        size =self.size_var.get()
        if(event.widget==self.s_minus):
            size=size-1
            if(size<140):
                size=140
        else:
            size=size+1
            if(size>222):
                size=222
        self.size_var.set(size)

    def apply(self):
        # P = X + 0,91 (taille en cm - 152,4)
        # X= 50 pour les hommes
        # X=45,5 pour les femmes
        # Vt = P * 6ml/kg
        if self.w_button.pushed:
            X = 45.5
        elif self.h_button.pushed:
            X = 50
        P = X + 0.91 * (int(self.size_var.get()) - 152.4)
        vt = round(P * 6)
        self.setting.change(vt)

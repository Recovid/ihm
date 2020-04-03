
# -*- coding: utf-8 -*-
import config
import tkinter as tk
from .helpers import Dialog
from .button import Button2, ButtonPR

class UserInputHandler:

    def plus_handler(self, big=False):
        pass
    def minus_handler(self, big=False):
        pass

    def selected_handler(self):
        pass

    def unselected_handler(self):
        pass

class UserInputManager:
    def __init__(self):
        self.selected=None

    def select(self,handler):
        if(self.selected is not None):
            self.selected.unselected_handler()
        self.selected=handler
        if(self.selected is not None):
            self.selected.selected_handler()


class KeyboardUserInputManager(UserInputManager):
    def __init__(self, app):
        UserInputManager.__init__(self)
        self.app=app
        self.app.bind('<Key>',self.keyinput)

    def keyinput(self,event):
        #print(event)
        if self.selected is not None:
            if(event.keysym=="Left"):
                self.selected.minus_handler()
            elif(event.keysym=="Right"):
                self.selected.plus_handler()

class ButtonUserInputManager(UserInputManager):
    def __init__(self,app):
        UserInputManager.__init__(self)
        self.width = config.buttonUserInput['width_ratio'] # int(app.winfo_screenwidth()*0.2)
        self.height = config.buttonUserInput['height_ratio'] #int(app.winfo_screenheight()*0.09)

        self.font_size = int(self.height*config.buttonUserInput['font_ratio_value'])

        self.canvas = tk.Canvas(app, height=self.height, width=self.width, \
            bg=config.buttonUserInput['background'],borderwidth=0)

        self.signs = ['--','-','+','++']
        self.arrows = ['<<','<','>','>>']
        self.ids_frame = [0,0,0,0]
        self.ids_text = [0,0,0,0]
        for i in range(0,4):
            coord = int(self.width*i/4),int(self.height*0.0),int((i+1)*self.width/4),int(self.height)
            self.ids_frame[i]=self.canvas.create_rectangle(coord,fill='grey',tags='frame_'+str(i))
            self.ids_text[i]=self.canvas.create_text(int(coord[0]+(coord[2]-coord[0])*0.5), int(self.height*0.5), anchor='c', \
                font=(config.buttonUserInput['font_family'], self.font_size),\
                fill=config.buttonUserInput['background'], text=self.signs[i],tags='text_'+str(i))

        self.canvas.itemconfig('all',state="hidden")

        self.canvas.bind('<ButtonPress-1>',self.onClick)
        self.canvas.bind('<ButtonRelease-1>',self.onUnClick)
        self.canvas.bind('<Configure>',self.configure)

    def configure(self,event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())
        self.font_size=int(self.width*0.10)
        for i in range(0,4):
            coords = int(self.width*i/4),int(self.height*0.0),int((i+1)*self.width/4),int(self.height)
            self.canvas.coords(self.ids_frame[i],coords)
            self.canvas.coords(self.ids_text[i],(int(coords[0]+self.width/8),int(self.height/2)))
            self.canvas.itemconfig(self.ids_text[i], font=(config.buttonUserInput['font_family'],self.font_size))

    def select(self, handler, arrows=False):
        UserInputManager.select(self,handler)
        if(handler is not None):
            texts = self.arrows if arrows else self.signs
            for i in range(0,4):
                self.canvas.itemconfig(self.ids_text[i],text=texts[i])
            self.canvas.itemconfig('all',state="normal")
        else:
            self.canvas.itemconfig('all',state="hidden")

    def find_idbutton(self,event):
        iditem = event.widget.find_withtag('current')[0]
        idbutton = None
        try:
            idbutton=self.ids_frame.index(iditem)
        except:
            pass
        try:
            idbutton=self.ids_text.index(iditem)
        except:
            pass
        return idbutton

    def onClick(self,event):
        idbutton = self.find_idbutton(event)
        self.canvas.itemconfigure(self.ids_frame[idbutton],fill=config.buttonUserInput['btn_background_selected'])
        self.canvas.update_idletasks()
        if(self.selected is not None):
            if(idbutton==0):
                self.selected.minus_handler(big=True)
            elif(idbutton==1):
                self.selected.minus_handler(big=False)
            elif(idbutton==2):
                self.selected.plus_handler(big=False)
            elif(idbutton==3):
                self.selected.plus_handler(big=True)

    def onUnClick(self,event):
        idbutton = self.find_idbutton(event)
        self.canvas.itemconfigure(self.ids_frame[idbutton],fill=config.buttonUserInput['btn_background'])
        self.canvas.update_idletasks()

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
                self.buttons[i].bind('<1>',self.click, '+')
        if(self.dmax is not None):
            tk.Label(fm, text="Max").pack(side=tk.LEFT,fill=tk.X,expand=1)
            self.vmax_var=tk.IntVar()
            self.vmax_var.set(self.dmax.value)
            self.label = tk.Label(fv, font=(config.minMaxDialog['font_family'], config.minMaxDialog['font_size']), textvariable=self.vmax_var).pack(side=tk.LEFT,fill=tk.X,expand=1)
            for i in [2,3]:
                self.buttons[i]=Button2(self.frame_buttons, content=self.signs[i])
                self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
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
        vt =int(self.size_var.get())
        self.setting.change(vt)

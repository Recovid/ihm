
# -*- coding: utf-8 -*-
import config
import tkinter as tk
from .helpers import Dialog

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

    def __init__(self, master, title, datamanager):
        self.datamanager=datamanager
        self.value=datamanager.value
        Dialog.__init__(self, master, title)


    def body(self, master):


        self.geometry("%dx%d" % (config.valueDialog['width'],config.valueDialog['height']))

        tk.Label(master, text=self.title()).pack(fill=tk.X)
        self.value_var=tk.StringVar()
        self.value_var.set(str(self.value))
        self.label = tk.Label(master, font=(config.valueDialog['font_family'], config.valueDialog['font_size']), textvariable=self.value_var).pack(fill=tk.X)

        self.signs = ['--','-','+','++']
        self.buttons = []
        self.frame_buttons=tk.Frame(master)
        for i in range(4):
            self.buttons.append(tk.Button(self.frame_buttons, text=self.signs[i]))
            self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
            self.buttons[i].bind('<1>',self.click)
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
        self.value=self.value+self.datamanager.step*inc
        self.value_var.set(self.value)


    def apply(self):
        self.datamanager.update(self.value)

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
                self.buttons[i]=tk.Button(self.frame_buttons, text=self.signs[i])
                self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
                self.buttons[i].bind('<1>',self.click)
        if(self.dmax is not None):
            tk.Label(fm, text="Max").pack(side=tk.LEFT,fill=tk.X,expand=1)
            self.vmax_var=tk.IntVar()
            self.vmax_var.set(self.dmax.value)
            self.label = tk.Label(fv, font=(config.minMaxDialog['font_family'], config.minMaxDialog['font_size']), textvariable=self.vmax_var).pack(side=tk.LEFT,fill=tk.X,expand=1)
            for i in [2,3]:
                self.buttons[i]=tk.Button(self.frame_buttons, text=self.signs[i])
                self.buttons[i].pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
                self.buttons[i].bind('<1>',self.click)







        return self.label # initial focus

    def click(self, event):
        if(event.widget==self.buttons[0]):
            self.vmin_var.set(self.vmin_var.get()-1*self.dmin.step)
        elif(event.widget==self.buttons[1]):
            self.vmin_var.set(self.vmin_var.get()+1*self.dmin.step)
        elif(event.widget==self.buttons[2]):
            self.vmax_var.set(self.vmax_var.get()-1*self.dmax.step)
        elif(event.widget==self.buttons[3]):
            self.vmax_var.set(self.vmax_var.get()+1*self.dmax.step)


    def apply(self):
        if(self.dmin is not None):
            self.dmin.update(self.vmin_var.get())
        if(self.dmax is not None):
            self.dmax.update(self.vmax_var.get())

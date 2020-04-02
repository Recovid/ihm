
# -*- coding: utf-8 -*-
import config
import tkinter as tk
from PIL import Image, ImageTk
import time

class Button():
    def __init__(self,app,id,text, text_push=None):
        self.text = tk.StringVar()
        self.text.set(text)
        self.id = id
        self.text_push = text_push if text_push else text
         
        self.width = config.button['width_ratio']#int(app.winfo_screenwidth()*0.01)
        self.height = config.button['height_ratio']#int(app.winfo_screenheight()*0.01)
        self.font_size=int(self.width/len(self.text.get()))
        #self.font_size = int(self.height*0.22)
        self.font_family = config.button['font_family']

        # self.userinputs=userinputs

        self.canvas = tk.Canvas(app, height=self.height, width=self.width, \
            bg=config.button['background'],borderwidth=0)
        print(self.canvas.winfo_width())
        coord = int(self.width*0.0),int(self.height*0.0),int(self.width),int(self.height)
        self.frame = self.canvas.create_rectangle(coord,fill=config.button['btn_background'],tags='frame')

        #check if text is a text or a file path
        if( text.count('.png') != 0):
            #the path is an image the button should display an icon and not a text
            print("display an icon and not a text:".format(text))
        else:
            self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
            font=(self.font_family,self.font_size),fill=config.button['color_text'], text=self.text.get(),tags='text')


        self.canvas.bind('<ButtonPress-1>',self.onClick)
        self.canvas.bind('<ButtonRelease-1>',self.onUnClick)
        self.canvas.bind('<Configure>',self.configure)
        
    def configure(self,event):
        self.width = int(self.canvas.winfo_width())
        self.height = int(self.canvas.winfo_height())
        self.font_size=int(self.width*config.button['font_ratio_value'])
        coords = 0,0,int(self.width),int(self.height)
        self.canvas.coords(self.frame,coords)
        self.canvas.coords(self.textid,(int(self.width/2),int(self.height/2)))
        self.canvas.itemconfig(self.textid, font=(self.font_family,self.font_size))

    def onClick(self,event):
        self.canvas.itemconfigure('frame',fill=config.button['btn_background_selected'])
        self.canvas.update_idletasks()
    
    def onUnClick(self,event):
        self.canvas.itemconfigure('frame',fill=config.button['btn_background'])
        self.canvas.update_idletasks()

    def push(self):
        self.canvas.itemconfigure('frame',fill=config.button['btn_background_selected'])
        self.canvas.itemconfigure(self.textid, text=self.text_push)
        self.canvas.update_idletasks()
    
    def release(self):
        self.canvas.itemconfigure('frame',fill=config.button['btn_background'])
        self.canvas.itemconfigure(self.textid, text=self.text.get())
        self.canvas.update_idletasks()

    def setText(self, text):
        #check if text is a text or a file path
        if( text.count('.png') != 0):
            #the path is an image the button should display an icon and not a text
            print("display an icon and not a text:".format(text))
        else:
            self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
            font=(self.font_family,self.font_size),fill=config.button['color_text'], text=self.text.get(),tags='text')

class Button2(tk.Button):
    def __init__(self,parent, content=None):
        tk.Button.__init__(self,parent,bg=config.button['btn_background'], activebackground=config.button['btn_background'], fg=config.button['color_text'], activeforeground=config.button['color_text'])
        self.content=content
        if(content is not None):
            self.set_content(content)

        self.bind('<ButtonPress-1>', lambda event : self.config(activebackground=config.button['btn_background_selected']))
        self.bind('<ButtonRelease-1>', lambda event : self.config(activebackground=config.button['btn_background']))

    def resize(self, event):
        if(self.img):
            img = Image.open(self.content).resize(
                (event.width-10, event.height-10), Image.ANTIALIAS
            )
            self.img = ImageTk.PhotoImage(img)
            self.config(image=self.img)

    def set_content(self, content):
        if( content.count('.png') != 0):
            self.img = ImageTk.PhotoImage(
                Image.open(content)
                )
            self.config(image=self.img)
            self.bind('<Configure>', self.resize)
        else:
            self.config(text=content)

class ButtonPR(Button2):
    def __init__(self, parent, content, content_push=None):
        Button2.__init__(self, parent ,content)
        self.pushed=False
        self.content_push=content_push
        self.content=content

        self.bind('<ButtonPress-1>',self.click)
        self.bind('<ButtonRelease-1>',self.unclick)
    def resize(self, event):
        if(self.img):
            img = Image.open(self.content_push if self.content_push is not None and self.pushed else self.content).resize(
                (event.width-10, event.height-10), Image.ANTIALIAS
            )
            self.img = ImageTk.PhotoImage(img)
            self.config(image=self.img)
    def click(self, event):
        if(self.pushed):
            self.pushed=False
            self.config(bg=config.button['btn_background'], activebackground=config.button['btn_background'], default=tk.DISABLED)
            if(self.content_push is not None):
                self.set_content(self.content)
        else:
            self.pushed=True
            self.config(bg=config.button['btn_background_selected'], activebackground=config.button['btn_background_selected'], default=tk.ACTIVE)
            if(self.content_push is not None):
                self.set_content(self.content_push)
        
    def unclick(self, event):
        if(self.pushed):
            self.config(bg=config.button['btn_background_selected'], activebackground=config.button['btn_background_selected'])
        else:
            self.config(bg=config.button['btn_background'], activebackground=config.button['btn_background'])

# app = tk.Tk()
# app.wm_title("Graphe Matplotlib dans Tkinter")

# bti = ButtonInputs(app)
# bti.canvas.pack()
# # btn1 = Button(app,0,'MLrfr')
# # btn1.canvas.pack()
# # s = 0
# # # for i in range(0,400):
# # #     print('debug:',i)
# # #     btn1.update(str(i))
# # #     time.sleep(0.1)
  
# app.mainloop()

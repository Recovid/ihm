
# -*- coding: utf-8 -*-
import config
import tkinter as tk
from PIL import Image, ImageTk
import time

class Button2(tk.Button):
    def __init__(self,parent, content=None):
        tk.Button.__init__(self,parent,font=config.button['font'],bg=config.button['btn_background'], activebackground=config.button['btn_background'], fg=config.button['color_text'], activeforeground=config.button['color_text'])
        if(content is not None):
            self.set_content(content)
        self.bind('<ButtonPress-1>', lambda event : self.config(activebackground=config.button['btn_background_selected']))
        self.bind('<ButtonRelease-1>', lambda event : self.config(activebackground=config.button['btn_background']))

    def set_content(self, content, bg=None):
        if( content.count('.png') != 0):
            img = Image.open(content)
            self.img = ImageTk.PhotoImage(img)
            self.config(image=self.img)
            if(bg is not None):
                self.config(bg=bg, activebackground=bg)
        else:
            self.config(text=content)
        self.update_idletasks()

    def set_background(self, newbg):
        self.config(bg=newbg,activebackground=newbg)

class ButtonPR(Button2):
    def __init__(self, parent, content, content_push=None):
        Button2.__init__(self, parent ,content)
        self.pushed=False
        self.content_push=content_push
        self.content=content

        self.bind('<ButtonPress-1>',self.click)
        self.bind('<ButtonRelease-1>',self.unclick)
    
    def click(self, event):
        if(self.pushed):
            self.release()
        else:
            self.push()
    
    def unclick(self, event):
        if(self.pushed):
            self.config(bg=config.button['btn_background_selected'], activebackground=config.button['btn_background_selected'])
        else:
            self.config(bg=config.button['btn_background'], activebackground=config.button['btn_background'])
    
    def push(self):
        self.pushed=True
        self.config(bg=config.button['btn_background_selected'], activebackground=config.button['btn_background_selected'], default=tk.ACTIVE)
        if(self.content_push is not None):
            self.set_content(self.content_push)

    def release(self):
        self.pushed=False
        self.config(bg=config.button['btn_background'], activebackground=config.button['btn_background'], default=tk.DISABLED)
        if(self.content_push is not None):
            self.set_content(self.content)



# -*- coding: utf-8 -*-
import config
import tkinter as tk
from .button import Button2, ButtonPR


class TitleDialog(tk.Toplevel):

    def __init__(self, parent):
        tk.Toplevel.__init__(self,parent)
        self.transient(parent)
        self.title("Informations")
        self.parent = parent
        self.active_text = tk.StringVar()
        #self.active_text.set("This is a Test")

        self.body = tk.Frame(self)
        self.width = config.titleDialog['width']
        self.height = config.titleDialog['height']


        self.geometry("%dx%d" % (self.width,self.height))
        
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        #tk.Grid.rowconfigure
        tk.Grid.rowconfigure(self.body, 0, weight=1, minsize=self.height/10)
        tk.Grid.rowconfigure(self.body, 3, weight=1, minsize=self.height/8)
        tk.Grid.rowconfigure(self.body, 2, weight=1, minsize=self.height/7)
        tk.Grid.rowconfigure(self.body, 1, weight=1, minsize=self.height/2)
        #for row_index in range(4):
        #    if(row_index == 0):
        #        tk.Grid.rowconfigure(self.body, row_index, weight=1, minsize=self.height/10)
        #    elif(row_index == 3):
        #        tk.Grid.rowconfigure(self.body, row_index, weight=1, minsize=self.height/8)
        #    else:
        #        tk.Grid.rowconfigure(self.body, row_index, weight=1, minsize=self.height/4)
        for column_index in range(3):
            tk.Grid.columnconfigure(self.body, column_index, weight=1, minsize= self.width/3)

        self.head_text = tk.Label(self.body, font=("Helvetica", int(self.height*0.05)), anchor='n', fg='white',bg='#4E69AB', text="Exclusivement pour investigations cliniques")
        self.head_text.grid(row=0, column=0, columnspan=3, sticky="senw")

            #if(column_index == 2):
        self.display = tk.Label(self.body, font=("Helvetica", int(self.height*0.1)), textvariable=self.active_text)
        self.display.grid(row=1, column=0, columnspan=3, sticky="senw")

        self.ref = Button2(self.body, "monitor/Alarms_Icon/Icon_Ref_Produit.png")
        self.ref.grid(row=2,column=0, sticky="senw")
        self.ref.bind('<ButtonPress-1>', self.onPushButtonRef, '+')

        self.util = tk.Label(self.body, font=("Helvetica", int(self.height*0.05)), text="Lire les \n Instructions")
        self.util.grid(row=2, column=1, sticky="senw")


        self.fab = Button2(self.body, "monitor/Alarms_Icon/Icon_Fab.png")
        self.fab.grid(row=2, column=2, sticky="senw")
        self.fab.bind('<ButtonPress-1>', self.onPushButtonFab, '+')

        self.btquit= Button2(self.body, "Quitter")
        self.btquit.config(font=config.powerSettings['font'])
        self.btquit.grid(row=3, column=0, columnspan=3, sticky="senw")
        self.btquit.bind('<1>',self.quitapp,'+')

        self.body.pack(padx=1, pady=1, fill=tk.BOTH, expand=1)

        self.wait_visibility()
        self.grab_set()
        

        self.wait_window(self)


    def quitapp(self, event):
        self.destroy()

    def onPushButtonRef(self, e):
        current_text = config.titleDialog['ref_technique'] + "\n" + 'Version de l\'IHM: ' \
            + config.titleDialog['ihm_version'] + "\n"+ 'Version du controleur: ' + config.titleDialog['ctrl_version']


        self.active_text.set(current_text)
        self.display.config(font=("Helvetica", int(self.height*0.05)))

    def onPushButtonFab(self, e):
        self.active_text.set(config.titleDialog['fab'])
        self.display.config(font=("Helvetica", int(self.height*0.045)))
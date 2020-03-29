import tkinter as tk

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

class ButtonUserInputManager():
    def __init__(self,app):
        UserInputManager.__init__(self)
        self.width = int(app.winfo_screenwidth()*0.2)
        self.height = int(app.winfo_screenheight()*0.09)

        self.font_size = int(self.height*0.35)

        self.canvas = tk.Canvas(app, height=self.height, width=self.width, bg="white",borderwidth=0)
        
        self.signs = ['--','-','+','++']
        self.arrows = ['<<','<','>','>>']
        self.ids_frame = [0,0,0,0]
        self.ids_text = [0,0,0,0]
        for i in range(0,4):
            coord = int(self.width*i/4),int(self.height*0.0),int((i+1)*self.width/4),int(self.height)
            self.ids_frame[i]=self.canvas.create_rectangle(coord,fill='grey',tags='frame_'+str(i))
            self.ids_text[i]=self.canvas.create_text(int(coord[0]+(coord[2]-coord[0])*0.5), int(self.height*0.5), anchor='c', \
                font=("Helvetica", self.font_size),fill='white', text=self.signs[i],tags='text_'+str(i))

        self.canvas.itemconfig('all',state="hidden")
        
        self.canvas.bind('<ButtonPress-1>',self.onClick)
        self.canvas.bind('<ButtonRelease-1>',self.onUnClick)
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
        self.canvas.itemconfigure(self.ids_frame[idbutton],fill="#c9d2e5")
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
        self.canvas.itemconfigure(self.ids_frame[idbutton],fill="grey")
        self.canvas.update_idletasks()



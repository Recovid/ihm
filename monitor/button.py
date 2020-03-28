import tkinter as tk
import time

class Button():
    def __init__(self,app,id,text, text_push=None):
        self.text = tk.StringVar()
        self.text.set(text)
        self.id = id
        self.text_push = text_push if text_push else text
         
        self.width = int(app.winfo_screenwidth()*0.09)
        self.height = int(app.winfo_screenheight()*0.09)
        # self.width = int(800*0.09) #150
        # self.height = int(600*0.09) #100

        self.font_size = int(self.height*0.16)
        
        

        # self.userinputs=userinputs

        self.canvas = tk.Canvas(app, height=self.height, width=self.width, bg="#c9d2e5",borderwidth=0)
        coord = int(self.width*0.0),int(self.height*0.0),int(self.width),int(self.height)
        self.frame = self.canvas.create_rectangle(coord,fill='grey',tags='frame')
        self.textid = self.canvas.create_text(int(self.width*0.5), int(self.height*0.5), anchor='c', \
        		font=("Helvetica", self.font_size),fill='white', text=self.text.get(),tags='text')
        
        self.canvas.bind('<ButtonPress-1>',self.onClick)
        self.canvas.bind('<ButtonRelease-1>',self.onUnClick)
        

    def onClick(self,event):
        self.canvas.itemconfigure('frame',fill="#c9d2e5")
        self.canvas.update_idletasks()
    
    def onUnClick(self,event):
        self.canvas.itemconfigure('frame',fill="grey")
        self.canvas.update_idletasks()

    def push(self):
        self.canvas.itemconfigure('frame',fill="#c9d2e5")
        self.canvas.itemconfigure(self.textid, text=self.text_push)
        self.canvas.update_idletasks()
    
    def release(self):
        self.canvas.itemconfigure('frame',fill="grey")
        self.canvas.itemconfigure(self.textid, text=self.text.get())
        self.canvas.update_idletasks()

class ButtonInputs():
    def __init__(self,app, userinputs):
        self.userinputs=userinputs
        self.width = int(app.winfo_screenwidth()*0.2)
        self.height = int(app.winfo_screenheight()*0.09)

        self.font_size = int(self.height*0.35)

        self.canvas = tk.Canvas(app, height=self.height, width=self.width, bg="#c9d2e5",borderwidth=0)
        
        self.buttons = ['--','-','+','++']
        self.ids_frame = [0,0,0,0]
        self.ids_text = [0,0,0,0]
        for i in range(0,4):
            coord = int(self.width*i/4),int(self.height*0.0),int((i+1)*self.width/4),int(self.height)
            self.ids_frame[i]=self.canvas.create_rectangle(coord,fill='grey',tags='frame_'+str(i))
            self.ids_text[i]=self.canvas.create_text(int(coord[0]+(coord[2]-coord[0])*0.5), int(self.height*0.5), anchor='c', \
                font=("Helvetica", self.font_size),fill='white', text=self.buttons[i],tags='text_'+str(i))

        self.canvas.bind('<ButtonPress-1>',self.onClick)
        self.canvas.bind('<ButtonRelease-1>',self.onUnClick)
   
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
        if(self.userinputs.selected is not None):
            if(idbutton==0):
                self.userinputs.selected.minus_handler(big=True)
            elif(idbutton==1):
                self.userinputs.selected.minus_handler(big=False)
            elif(idbutton==2):
                self.userinputs.selected.plus_handler(big=False)
            elif(idbutton==3):
                self.userinputs.selected.plus_handler(big=True)

    def onUnClick(self,event):
        idbutton = self.find_idbutton(event)
        self.canvas.itemconfigure(self.ids_frame[idbutton],fill="grey")
        self.canvas.update_idletasks()


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

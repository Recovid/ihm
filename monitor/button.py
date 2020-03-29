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

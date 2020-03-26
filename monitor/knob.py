import tkinter as tk
import time

class Knob:
	def __init__(self,app,min_range,max_range,id,unit,title):
		self.value = 0.0
		self.max_range = max_range
		self.min_range = min_range
		self.state = 0
		self.id = id
		self.unit = unit
		self.title = title

		self.width = 100
		self.height = 100

		self.canvas = tk.Canvas(app, height=self.height, width=self.width)
		coord = int(self.width*0.1), int(self.height*0.1), int(self.width*0.9), int(self.height*0.9)
		self.arc_green = self.canvas.create_arc(coord, start=-45, extent=270, fill="#4E69AB")

		self.arc_grey = self.canvas.create_arc(coord, start=-45, extent=270, fill="grey",tags='knob_value'+str(self.id))

		coord = int(self.width*0.2), int(self.height*0.2), int(self.width*0.8), int(self.height*0.8)
		self.circle = self.canvas.create_oval(coord, fill="grey", width=2,tags='knob_circle'+str(self.id))

		self.canvas.create_text(int(self.width*0.5), int(self.height*0.4), anchor='c', \
				font=("Helvetica", 22),fill='white', text=str(0),tags='knob_value_text'+str(self.id))
		self.canvas.create_text(int(self.width*0.5), int(self.height*0.68), anchor='s', \
				font=("Helvetica", 10),fill='white', text=self.unit,tags='knob_value_unit'+str(self.id))
		self.canvas.create_text(int(self.width*0.5), int(self.height*0.98), anchor='s', \
				font=("Helvetica", 15),fill='grey', text=self.title)

		self.canvas.create_text(int(self.width*0.2), int(self.height*0.85), anchor='e', \
				font=("Helvetica", 12),fill='grey', text=self.min_range)

		self.canvas.create_text(int(self.width*0.8), int(self.height*0.85), anchor='w', \
				font=("Helvetica", 12),fill='grey', text=self.max_range)		

		
		self.canvas.tag_bind('knob_circle'+str(self.id), '<ButtonPress-1>',self.onClick)
		self.canvas.tag_bind('knob_value_text'+str(self.id), '<ButtonPress-1>',self.onClick)
		self.canvas.tag_bind('knob_value_unit'+str(self.id), '<ButtonPress-1>',self.onClick)
		self.canvas.bind('<Motion>', self.motion)
		
		self.timer()
		

	def update(self,value):
		if value>self.min_range and value <=self.max_range:
			if self.state==1:
				self.value = value
				self.value_norm = 270 - (((self.value/self.max_range) + self.min_range)*270)
				print('v:',self.value,' vn:',self.value_norm)
				item_txt = self.canvas.find_withtag("knob_value"+str(self.id))
				self.canvas.itemconfigure(item_txt,extent=self.value_norm)
				item_txt = self.canvas.find_withtag("knob_value_text"+str(self.id))
				self.canvas.itemconfigure(item_txt,text=str(value))
				self.canvas.update()
		
	def onClick(self,event):
		self.state = 1
		self.canvas.itemconfigure('knob_circle'+str(self.id), fill='#c9d2e5')
		

	def motion(self,event):
		if self.state==1:
		    x, y = event.x, event.y
		    print('{}, {}'.format(x, y))
		    self.update(y)

	def timer(self):
		if self.state==1:
			self.state = 0
			self.canvas.itemconfigure('knob_circle'+str(self.id), fill='gray')
		self.canvas.after(5000, self.timer)	    

		


# Programme de test

# app = tk.Tk()
# app.wm_title("Graphe Matplotlib dans Tkinter")

# btn1 = Knob(app, 0, 400,0,'MLrfr','VT')
# btn2 = Knob(app, 0, 30,1,'MLrfr','VT')
# btn3 = Knob(app, 0, 50,2,'MLrfr','VT')
# btn1.canvas.pack()
# btn2.canvas.pack()
# btn3.canvas.pack()

# # for i in range(0,400):
# # 	btn1.update(i)
# # 	btn2.update(i)
# # 	btn3.update(i)
# # 	time.sleep(0.1)
# app.mainloop()
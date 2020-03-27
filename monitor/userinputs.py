
class UserInputHandler:

    def left_handler(self):
        pass
    def right_handler(self):
        pass

    def selected_handler(self):
        pass

    def unselected_handler(self):
        pass

class UserInputManager:
    def __init__(self):
        self.handlers=[]
        self.selected=None

    def append_handler(self, handler):
        self.handlers.append(handler)

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
                self.selected.left_handler()
            elif(event.keysym=="Right"):
                self.selected.right_handler()



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


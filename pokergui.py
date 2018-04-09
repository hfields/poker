from tkinter import *

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.drawShapes()
        #self.createWidgets()
        self.number = 0

    def createWidgets(self):
        self.INCREASE = Button(self, text = "INC", fg = "blue", command = self.increase)
        self.INCREASE.pack({"side": "left"})
        self.DECREASE = Button(self, text = "DEC", fg = "blue", command = self.decrease)
        self.DECREASE.pack({"side": "left"})
        self.DIE = Button(self, text = "DIE", fg = "blue", command = self.quit)
        self.DIE.place(x = 500, y = 250)

    def drawShapes(self):
        #self.BACKGROUND = Canvas(self, width = 1000, height = 500, bg = 'green')
        #self.BACKGROUND.pack()
        self.IMAGE1 = Canvas(self)
        self.IMAGE1.pack()
        img1 = PhotoImage(master = self, file = "stock1.png")
        self.IMAGE1.create_image(0, 0, image = img1)

    def increase(self):
        self.number += 1
        print(self.number)

    def decrease(self):
        self.number -= 1
        print(self.number)



top = Tk()
top.geometry("1000x500")
app = Application(master=top)


app.mainloop()
top.destroy()
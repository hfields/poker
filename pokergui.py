from tkinter import *
from cards import *

"""
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

"""
# Initialize global variables for the gamestate and deck
state = "preflop"
deck = Deck()

# Initialize global variables for the community cards
boardImages = []
boardLabels = []
faceupBoard = []

# Initialize global variables for players and their hands
numPlayers = 2
handWindows = []
hands = []
handImages = []
handLabels = []

def clearBoard():
    """ Destroys all labels and images associated with the board and resets the
    boardImages and boardLabels lists to empty"""
    global boardImages
    global boardLabels
    
    for label in boardLabels:
        label.destroy()

    for image in boardImages:
        image.__del__()

    boardImages = []
    boardLabels = []

def clearHands():
    """ Destroys the player hands along with all labels and images associated with them,
    then resets all associated lists to empty"""
    global hands
    global handImages
    global handLabels

    for label in handLabels:
        label.destroy()

    for image in handImages:
        image.__del__()

    for hand in hands:
        del hand

    hands = []
    handImages = []
    handLabels = []

def addCards(root, cards):
    """ Creates labels for cards on the board"""
    global boardImages
    global boardLabels

    clearBoard()
    
    for card in cards:
        boardImages += [PhotoImage(file ="Cards/" + repr(card) + ".png")]

    for image in boardImages:
        boardLabels += [Label(root, image = image)]

    for label in boardLabels:
        label.pack(side = "left")

def dealBoard():
    """ Deals the community cards to the board"""
    global state
    global deck
    global faceupBoard

    # Switch depending on the game state
    if state == "preflop":
        # Burn one and deal 3 cards, then switch gamestate to flop
        print("Dealing the flop...")
        deck.burn()

        faceupBoard += deck.deal(3)
        addCards(top, faceupBoard)

        state = "flop"

    elif state == "flop":
        # Burn one and deal one card, then switch gamestate to turn
        print("Dealing the turn...")
        deck.burn()

        faceupBoard += deck.deal(1)
        addCards(top, faceupBoard)

        state = "turn"

    elif state == "turn":
        # Burn one and deal one card, then switch gamestate to river
        print("Dealing the river...")
        deck.burn()

        faceupBoard += deck.deal(1)
        addCards(top, faceupBoard)

        state = "river"

    else:
        # Reset the deck, clear the existing widgets and reset gamestate to preflop
        print("Resetting deck...")
        deck.reset()

        clearBoard()
        clearHands()
        faceupBoard = []

        state = "preflop"

def dealPlayers():
    global deck
    global hands
    global handWindows
    global handImages
    global handLabels

    for i in range(0, numPlayers):
        hands += [Hand(2).fillHand(deck)]

        for card in hands[i].cards:
            handImages += [PhotoImage(master = handWindows[i], file ="Cards/" + repr(card) + ".png")]
    
        for image in handImages[i * 2:]:
            handLabels += [Label(handWindows[i], image = image)]

    for label in handLabels:
        label.pack(side = "left")

top = Tk()

for i in range(0, numPlayers):
    handWindows += [Tk()]
    handWindows[i].geometry("600x300")
    playerString = "Player " + str(i + 1)
    Label(handWindows[i], text = playerString).pack(side = "top")

top.geometry("1200x300")

dealBoardButton = Button(top, 
                   text="Deal to board", 
                   fg="red",
                   command=dealBoard).pack()

dealHandButton = Button(top, 
                   text="Deal to players", 
                   fg="red",
                   command=dealPlayers).pack()

burnImage = PhotoImage(file = "Cards/Facedown.png")
burnCard = Label(image=burnImage).pack(side = "left")

top.mainloop()

top.destroy()
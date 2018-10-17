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
handImages = {}
handLabels = {}

def clearBoard():
    """ Destroys all labels and images associated with the board and resets the
    boardImages and boardLabels lists to empty"""
    global boardImages
    global boardLabels
    
    # Iterate through labels and images in boardLabels and boardImages and delete them
    for label in boardLabels:
        label.destroy()

    for image in boardImages:
        image.__del__()

    # Reset boardImages and boardLabels
    boardImages = []
    boardLabels = []

def clearHands():
    """ Destroys the player hands along with all labels and images associated with them,
    then resets all associated lists to empty"""
    global hands
    global handImages
    global handLabels

    # Iterate through each entry in handLabels and handImages and delete each image and label
    for i in range(0, numPlayers):
        for label in handLabels[i]:
            label.destroy()

        for image in handImages[i]:
            image.__del__()

    # Delete all hands
    for hand in hands:
        del hand

    # Reset global variables
    hands = []
    handImages = {}
    handLabels = {}

def addCards(root, cards):
    """ Creates labels for cards on the board"""
    global boardImages
    global boardLabels

    # Track where the next images will be added to boardImages
    nextIndex = len(boardImages)
    
    # Add images for the given cards to boardImages
    for card in cards:
        boardImages += [PhotoImage(master = root, file ="Cards/" + repr(card) + ".png")]

    # Add labels for all of the new images
    for image in boardImages[nextIndex:]:
        boardLabels += [Label(root, image = image)]

    # Pack the labels into the top window
    for label in boardLabels[nextIndex:]:
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

        flop = deck.deal(3)
        faceupBoard += flop
        addCards(top, flop)

        state = "flop"

    elif state == "flop":
        # Burn one and deal one card, then switch gamestate to turn
        print("Dealing the turn...")
        deck.burn()

        turn = deck.deal(1)
        faceupBoard += turn
        addCards(top, turn)

        state = "turn"

    elif state == "turn":
        # Burn one and deal one card, then switch gamestate to river
        print("Dealing the river...")
        deck.burn()

        river = deck.deal(1)
        faceupBoard += river
        addCards(top, river)

        print(HandHelper.findWinner(hands, faceupBoard))

        state = "river"

    else:
        # Reset the deck, clear the existing widgets and reset gamestate to preflop
        print("Resetting deck...")

        deck.reset()

        clearBoard()
        clearHands()
        faceupBoard = []

        state = "preflop"

def flipCards(playerIndex):
    global hands
    global handWindows
    global handImages
    global handLabels

    # If the cards are face-up, flip them face-down
    if hands[playerIndex].faceUp:
        # Delete the labels in this player's entry in handLabels
        for label in handLabels[playerIndex]:
            label.destroy()

        handLabels[playerIndex] = []

        # Create labels for face-down cards
        for i in range(0, 2):
            handLabels[playerIndex] += [Label(handWindows[playerIndex], image = handImages[playerIndex][0])]

        # Display labels on window
        for label in handLabels[playerIndex]:
            label.pack(side = "left")

    # If the cards are face-down, flip them face-ups
    else:
        # Delete the labels in this player's entry in handLabels
        for label in handLabels[playerIndex]:
            label.destroy()

        handLabels[playerIndex] = []

        # Create labels for face-down cards
        for image in handImages[playerIndex][1:]:
            handLabels[playerIndex] += [Label(handWindows[playerIndex], image = image)]

        # Display labels on window
        for label in handLabels[playerIndex]:
            label.pack(side = "left")

    # Flip the faceUp property of the given hand
    hands[playerIndex].flip()

def dealPlayers():
    global deck
    global hands
    global handWindows
    global handImages
    global handLabels

    # Create hands for as many players as designated by numPlayers
    for i in range(0, numPlayers):
        hands += [Hand(2).fillHand(deck)]
        handImages[i] = []
        handLabels[i] = []

        # Add the face-down card image to this entry of handImages
        handImages[i] += [PhotoImage(master = handWindows[i], file ="Cards/Facedown.png")]

        # Add the face-up images of the cards in the current hand to this entry of handImages
        for card in hands[i].cards:
            handImages[i] += [PhotoImage(master = handWindows[i], file ="Cards/" + repr(card) + ".png")]

        # Create labels for face-down cards
        for j in range(0, 2):
            handLabels[i] += [Label(handWindows[i], image = handImages[i][0])]

        # Display labels on window
        for label in handLabels[i]:
            label.pack(side = "left")

# Create the top level window
top = Tk()
top.geometry("1200x300")

# Add buttons and a face-down card to top
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

# Create new windows for each player
for i in range(0, numPlayers):
    handWindows += [Tk()]
    handWindows[i].geometry("600x300")
    playerString = "Player " + str(i + 1)
    Label(handWindows[i], text = playerString).pack(side = "top")
    Button(handWindows[i], 
        text = "Flip cards",
        fg = "red",
        command=lambda i=i: flipCards(i)).pack()  

top.mainloop()
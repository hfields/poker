from tkinter import *
from cards import *

class Application():
    def __init__(self, numPlayers, master, state = "preflop"):
        self.state = state
        self.master = master
        self.numPlayers = numPlayers
        self.deck = Deck()
        self.boardImages = []
        self.boardLabels = []
        self.faceupBoard = []
        self.handWindows = []
        self.hands = []
        self.handImages = {}
        self.handLabels = {}

        # Add buttons and a face-down card to top
        dealBoardButton = Button(top, 
                        text="Deal to board", 
                        fg="red",
                        command=lambda: self.dealBoard()).pack()

        dealHandButton = Button(top, 
                        text="Deal to players", 
                        fg="red",
                        command=lambda: self.dealPlayers()).pack()

        self.burnImage = PhotoImage(file = "Cards/Facedown.png")
        burnCard = Label(image=self.burnImage).pack(side = "left")
  
        # Create new windows for each player
        for i in range(0, self.numPlayers):
            self.handWindows += [Tk()]
            self.handWindows[i].geometry("600x300")
            playerString = "Player " + str(i + 1)
            Label(self.handWindows[i], text = playerString).pack(side = "top")
            Button(self.handWindows[i], 
                text = "Flip cards",
                fg = "red",
                command=lambda i=i: self.flipCards(i)).pack()
        
    def clearBoard(self):
        """ Destroys all labels and images associated with the board and resets the
        boardImages and boardLabels lists to empty"""
        
        # Iterate through labels and images in boardLabels and boardImages and delete them
        for label in self.boardLabels:
            label.destroy()

        for image in self.boardImages:
            image.__del__()

        # Reset boardImages and boardLabels
        self.boardImages = []
        self.boardLabels = []

    def clearHands(self):
        """ Destroys the player hands along with all labels and images associated with them,
        then resets all associated lists to empty"""

        # Iterate through each entry in handLabels and handImages and delete each image and label
        for i in range(0, self.numPlayers):
            for label in self.handLabels[i]:
                label.destroy()

            for image in self.handImages[i]:
                image.__del__()

        # Delete all hands
        for hand in self.hands:
            del hand

        # Reset global variables
        self.hands = []
        self.handImages = {}
        self.handLabels = {}

    def addCards(self, cards):
        """ Creates labels for cards on the board"""

        # Track where the next images will be added to boardImages
        nextIndex = len(self.boardImages)
        
        # Add images for the given cards to boardImages
        for card in cards:
            self.boardImages += [PhotoImage(master = self.master, file ="Cards/" + repr(card) + ".png")]

        # Add labels for all of the new images
        for image in self.boardImages[nextIndex:]:
            self.boardLabels += [Label(self.master, image = image)]

        # Pack the labels into the top window
        for label in self.boardLabels[nextIndex:]:
            label.pack(side = "left")

    def dealBoard(self):
        """ Deals the community cards to the board"""

        # Switch depending on the game state
        if self.state == "preflop":
            # Burn one and deal 3 cards, then switch gamestate to flop
            print("Dealing the flop...")
            self.deck.burn()

            flop = self.deck.deal(3)
            self.faceupBoard += flop
            self.addCards(flop)

            self.state = "flop"

        elif self.state == "flop":
            # Burn one and deal one card, then switch gamestate to turn
            print("Dealing the turn...")
            self.deck.burn()

            turn = self.deck.deal(1)
            self.faceupBoard += turn
            self.addCards(turn)

            self.state = "turn"

        elif self.state == "turn":
            # Burn one and deal one card, then switch gamestate to river
            print("Dealing the river...")
            self.deck.burn()

            river = self.deck.deal(1)
            self.faceupBoard += river
            self.addCards(river)

            print(HandHelper.findWinner(self.hands, self.faceupBoard))

            self.state = "river"

        else:
            # Reset the deck, clear the existing widgets and reset gamestate to preflop
            print("Resetting deck...")

            self.deck.reset()

            self.clearBoard()
            self.clearHands()
            self.faceupBoard = []

            self.state = "preflop"

    def flipCards(self, playerIndex):
        # If the cards are face-up, flip them face-down
        if self.hands[playerIndex].faceUp:
            # Delete the labels in this player's entry in self.handLabels
            for label in self.handLabels[playerIndex]:
                label.destroy()

            self.handLabels[playerIndex] = []

            # Create labels for face-down cards
            for i in range(0, 2):
                self.handLabels[playerIndex] += [Label(self.handWindows[playerIndex], image = self.handImages[playerIndex][0])]

            # Display labels on window
            for label in self.handLabels[playerIndex]:
                label.pack(side = "left")

        # If the cards are face-down, flip them face-ups
        else:
            # Delete the labels in this player's entry in self.handLabels
            for label in self.handLabels[playerIndex]:
                label.destroy()

            self.handLabels[playerIndex] = []

            # Create labels for face-down cards
            for image in self.handImages[playerIndex][1:]:
                self.handLabels[playerIndex] += [Label(self.handWindows[playerIndex], image = image)]

            # Display labels on window
            for label in self.handLabels[playerIndex]:
                label.pack(side = "left")

        # Flip the faceUp property of the given hand
        self.hands[playerIndex].flip()

    def dealPlayers(self):
        # Create hands for as many players as designated by numPlayers
        for i in range(0, self.numPlayers):
            self.hands += [Hand(2).fillHand(self.deck)]
            self.handImages[i] = []
            self.handLabels[i] = []

            # Add the face-down card image to this entry of self.handImages
            self.handImages[i] += [PhotoImage(master = self.handWindows[i], file ="Cards/Facedown.png")]

            # Add the face-up images of the cards in the current hand to this entry of self.handImages
            for card in self.hands[i].cards:
                self.handImages[i] += [PhotoImage(master = self.handWindows[i], file ="Cards/" + repr(card) + ".png")]

            # Create labels for face-down cards
            for j in range(0, 2):
                self.handLabels[i] += [Label(self.handWindows[i], image = self.handImages[i][0])]

            # Display labels on window
            for label in self.handLabels[i]:
                label.pack(side = "left")

# Create the top level window
top = Tk()
top.geometry("1200x300")

app = Application(2, top)

top.mainloop()
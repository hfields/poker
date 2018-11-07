from tkinter import *
from cards import *
from pokerchips import *
from functools import *

class Application():
    def __init__(self, table, master, state = "preRound"):
        self.state = state
        self.master = master
        self.table = table
        self.playerNames = list(map(lambda x: x.name, table.allPlayers))
        self.numPlayers = len(self.playerNames)
        self.startingChips = table.allPlayers[0].chips
        self.deck = Deck()
        self.boardImages = []
        self.boardLabels = []
        self.faceupBoard = []
        self.handWindows = []
        self.hands = []
        self.chipCounts = []
        self.handImages = {}
        self.handLabels = {}
        self.round = 0
        self.stopBetting = False

        # Add buttons and a face-down card to top
        self.proceedButton = Button(self.master, 
                        text="Proceed", 
                        fg="red",
                        command=lambda: self.proceed())
        self.proceedButton.pack()

        quitButton = Button(self.master, 
                        text="Quit", 
                        fg="red",
                        command= self.master.destroy).pack(side = "bottom")
    
        self.burnImage = PhotoImage(file = "Cards/Facedown.png")
        burnCard = Label(image=self.burnImage).pack(side = "left")
  
        # Create new windows for each player
        for i in range(0, self.numPlayers):
            self.handWindows += [Toplevel()]
            self.handWindows[i].geometry("600x300")
            chipCount = StringVar()
            self.chipCounts += [chipCount]
            
            chipCount.set("Chips: " + str(self.startingChips))

            playerString = "Player " + str(i + 1) + ": " + self.playerNames[i]
            Label(self.handWindows[i], text = playerString).pack(side = "top")
            Label(self.handWindows[i], textvariable = chipCount).pack(side = "top")

            Button(self.handWindows[i], 
                text = "Flip cards",
                fg = "red",
                command=lambda i=i: self.flipCards(i)).pack()

    def proceed(self):
        """ Proceeds to the next step in the game, based on the current state and certain
        table conditions"""
        if self.state == "preRound":
            print("PRE-FLOP")

            # Disable Proceed button
            self.proceedButton.config(state = DISABLED)

            # Reset stopBetting and update state
            self.stopBetting = False
            self.state = "preflop"
            
            # Deal players and run a pre-flop betting rotation
            self.dealPlayers()
            table.getPreFlopRotation(self.round)
            self.stopBetting = self.table.preflop()

            # Re-enable the Proceed button and check to see if betting should stop
            self.proceedButton.config(state = NORMAL)
            self.stopBetting = self.stopBetting or self.table.allPlayersAllin()
            
            # If betting should stop, automatically proceed through dealing the cards
            if self.stopBetting:
                self.proceed()
            
            # Otherwise, prompt to proceed to the flop
            else:
                self.updateChips()
                print("Pre-flop betting concluded. Press Proceed to deal flop")
        
        else:
            self.dealBoard()

    def dealBoard(self):
        """ Deals the community cards to the board"""
        # Switch depending on the game state
        if self.state == "preflop":
            # Disable Proceed button
            self.proceedButton.config(state = DISABLED)

            # Burn one and deal 3 cards, then switch gamestate to flop
            self.deck.burn()

            flop = self.deck.deal(3)
            self.faceupBoard += flop
            self.addCards(flop)

            self.state = "flop"

            # If betting has already stopped, automatically proceed to the end
            if self.stopBetting:
                self.proceed()

            else:
                # Conduct flop betting
                print("FLOP")
                self.table.getRotation(self.round)

                # Run a betting rotation
                self.stopBetting = self.table.postflop()

                # Re-enable the Proceed button and check to see if betting should continue
                self.proceedButton.config(state = NORMAL)
                self.stopBetting = self.stopBetting or self.table.allPlayersAllin()

                # If betting should stop, automatically proceed to the end
                if self.stopBetting:
                    self.proceed()

                else:
                    self.updateChips()
                    print("Flop betting concluded. Press Proceed to deal turn")

        elif self.state == "flop":
            # Disable Proceed button
            self.proceedButton.config(state = DISABLED)

            # Burn one and deal one card, then switch gamestate to turn
            self.deck.burn()

            turn = self.deck.deal(1)
            self.faceupBoard += turn
            self.addCards(turn)

            self.state = "turn"

            # If betting has already stopped, automatically proceed to the end
            if self.stopBetting:
                self.proceed()

            else:
                # Conduct turn betting
                print("TURN")
                self.table.getRotation(self.round)
                
                # Run a betting rotation
                self.stopBetting = self.table.postflop()

                # Re-enable the Proceed button and check to see if betting should continue
                self.proceedButton.config(state = NORMAL)
                self.stopBetting = self.stopBetting or self.table.allPlayersAllin()

                # If betting should stop, automatically proceed to the end
                if self.stopBetting:
                    self.proceed()

                else:
                    self.updateChips()
                    print("Turn betting concluded. Press Proceed to deal river")

        elif self.state == "turn":
            # Disable Proceed button
            self.proceedButton.config(state = DISABLED)

            # Burn one and deal one card, then switch gamestate to river
            self.deck.burn()

            river = self.deck.deal(1)
            self.faceupBoard += river
            self.addCards(river)

            self.state = "river"

            # If betting has already stopped, automatically proceed to the end
            if self.stopBetting:
                self.proceed()

            else:
                # Conduct river betting
                print("RIVER")
                self.table.getRotation(self.round)

                # Run a betting rotation
                self.table.postflop()

                # Re-enable the Proceed button
                self.proceedButton.config(state = NORMAL)

                self.updateChips()
                print("All betting concluded. Press Proceed to resolve pots.")

        elif self.state == "river":
            # Disable proceed button and resolve pots 
            self.proceedButton.config(state = DISABLED)

            self.table.resolvePots(self.faceupBoard)

            # Re-enable the Proceed button and switch gamestate to postRound
            self.proceedButton.config(state = NORMAL)
            self.state = "postRound"

            self.updateChips()
            print("Pots resolved. Press Proceed to go to next round.")

        else:
            # Reset the deck, increment round, clear the existing widgets and reset gamestate to preflop
            self.round += 1
            print("Round", self.round + 1)

            self.deck.reset()

            self.clearBoard()
            self.clearHands()
            self.faceupBoard = []

            self.state = "preRound"

    def updateChips(self):
        """ Updates the chip counts of every player in the game."""
        for i in range(0, len(self.table.allPlayers)):
            self.chipCounts[i].set("Chips: " + str(self.table.allPlayers[i].chips))

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

    def flipCards(self, playerIndex):
        """ Flip the cards in a given player's window"""
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
        """ Deal cards to the windows representing each Hand"""
        # Create hands for as many players as designated by numPlayers
        for i in range(0, self.numPlayers):
            # Create a hand for each player and add that hand to the hands attribute so it can be displayed
            newHand = Hand(2).fillHand(self.deck)
            table.Players[i].hand = newHand
            self.hands += [newHand]
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

# Initialize the poker table
table = Table()

# Get the players and blinds
table.getPlayers()
table.getBlinds()

# Create the top level window
top = Tk()
top.geometry("1200x300")

app = Application(table, top)

print("Round", app.round + 1)

top.mainloop()

del table
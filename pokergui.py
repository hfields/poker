from tkinter import *
from cards import *
from pokerchips import *
from functools import *

class Application():
    def __init__(self, table, master, state = "preRound"):
        self.state = state
        self.states = ["preRound", "preflopBetting", "preflop", "flopBetting", "flop", "turnBetting", "turn", "riverBetting", "river", "postRound"]
        self.master = master
        self.table = table
        
        self.playerNames = list(map(lambda x: x.name, table.allPlayers))
        self.numPlayers = len(self.playerNames)
        self.numActivePlayers = self.numPlayers
        self.startingChips = table.allPlayers[0].chips
        
        self.deck = Deck()
        self.boardImages = []
        self.boardLabels = []
        self.faceupBoard = []
        
        # Player window variables
        self.handWindows = []
        self.hands = {}
        self.chipCounts = []
        self.bets = []
        self.handImages = {}
        self.handLabels = {}
        self.callButtons = {}
        self.raiseButtons = {}
        self.raiseSliders = {}
        self.allinButtons = {}
        self.foldButtons = {}

        # Main window label variables
        self.currentBet = StringVar()
        self.potString = StringVar()
        
        # Variables for conducting betting
        self.round = 0
        self.rotationQueue = []
        self.stopBetting = False
        self.bettingOngoing = False

        # Add buttons and a face-down card to main window
        self.proceedButton = Button(self.master, 
                        text="Proceed", 
                        fg="red",
                        command=lambda: self.proceed())
        self.proceedButton.pack()

        # Add a quit button to close all windows
        quitButton = Button(self.master, 
                        text="Quit", 
                        fg="red",
                        command= self.master.destroy).pack(side = "bottom")
    
        self.burnImage = PhotoImage(file = "Cards/Facedown.png")
        burnCard = Label(image=self.burnImage).pack(side = "left")

        # Add a label for the current bet and the pots
        self.currentBet.set("Current bet: 0")
        Label(textvariable = self.currentBet).pack(side = "top")
        self.potString.set("Main pot: 0")
        Label(textvariable = self.potString).pack(side = "top")
  
        # Create new windows for each player
        for i in range(0, self.numPlayers):
            self.handWindows += [Toplevel()]
            self.handWindows[i].geometry("600x400")
            chipCount = StringVar()
            bet = StringVar()
            self.chipCounts += [chipCount]
            self.bets += [bet]
            
            chipCount.set("Chips: " + str(self.startingChips))
            bet.set("Bet: 0")

            playerString = "Player " + str(i + 1) + ": " + self.playerNames[i]
            Label(self.handWindows[i], text = playerString).pack(side = "top")
            Label(self.handWindows[i], textvariable = chipCount).pack(side = "top")
            Label(self.handWindows[i], textvariable = bet).pack(side = "top")

            Button(self.handWindows[i], 
                text = "Flip cards",
                fg = "red",
                command=lambda i=i: self.flipCards(i)).pack()
            
            # Initialize betting option buttons for the window
            callButton = Button(self.handWindows[i], 
                text = "Call",
                fg = "red",
                state = DISABLED,
                command=lambda i=i: self.setBet(self.table.allPlayers[i], "c"))
            
            raiseButton = Button(self.handWindows[i], 
                text = "Raise",
                fg = "red",
                state = DISABLED,
                command=lambda i=i: self.setBet(self.table.allPlayers[i], "r"))

            # Invert to and from_ so that slider increases upward
            raiseSlider = Scale(self.handWindows[i],
                to = self.table.bigBlind,
                from_ = self.startingChips - self.table.bigBlind,
                state = DISABLED)

            # Start slider at bottom
            raiseSlider.set(self.table.bigBlind)

            allinButton = Button(self.handWindows[i], 
                text = "All-in",
                fg = "red",
                state = DISABLED,
                command=lambda i=i: self.setBet(self.table.allPlayers[i], "a"))

            foldButton = Button(self.handWindows[i], 
                text = "Fold",
                fg = "red",
                state = DISABLED,
                command=lambda i=i: self.setBet(self.table.allPlayers[i], "f"))

            # Track the buttons/sliders in their appropriate dictionaries
            self.callButtons[i] = callButton
            self.raiseSliders[i] = raiseSlider
            self.raiseButtons[i] = raiseButton
            self.allinButtons[i] = allinButton
            self.foldButtons[i] = foldButton
            
            # Pack the buttons/sliders to the windows
            callButton.pack(side = "right")
            raiseSlider.pack(side = "right")
            raiseButton.pack(side = "right")
            allinButton.pack(side = "right")
            foldButton.pack(side = "right")

    def proceed(self):
        """ Proceeds to the next step in the game, based on the current state and certain
        table conditions"""
        if self.state == "preRound":
            print("PRE-FLOP")

            # Disable Proceed button
            self.proceedButton.config(state = DISABLED)

            # Reset stopBetting and update state
            self.stopBetting = False
            self.state = "preflopBetting"
            
            # Deal players and set up a pre-flop betting rotation
            self.dealPlayers()
            self.table.getPreFlopRotation(self.round)
            self.preflopSetup()

            # Pop the first Player from the queue
            self.getNextPlayer()

        # If we are in a betting round, handle the betting
        elif self.state[-7:] == "Betting":
            # Remove folded players from rotation
            for player in self.table.foldedPlayers:
                if player in self.table.rotation:
                    self.table.rotation.remove(player)
        
            # Remove all-in players from rotation and move them from allinPlayers to resolved players
            for player in self.table.allinPlayers:
                self.table.rotation.remove(player)
                self.table.resolvedAllinPlayers += [player]

            # Clear allinPlayers
            self.table.allinPlayers = []

            # If the rotationQueue is not yet empty, move on to the next Player
            if len(self.rotationQueue) != 0:
                self.getNextPlayer()

            else:
                # If everyone left in the rotation has not met the current bet, redo the rotation
                if not all(player.bet >= self.table.currentBet for player in self.table.rotation):
                    self.fillQueue()
                    self.proceed()

                else:
                    # Progress game state
                    self.state = self.states[self.states.index(self.state) + 1]

                    # Reallow betting for next rotation
                    for player in self.table.rotation:
                        player.canBet = True

                    # Set stopBetting based on whether or not there is a single or no players left in the rotation
                    self.stopBetting = self.table.lastPlayer()

                    # Re-enable the Proceed button and check to see if betting should stop
                    self.proceedButton.config(state = NORMAL)
                    self.stopBetting = self.stopBetting or self.table.allPlayersAllin()

                    # Reset rotation
                    self.table.rotation = []
                    
                    # If betting should stop, automatically proceed through dealing the cards
                    if self.stopBetting:
                        self.proceed()
                    
                    # Otherwise, prompt to proceed to the next state
                    else:
                        self.updateChips()

                        if self.state == "preflop":
                            print("Pre-flop betting concluded. Press Proceed to deal the flop.")

                        elif self.state == "flop":
                            print("Flop betting concluded. Press Proceed to deal the turn.")
                        
                        elif self.state == "turn":
                            print("Turn betting concluded. Press Proceed to deal the river.")

                        elif self.state == "river":
                            print("River betting concluded. Press Proceed to resolve pots.")
        
        elif self.state == "preflop":
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

                # Set state
                self.state = "flopBetting"

                # Set up a betting rotation
                self.table.getRotation(self.round)
                self.postflopSetup()
                
                # Pop the first Player from the queue
                self.getNextPlayer()

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
                
                # Set state
                self.state = "turnBetting"

                # Set up a betting rotation
                self.table.getRotation(self.round)
                self.postflopSetup()
                
                # Pop the first Player from the queue
                self.getNextPlayer()

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
                
                # Set state
                self.state = "riverBetting"

                # Set up a betting rotation
                self.table.getRotation(self.round)
                self.postflopSetup()
                
                # Pop the first Player from the queue
                self.getNextPlayer()

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

            # Check to see if Players should be removed from the game or if the game is finished
            self.updatePlayers()

            self.state = "preRound"

    def getNextPlayer(self):
        """ Pop a Player from the rotation queue and enable their betting buttons. If
        the Player shouldn't be betting for whatever reason, call proceed so another
        Player can be popped"""
        # Pop another Player from the queue
        player = self.rotationQueue.pop()

        # If there is one player or none left in the rotation and the remaining player does not need to bet, clear the queue and proceed
        if self.table.allPlayersFolded() or (self.table.lastPlayer() and player.bet >= self.table.currentBet):
            self.rotationQueue.clear()
            self.proceed()

        # If the player is not allowed to bet, continue to the next iteration
        elif not player.canBet:
            self.proceed()

        # Otherwise, enable the Player's betting buttons
        else:
            self.enableBetting(player)

    def preflopSetup(self):
        """ Sets up the pre-flop betting rotation."""
        # Set up the blinds and the pot and fill the rotation queue
        self.table.preflop(self)
        self.fillQueue()

    def postflopSetup(self):
        """ Sets up a post-flop betting rotation."""
        # Set up the starting bets and fill the rotation queue
        self.table.postflop(self)
        self.fillQueue()

    def fillQueue(self):
        """ Fills up the rotation queue with the Players from the table's
        rotation attribute"""
        # Fill up the rotation queue
        for player in self.table.rotation:
            self.rotationQueue = [player] + self.rotationQueue

    def updateChips(self):
        """ Updates the chip counts of every player in the game and the
        current bet."""
        # Update variables for player windows
        for i in range(0, len(self.table.allPlayers)):
            self.chipCounts[i].set("Chips: " + str(self.table.allPlayers[i].chips))
            self.bets[i].set("Bet: " + str(self.table.allPlayers[i].bet))

        # Update variables for main window
        self.currentBet.set("Current bet: " + str(self.table.currentBet))
        pots = self.table.pots

        if len(pots) == 0:
            pString = "Main pot: 0"

        else:
            pString = "Main pot: " + str(pots[0].amount)
            for pot in pots[1:]:
                pString += "    Side pot: " + str(pot.amount)
        
        self.potString.set(pString)

    def enableBetting(self, player):
        """ Finds the action the given player wants to take while betting"""
        # Reset bettingOngoing to "none" and find the index of the given Player
        self.bettingOngoing = "none"
        playerIndex = self.table.allPlayers.index(player)

        # Find the appropriate bounds for the slider
        minRaise = self.table.currentBet if self.table.currentBet != 0 else self.table.bigBlind
        maxRaise = player.chips - (self.table.currentBet - player.bet)

        # If the player doesn't have enough chips to raise, or has just enough, set minRaise and maxRaise to the player's remaining chips
        if maxRaise <= 0:
            maxRaise = player.chips
            minRaise = player.chips
        
        # Change raising slider bounds as is appropriate and enable it
        raiseSlider = self.raiseSliders[playerIndex]
        raiseSlider.config(
            to = minRaise, 
            from_ = maxRaise,
            state = NORMAL)

        # Start slider at bottom
        raiseSlider.set(minRaise)

        # Enable betting buttons for the given Player
        self.callButtons[playerIndex].config(state = NORMAL)
        self.raiseButtons[playerIndex].config(state = NORMAL)
        self.allinButtons[playerIndex].config(state = NORMAL)
        self.foldButtons[playerIndex].config(state = NORMAL)

    def disableBetting(self, player):
        # Find the index of the given Player
        playerIndex = self.table.allPlayers.index(player)

        # Reset slider value and range and disable it
        raiseSlider = self.raiseSliders[playerIndex]
        raiseSlider.config(
            to = 0,
            from_ = 0,
            state = DISABLED)
        raiseSlider.set(0)

        # Disable betting buttons for the given Player
        self.callButtons[playerIndex].config(state = DISABLED)
        self.raiseButtons[playerIndex].config(state = DISABLED)
        self.allinButtons[playerIndex].config(state = DISABLED)
        self.foldButtons[playerIndex].config(state = DISABLED)

    def setBet(self, player, x):
        """ Handles a given player's bet based on the string provided. A
        "c" indicates a call, an "r" indicates a raise, an "a" indicates
        all-in, and an "f" indicates a fold"""
        print(player)
        # Player calls/checks
        if x == 'c':
            # Prevent the player from betting again until someone else raises
            player.canBet = False

            if self.table.currentBet == player.bet:
                print("Player", player.name, "has checked. \n")
            elif self.table.currentBet - player.bet >= player.chips:
                self.table.allIn(player)
                print(player, "\n")
            else:
                print("Player", player.name, "has called. \n")
                player.Call(self.table.currentBet)
                self.table.stay(player)
        
        # Player raises
        elif x == 'r':
            while True:
                # Re-allow all other players to bet
                for betPlayer in self.table.Players:
                    betPlayer.canBet = True
                
                # Prevent the player from betting again until someone else raises
                player.canBet = False

                r = self.raiseSliders[self.table.allPlayers.index(player)].get()
                if r == player.chips - (self.table.currentBet - player.bet):
                    self.table.allIn(player)
                    print(player, "\n")
                    break
                
                # TODO: Remove, this check should be done by restricting slider values
                elif r > player.chips - (self.table.currentBet - player.bet):
                    print("You do not have enough chips to raise by that amount. \n")
                    continue
                
                elif r >= self.table.currentBet:
                    player.Raise(self.table.currentBet, r)
                    self.table.stay(player)
                    self.table.currentBet += r
                    print("Player", player.name, "has raised to", self.table.currentBet, "\n")
                    break
                
                # TODO: Remove, this check should be done by restricting slider values
                else:
                    print("You must raise by at least as much as the current bet:", self.table.currentBet,"\n")
                    continue
        
        # Player goes all-in
        elif x == 'a':
            # If allIn raises the currentBet, re-allow all other players to bet
            if player.chips + player.bet > self.table.currentBet:
                for betPlayer in self.table.Players:
                    betPlayer.canBet = True

            self.table.allIn(player)
            print(player, "\n")
        
        # Player folds            
        elif x == 'f':
            self.table.fold(player)
            print(player, "\n")

        # Update the chips
        self.updateChips()

        # Disable betting buttons
        self.disableBetting(player)

        # Proceed to the next Player (or to the end of betting)
        self.proceed()

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
        for i in self.handLabels.keys():
            for label in self.handLabels[i]:
                label.destroy()

            for image in self.handImages[i]:
                image.__del__()

        # Delete all player hands
        for key in self.hands:
            del self.table.allPlayers[key].hand

        # Reset global variables
        self.hands.clear()
        self.handImages.clear()
        self.handLabels.clear()

    def updatePlayers(self):
        """ Check for newly-bankrupted Players, close their windows and
        update numActivePlayers"""
        # Iterate through the indices of all the Players who were in the game at the start
        for i in range(self.numPlayers):
            # Find Players who are bankrupt and have not had their windows destroyed yet
            if self.handWindows[i] != None and self.table.allPlayers[i] in self.table.bankruptPlayers:
                # Destroy the player window, set it to None in handWindows, and decrement numActivePlayers
                self.handWindows[i].destroy()
                self.handWindows[i] = None
                self.numActivePlayers -= 1

        # If there is a single player left, initiate victory
        if self.numActivePlayers == 1:
            self.initiateVictory()

    def initiateVictory(self):
        """ Closes player windows and prints a victory message for the winning Player"""
        for window in self.handWindows:
            if window != None:
                window.destroy()

        winner = table.winningPlayer()
        Label(text = "Congratulations! " + winner.name + " has won!", height = 30).pack()
        print("Player", winner.name, "has won!")

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
        # Create hands for as many players as designated by numActivePlayers
        for i in range(0, self.numActivePlayers):
            # Create a hand for each player and add that hand to the hands attribute so it can be displayed
            newHand = Hand(2).fillHand(self.deck)
            table.Players[i].hand = newHand
            playerIndex = table.allPlayers.index(table.Players[i])
            self.hands[playerIndex] = newHand
            self.handImages[playerIndex] = []
            self.handLabels[playerIndex] = []

            # Add the face-down card image to this entry of self.handImages
            self.handImages[playerIndex] += [PhotoImage(master = self.handWindows[playerIndex], file ="Cards/Facedown.png")]

            # Add the face-up images of the cards in the current hand to this entry of self.handImages
            for card in newHand.cards:
                self.handImages[playerIndex] += [PhotoImage(master = self.handWindows[playerIndex], file ="Cards/" + repr(card) + ".png")]

            # Create labels for face-down cards
            for j in range(0, 2):
                self.handLabels[playerIndex] += [Label(self.handWindows[playerIndex], image = self.handImages[playerIndex][0])]

            # Display labels on window
            for label in self.handLabels[playerIndex]:
                label.pack(side = "left")

# Initialize the poker table
table = Table()

# Get the players and blinds
table.getPlayers()
table.getBlinds()

# Create the top level window
top = Tk()
top.geometry("1200x450")

app = Application(table, top)

print("Round", app.round + 1)

top.mainloop()

del table
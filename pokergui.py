from tkinter import *
from cards import *
from pokerchips import *
from functools import *
import asyncio

class Application():
    def __init__(self, table = None, master = None, state = "preRound", bot = None):
        """ Create a new Application, which runs a tkinter GUI for a Texas hold-em poker game.
        Takes in arguments for table (the Table object linked to the application), master (the
        top-level tkinter window the game is to be played in), state (the state the game should
        start in), and bot (the message bot associated with the application if it is being
        played in online mode)"""
        # If table argument was not provided, create a default Table
        if not table:
            table = Table()
        
        self.state = state
        self.states = ["preRound", "preflopBetting", "preflop", "flopBetting", "flop", "turnBetting", "turn", "riverBetting", "river", "postRound"]
        self.master = master
        self.table = table
        self.bot = bot
        
        self.playerNames = list(map(lambda x: x.name, table.allPlayers))
        self.numPlayers = len(self.playerNames)
        self.numActivePlayers = self.numPlayers
        self.startingChips = table.allPlayers[0].chips
        
        # Card-tracking variables
        self.deck = Deck()
        self.faceupBoard = []

        # Main window variables, created only in local mode
        self.boardImages = []
        self.boardLabels = []        
        
        # Player window variables, created only in local mode
        if not self.bot:
            self.handWindows = []
            self.hands = {}
            self.chipCounts = []
            self.bets = []
            self.handImages = {}
            self.handLabels = {}
            self.flipButtons = {}
            self.callButtons = {}
            self.raiseButtons = {}
            self.raiseSliders = {}
            self.allinButtons = {}
            self.foldButtons = {}

        # Main window label variables (stringvars if local, strings otherwise)
        if not self.bot:
            self.currentBet = StringVar()
            self.potString = StringVar()
            
            # Set string variables
            self.currentBet.set("Current bet: 0")
            self.potString.set("Main pot: 0")

        else:
            self.currentBet = "Current bet: 0"
            self.potString = "Main pot: 0"
        
        # Variables for conducting betting
        self.round = 0
        self.rotationQueue = []
        self.stopBetting = False
        self.allPlayersFolded = False

        # Local mode only operations
        if not self.bot:
            # Add buttons and a face-down card to main window
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

            Label(textvariable = self.currentBet).pack(side = "top")
            Label(textvariable = self.potString).pack(side = "top")
  
            # Create new windows for each player
            for i in range(0, self.numPlayers):
                # Initialize window
                self.handWindows += [Toplevel()]
                self.handWindows[i].geometry("600x400")
                
                # Initialize string variables for bet and chip Labels
                chipCount = StringVar()
                bet = StringVar()
                self.chipCounts += [chipCount]
                self.bets += [bet]
                
                chipCount.set("Chips: " + str(self.startingChips))
                bet.set("Bet: 0")

                # Initialize player name and pack in Labels
                playerString = "Player " + str(i + 1) + ": " + self.playerNames[i]
                Label(self.handWindows[i], text = playerString).pack(side = "top")
                Label(self.handWindows[i], textvariable = chipCount).pack(side = "top")
                Label(self.handWindows[i], textvariable = bet).pack(side = "top")

                # Initialize card flipping Button
                flipButton = Button(self.handWindows[i], 
                    text = "Flip cards",
                    fg = "red",
                    state = DISABLED,
                    command=lambda i=i: self.flipCards(i))
                
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
                self.flipButtons[i] = flipButton
                self.callButtons[i] = callButton
                self.raiseSliders[i] = raiseSlider
                self.raiseButtons[i] = raiseButton
                self.allinButtons[i] = allinButton
                self.foldButtons[i] = foldButton
                
                # Pack the buttons/sliders to the windows
                flipButton.pack()
                callButton.pack(side = "right")
                raiseSlider.pack(side = "right")
                raiseButton.pack(side = "right")
                allinButton.pack(side = "right")
                foldButton.pack(side = "right")     

    async def proceed(self):
        """ Proceeds to the next step in the game, based on the current state and certain
        table conditions"""
        if self.state == "preRound":
            print("PRE-FLOP")

            # Disable Proceed button if in local mode
            if not self.bot:
                self.proceedButton.config(state = DISABLED)

            # Reset stopBetting, allPlayersFolded, and rotationQueue and update state
            self.stopBetting = False
            self.allPlayersFolded = False
            self.rotationQueue.clear()
            self.state = "preflopBetting"

            # Un-fold and re-enable players to bet, if needed
            for player in self.table.Players:
                player.canBet = True
                player.folded = False
            
            # Deal players and set up a pre-flop betting rotation
            await self.dealPlayers()
            self.table.getPreFlopRotation(self.round)
            await self.preflopSetup()
            
            # Enable flipButtons if in local mode
            if not self.bot:
                self.enableFlipping()

            # Pop the first Player from the queue
            await self.getNextPlayer()

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
                await self.getNextPlayer()

            else:
                # If everyone left in the rotation has not met the current bet, redo the rotation
                if not all(player.bet >= self.table.currentBet for player in self.table.rotation):
                    await self.fillQueue()
                    await self.proceed()

                else:
                    # Progress game state
                    self.state = self.states[self.states.index(self.state) + 1]

                    # Reallow betting for next rotation
                    for player in self.table.rotation:
                        player.canBet = True

                    # Set stopBetting and allPlayersFolded based on table methods
                    self.stopBetting = self.table.lastPlayer()
                    self.allPlayersFolded = self.table.allPlayersFolded()

                    # Re-enable the Proceed button if in local mode
                    if not self.bot:
                        self.proceedButton.config(state = NORMAL)

                    # Check to see if betting should stop
                    self.stopBetting = self.stopBetting or self.table.allPlayersAllin()

                    # Reset rotation
                    self.table.rotation = []
                    
                    # If all players have folded, proceed immediately to pot resolution
                    if self.allPlayersFolded:
                        print("All players but one have folded. Proceeding to pot resolution")
                        self.state = "river"
                        await self.proceed()
                    
                    # Otherwise, prompt to proceed to the next state
                    else:
                        await self.updateChips()

                        # If in local mode, print a message and wait for proceed to be pressed
                        if not self.bot:
                            if self.state == "preflop":
                                print("Pre-flop betting concluded. Press Proceed to deal the flop.")

                            elif self.state == "flop":
                                print("Flop betting concluded. Press Proceed to deal the turn.")
                            
                            elif self.state == "turn":
                                print("Turn betting concluded. Press Proceed to deal the river.")

                            elif self.state == "river":
                                print("River betting concluded. Press Proceed to resolve pots.")

                        # If in online mode, automatically proceed
                        else:
                            await self.proceed()
        
        elif self.state == "preflop":
            # Disable proceed button if in local mode
            if not self.bot:
                self.proceedButton.config(state = DISABLED)

            # Burn one and deal 3 cards, then switch gamestate to flop
            self.deck.burn()

            flop = self.deck.deal(3)
            self.faceupBoard += flop

            # Add cards to main window if in local mode
            if not self.bot:
                self.addCards(flop)

            self.state = "flop"

            # If in online mode, message the group thread with the new board
            if self.bot:
                await self.bot.updateBoard(self.state, self.faceupBoard)

            # If betting has already stopped, don't conduct betting
            if self.stopBetting:
                # If in local mode, wait for proceed to be pressed
                if not self.bot:
                    self.proceedButton.config(state = NORMAL)
                    print("Press Proceed to deal the turn.")

                # If in online mode, proceed automatically
                else:
                    await self.proceed()

            else:
                # Conduct flop betting
                print("FLOP")

                # Set state
                self.state = "flopBetting"

                # Set up a betting rotation
                await self.table.getRotation(self.round)
                await self.postflopSetup()
                
                # Pop the first Player from the queue
                await self.getNextPlayer()

        elif self.state == "flop":
            # Disable proceed button if in local mode
            if not self.bot:
                self.proceedButton.config(state = DISABLED)

            # Burn one and deal one card, then switch gamestate to turn
            self.deck.burn()

            turn = self.deck.deal(1)
            self.faceupBoard += turn

            # Add cards to main window if in local mode
            if not self.bot:
                self.addCards(turn)

            self.state = "turn"

            # If in online mode, message the group thread with the new board
            if self.bot:
                await self.bot.updateBoard(self.state, self.faceupBoard)

            # If betting has already stopped, automatically proceed to the end
            if self.stopBetting:
                # If in local mode, wait for proceed to be pressed
                if not self.bot:
                    self.proceedButton.config(state = NORMAL)
                    print("Press Proceed to deal the river.")

                # If in online mode, proceed automatically
                else:
                    await self.proceed()

            else:
                # Conduct turn betting
                print("TURN")
                
                # Set state
                self.state = "turnBetting"

                # Set up a betting rotation
                await self.table.getRotation(self.round)
                await self.postflopSetup()
                
                # Pop the first Player from the queue
                await self.getNextPlayer()

        elif self.state == "turn":
            # Disable proceed button if in local mode
            if not self.bot:
                self.proceedButton.config(state = DISABLED)

            # Burn one and deal one card, then switch gamestate to river
            self.deck.burn()

            river = self.deck.deal(1)
            self.faceupBoard += river

            # Add cards to main window if in local mode
            if not self.bot:
                self.addCards(river)

            self.state = "river"

            # If in online mode, message the group thread with the new board
            if self.bot:
                await self.bot.updateBoard(self.state, self.faceupBoard)

            # If betting has already stopped, automatically proceed to the end
            if self.stopBetting:
                # If in local mode, wait for proceed to be pressed
                if not self.bot:
                    self.proceedButton.config(state = NORMAL)
                    print("Press Proceed to resolve pots.")

                # If in online mode, proceed automatically
                else:
                    await self.proceed()

            else:
                # Conduct river betting
                print("RIVER")
                
                # Set state
                self.state = "riverBetting"

                # Set up a betting rotation
                await self.table.getRotation(self.round)
                await self.postflopSetup()
                
                # Pop the first Player from the queue
                await self.getNextPlayer()

        elif self.state == "river":
            # Disable proceed button if in local mode
            if not self.bot:
                self.proceedButton.config(state = DISABLED)

            # Resolve pots
            await self.table.resolvePots(self.faceupBoard, bot = self.bot)

            # Switch gamestate to postRound
            self.state = "postRound"
            await self.updateChips()
            
            # Re-enable the Proceed button if in local mode 
            if not self.bot:
                self.proceedButton.config(state = NORMAL)
                print("Pots resolved. Press Proceed to go to next round.")

            # If in online mode, proceed automatically
            else:
                await self.proceed()

        else:
            # Reset the deck, increment round, clear the existing widgets and reset gamestate to preflop
            self.round += 1
            print("Round", self.round + 1)

            self.deck.reset()
            self.faceupBoard = []

            # If in local mode, clear the board
            if not self.bot:
                self.clearBoard()

                # Disable Flip Cards buttons and clear hands if in local mode
                self.disableFlipping()
                self.clearHands()

            # Check to see if Players should be removed from the game or if the game is finished
            await self.updatePlayers()

            self.state = "preRound"

            # Update main window labels
            if not self.bot:
                self.currentBet.set("Current bet: 0")
                self.potString.set("Main pot: 0")
            
            else:
                self.currentBet = "Current bet: 0"
                self.potString = "Main pot: 0"
                await self.proceed()

    async def getNextPlayer(self):
        """ Pop a Player from the rotation queue and enable their betting buttons. If
        the Player shouldn't be betting for whatever reason, call proceed so another
        Player can be popped"""
        # Pop another Player from the queue
        player = self.rotationQueue.pop()

        # If there is one player or none left in the rotation and the remaining player does not need to bet, clear the queue and proceed
        if self.table.allPlayersFolded() or (self.table.lastPlayer() and player.bet >= self.table.currentBet):
            self.rotationQueue.clear()
            await self.proceed()

        # If the player is not allowed to bet, continue to the next iteration
        elif not player.canBet:
            await self.proceed()

        # Enable the Player's betting buttons if in local mode
        elif not self.bot:
            self.enableBetting(player)

        # If in online mode, set bot to listen for the response of the given player
        else:
            await self.bot.getPlayerResponse(player)

    async def preflopSetup(self):
        """ Sets up the pre-flop betting rotation."""
        # Set up the blinds and the pot and fill the rotation queue
        await self.table.preflop(self)
        await self.fillQueue()

    async def postflopSetup(self):
        """ Sets up a post-flop betting rotation."""
        # Set up the starting bets and fill the rotation queue
        await self.table.postflop(self)
        await self.fillQueue()

    async def fillQueue(self):
        """ Fills up the rotation queue with the Players from the table's
        rotation attribute"""
        # Fill up the rotation queue
        for player in self.table.rotation:
            self.rotationQueue = [player] + self.rotationQueue

    async def updateChips(self):
        """ Updates the chip counts of every player in the game and the
        current bet."""
        # Update variables for player windows if in local mode
        if not self.bot:
            for i in range(0, len(self.table.allPlayers)):
                self.chipCounts[i].set("Chips: " + str(self.table.allPlayers[i].chips))
                self.bets[i].set("Bet: " + str(self.table.allPlayers[i].bet))

        # Update variables for main window
        pots = self.table.pots

        if len(pots) == 0:
            pString = "Main pot: 0"

        else:
            pString = "Main pot: " + str(pots[0].amount)
            for pot in pots[1:]:
                pString += "    Side pot: " + str(pot.amount)
        
        # Update StringVars (local) or strings (online)
        if not self.bot:
            self.currentBet.set("Current bet: " + str(self.table.currentBet))
            self.potString.set(pString)

        else:
            self.currentBet = "Current bet: " + str(self.table.currentBet)
            self.potString = pString

    def enableFlipping(self):
        """ Enables Flip Cards button for all Players"""
        # Iterate through all the flipButtons and enable them
        for key in self.flipButtons:
            self.flipButtons[key].config(state = NORMAL)

    def disableFlipping(self):
        """ Disables Flip Cards button for all Players"""
        # Iterate through all the flipButtons and enable them
        for key in self.flipButtons:
            self.flipButtons[key].config(state = DISABLED)

    def enableBetting(self, player):
        """ Enables betting buttons for a given player"""
        # Find the index of the given Player
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
        """ Disables betting buttons for a given Player"""
        # Find the index of the given Player
        playerIndex = self.table.allPlayers.index(player)

        # Reset slider value and range and disable it
        raiseSlider = self.raiseSliders[playerIndex]
        raiseSlider.config(
            to = 0,
            from_ = 1)
        raiseSlider.set(0)
        raiseSlider.config(state = DISABLED)

        # Disable betting buttons for the given Player
        self.callButtons[playerIndex].config(state = DISABLED)
        self.raiseButtons[playerIndex].config(state = DISABLED)
        self.allinButtons[playerIndex].config(state = DISABLED)
        self.foldButtons[playerIndex].config(state = DISABLED)

    async def setBet(self, player, x, raiseAmount = None):
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

                # Get raise amount from sliders if in local mode
                if not self.bot:
                    r = self.raiseSliders[self.table.allPlayers.index(player)].get()

                # If in online mode, use raiseAmount argument
                else:
                    r = raiseAmount

                # Set player to all-in if raise amount is equal to all-in
                if r == player.chips - (self.table.currentBet - player.bet):
                    self.table.allIn(player)
                    print(player, "\n")
                    break

                elif r > player.chips - (self.table.currentBet - player.bet):
                    print("You do not have enough chips to raise by that amount. \n")
                    break
                
                # Handle raise for Player and Table
                elif r >= self.table.currentBet:
                    player.Raise(self.table.currentBet, r)
                    self.table.stay(player)
                    self.table.currentBet += r
                    print("Player", player.name, "has raised to", self.table.currentBet, "\n")
                    break
        
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
        await self.updateChips()

        # Disable betting buttons if in local mode
        if not self.bot:
            self.disableBetting(player)

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

    async def updatePlayers(self):
        """ Check for newly-bankrupted Players, close their windows and
        update numActivePlayers"""
        # If in local mode, iterate through the indices of all the Players who were in the game at the start
        if not self.bot:
            for i in range(self.numPlayers):
                # Find Players who are bankrupt and have not had their windows destroyed yet
                if self.handWindows[i] != None and self.table.allPlayers[i] in self.table.bankruptPlayers:
                    # Destroy the player window, set it to None in handWindows, and decrement numActivePlayers
                    self.handWindows[i].destroy()
                    self.handWindows[i] = None
                    self.numActivePlayers -= 1

        # If there is a single player left, initiate victory
        if len(self.table.Players) == 1:
            await self.initiateVictory()

    async def initiateVictory(self):
        """ Closes player windows and prints a victory message for the winning Player"""
        # Destroy last window if in local mode
        if not self.bot:
            for window in self.handWindows:
                if window != None:
                    window.destroy()

        winner = self.table.winningPlayer()

        if not self.bot:
            Label(text = "Congratulations! " + winner.name + " has won!", height = 30).pack()

        else:
            await self.bot.endGame(winner)
            
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

    async def dealPlayers(self):
        """ Deal cards to the windows representing each Hand"""
        # Create hands for as many players as designated by numActivePlayers
        for i in range(0, self.numActivePlayers):
            # Create a hand for each player
            newHand = Hand(2).fillHand(self.deck)
            self.table.Players[i].hand = newHand

            # If in local mode, handle player windows
            if not self.bot:
                # Set player window attributes
                playerIndex = self.table.allPlayers.index(self.table.Players[i])
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
            
            # If in online mode, message players with their hands
            else:
                await self.bot.dealPlayer(self.table.Players[i])

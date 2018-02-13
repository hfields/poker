# Huey Fields
# 12/23/16

import functools

debug = True

class Player:
    """ Creates a representation of a player according to 4 traits: 
    their name, how many chips they have, their current bet, whether 
    or not they've won the current pot, and whether or not they've folded."""
    def __init__(self, name = '', chips = 0, bet = 0, won = False, folded = False, allin = False, canBet = True):
        self.name = name
        self.chips = chips
        self.bet = bet
        self.won = won
        self.folded = folded
        self.allin = allin
        self.canBet = canBet
    
    def __repr__(self):
        """ Returns a string describing the given player"""
        if self.allin == True:
            return "Player " + self.name + " is all in with " + str(self.bet) + " chips."
        else:
            return "Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips."

    def resolveBet(self, pot):
        """ Resolves a completed bet by awarding the pot to the winner
        or reinitializing the bet to 0 for a loser"""
        if self.won == True:
            self.bet = 0
            self.chips += pot
        else:
            self.bet = 0

    def Call(self, currentBet):
        """ Increases a player's bet to call"""
        self.chips -= currentBet - self.bet
        self.bet = currentBet     

    def Raise(self, currentBet, raiseAmount):
        """ Increases a player's bet to raise by a specified amount"""
        self.chips -= currentBet + raiseAmount - self.bet
        self.bet = currentBet + raiseAmount

    def Allin(self):
        """ Increase a player's bet so that they are all-in"""
        self.allin = True
        self.bet += self.chips
        self.chips = 0

    def inPot(self, pot):
        """ Return True if the player is in a certain pot, False
        if not"""
        return self in pot.Players

class Pot:
    """ Creates a representation of a pot. This includes the number of chips
    in the pot, the number of chips per player, a list of the players in the
    pot, whether the pot is the main pot or a side pot, and whether or not
    the pot is the current pot
    """
    def __init__(self, amount = 0, Players = [], mainPot = True, currentPot = False):
        self.amount = amount
        self.Players = Players
        self.amountPerPlayer = amount // len(Players)
        self.mainPot = mainPot
        self.currentPot = currentPot

    def __repr__(self):
        """ Returns a string describing the given pot"""
        # Create a string to be filled up and returned
        s = str(self.amount) + " chips "
        
        if len(self.Players) == 1:
            s += "with " + self.Players[0].name
        else:
            s += "between "
            # Add the names of the players in the pot
            for player in self.Players[0:-1]:
                s += player.name + ", "
            
            if len(self.Players) == 2:
                s = s[0:-2] + " "

            s += "and " + self.Players[-1].name

        if self.mainPot:
            return s + "."
        else:
            return s + " (side pot)."
    
    def increaseBet(self, inc):
        """ Increases the bet required to stay in the pot (amountPerPlayer) by inc"""
        self.amountPerPlayer += inc

    def addPlayer(self, newPlayer):
        """ Adds a player to the pot by increasing the amount by that player's
        bet, adding that player to the list of players in the pot, and changing
        amountPerPlayer as needed"""
        self.amount += newPlayer.bet
        if self.currentPot:
            self.increaseBet(newPlayer.bet - self.amountPerPlayer)
        self.Players += [newPlayer]
    
    def removePlayer(self, foldPlayer):
        """ Removes a player from the pot by removing that player from the list 
        of players in the pot"""
        if foldPlayer.inPot(self):
            self.Players.remove(foldPlayer)


class Table:
    """ Creates a representation of a poker table. This includes 5 lists of 
    Player objects: a full list of players, a list of players that have gone
    bankrupt, a list of players that have folded, a list of players who are
    currently all-in, a list of players who are all-in whose bets have been
    resolved to pots, and a list of players in the current betting rotation.
    The table also keeps track of the small blind, big blind, and current bet 
    as integers, and keeps a list of all pots on the table (main pot and side pots)
    """
    def __init__(self, Players = [], bankruptPlayers = [], foldedPlayers = [], allinPlayers = [], resolvedAllinPlayers = [], rotation = [], smallBlind = 0, bigBlind = 0, currentBet = 0, pots = []):
        self.Players = Players
        self.bankruptPlayers = bankruptPlayers
        self.foldedPlayers = foldedPlayers
        self.allinPlayers = allinPlayers
        self.resolvedAllinPlayers = resolvedAllinPlayers
        self.rotation = rotation
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        self.currentBet = currentBet
        self.pots = pots
    
    def playerInfo(self, players):
        """ Prints out important player info"""    
        for player in players:
            print(player)

    def potInfo(self):
        """ Prints out info about the pots"""
        numPots = len(self.pots)
        if numPots == 1:
            print("There is currently 1 pot:")
        else:
            print("There are currently " + str(numPots) + " pots:")
        for pot in self.pots:
            print(pot)

    def getPlayers(self):
        """ Uses user input to find the names of all the players, and how many chips they
        should start with, then sets the Players to that """
        # Find out how many people are playing, their names, and the starting amount of chips
        while True:
            p = get_int("How many players should there be? ")
            if p >= 2:
                playercount = p
                break
            else:
                print("Please choose a higher number of players.\n")
                continue
        playernames = []
        for i in range(playercount):
            while True:
                s = "Player " + str(i + 1) + ", what is your name? "
                name = str(input(s))
                if name in playernames:
                    print("That name has already been taken. Please choose another.\n")
                    continue
                else:
                    playernames += [name]
                    break
        
        startChips = get_int("How many chips should each player start with? ")
        
        # Fill up Players
        for player in playernames:
            self.Players += [Player(player, startChips)]
    
    def getBlinds(self):
        """ Uses user input to set the small and big blind. Big blind will always be
        double the small blind"""
        while True:
            s = get_int("How much should small blind be (big blind will be double the small blind)? ")
            if 2 * s <= self.Players[0].chips:
                self.smallBlind = s
                self.bigBlind = 2 * s
                break
            else:
                print("Big blind cannot be greater than the amount of chips each player starts with.\n")
                continue

    def getPreFlopRotation(self, round):
        """ Uses the round number to determine the (pre-flop) betting rotation."""
        # Set indices in player list for dealer and blinds
        playerCount = len(self.Players)
        dealer = round % playerCount - 1

        if (playerCount > 2):
            blind1 = dealer + 1
            blind2 = dealer + 2
        else:
            blind1 = dealer + 1
            blind2 = dealer
        
        print("Player", self.Players[dealer].name, "is the dealer.\n")

        # Create a list of player indices in their pre-flop rotation order
        for i in range(blind2 + 1, playerCount):
            self.rotation += [self.Players[i]]
        for i in range(blind2 + 1):
            self.rotation += [self.Players[i]]

    def getRotation(self, round):
        """ Uses the round number to determine the betting rotation."""
        # Set indices in player list for the dealer
        playerCount = len(self.Players)
        dealer = round % playerCount - 1

        # Create a list of player indices in their regular rotation order
        for i in range(dealer + 1, playerCount):
            self.rotation += [self.Players[i]]
        for i in range(dealer + 1):
            self.rotation += [self.Players[i]]

    def preflop(self):
        """ Handles the pre-flop betting rotation"""
        # Handle small blind
        if self.rotation[-2].chips > self.smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and starts with a bet of", self.smallBlind, "chips.")
            self.rotation[-2].Call(self.smallBlind)
        elif self.rotation[-2].chips == self.smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and is all in with", self.smallBlind, "chips.")
            self.rotation[-2].Allin()
            self.allinPlayers += [self.rotation.pop(-2)]
        else:
            print("Player", self.rotation[-2].name, "is small blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-2].chips, "chips.")
            self.rotation[-2].Allin()
            self.allinPlayers += [self.rotation.pop(-2)]
        
        # Handle big blind
        if self.rotation[-1].chips > self.bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and starts with a bet of", self.bigBlind, "chips.\n")
            self.rotation[-1].Call(self.bigBlind)
        elif self.rotation[-1].chips == self.bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and is all in with", self.bigBlind, "chips.\n")
            self.rotation[-1].Allin()
            self.allinPlayers += [self.rotation.pop(-1)]
        else:
            print("Player", self.rotation[-1].name, "is big blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-1].chips, "chips.\n")
            self.rotation[-1].Allin()
            self.allinPlayers += [self.rotation.pop(-1)]

        # Set the currentBet to the highest bet made by the players in the blinds and create the pots
        self.currentBet = max(self.rotation[-2].bet, self.rotation[-1].bet)
        self.createPots()

        #self.playerInfo(self.Players)
        #self.potInfo()

        self.bettingRotation()
    
    def createPots(self):
        # Sort the allinPlayers from least to greatest
        self.allinPlayers = chipMSort(self.allinPlayers)
        
        # Iterate through the players who are all-in but haven't had their bets put into pots yet
        for player in self.allinPlayers:
            i = self.allinPlayers.index(player)
            
            # If there are no pots so far, create the main pot
            if self.pots == []:
                self.pots += [Pot(player.bet * (len(self.allinPlayers) - i), self.allinPlayers[i:], True)]
            
            # Otherwise, create the next side pot
            else:
                self.pots += [Pot(player.bet - self.pots[i - 1].amountPerPlayer * (len(self.allinPlayers) - i), self.allinPlayers[i:], False)]

            # Move the player to resolvedAllinPlayers
            self.resolvedAllinPlayers += [player]
        
        self.allinPlayers = []
        
        # If there are no pots so far, create the main pot with the blinds
        if self.pots == []:
            self.pots += [Pot(self.rotation[-2].bet + self.rotation[-1].bet, self.rotation[-2:], True)]

        # Set the latest pot's currentPot flag to True
        self.pots[-1].currentPot = True

    def bettingRotation(self):
        """ Handles a single betting rotation"""
        
        # Continue until all bets are settled
        while True:
            for player in self.rotation:
                # If the player is not allowed to bet, continue to the next iteration
                if not player.canBet:
                    continue 
                
                # Print info
                self.playerInfo(self.rotation)
                self.potInfo()
                print("The current bet is", self.currentBet, "\n")
                print(player)

                # Player has not enough or just enough chips to match the current bet
                if player.chips <= self.currentBet - player.bet:
                    while True:
                        x = str(input(player.name + ", what action would you like to take? You do not have enough chips to raise. Type in 'c' to call (all-in) or 'f' to fold."))
                        if x == 'c' or x == 'f':
                            break
                        # Debugger only command. Exits betting rotation function
                        elif x == 'q' and debug == True:
                            return
                        # Invalid character entered
                        else:
                            print("Please input a valid character. 'c' to call (all-in) or 'f' to fold. \n")
                            continue
                
                # Player has enough chips to call but not to raise
                elif player.chips < 2 * self.currentBet - player.bet:
                    while True:
                        x = str(input(player.name + ", what action would you like to take? You do not have enough chips to raise. Type in 'c' to call, 'a' to go all-in, or 'f' to fold."))
                        if x == 'c' or x == 'a' or x == 'f':
                            break
                        # Debugger only command. Exits betting rotation function
                        elif x == 'q' and debug == True:
                            return
                        # Invalid character entered
                        else:
                            print("Please input a valid character. 'c' to call (all-in) or 'f' to fold. \n")
                            continue
                else:
                    while True:
                        x = str(input(player.name + ", what action would you like to take? Type in 'c' to call/check, 'r' to raise, 'a' to go all in, or 'f' to fold. "))
                        if x == 'c' or x == 'r' or x == 'a' or x == 'f':
                            break
                        # Debugger only command. Exits betting rotation function
                        elif x == 'q' and debug == True:
                            return
                        # Invalid character entered
                        else:
                            print("Please input a valid character. 'c' to call, 'r' to raise, 'a' to go all-in, or 'f' to fold. \n")
                            continue
                
                # Player calls/checks
                if x == 'c':
                    if self.currentBet == 0:
                        print("Player", player.name, "has checked. \n")
                    elif self.currentBet - player.bet >= player.chips:
                        player.Allin()
                        self.allinPlayers += [player]
                        self.rotation.remove(player)
                        print(player)
                    else:
                        print("Player", player.name, "has called. \n")
                        player.Call(self.currentBet)
                        self.stay(player)
                
                # Player raises
                elif x == 'r':
                    while True:
                        # Re-allow the last player to bet
                        self.rotation[-1].canBet = True

                        r = get_int("How much do you want to raise by? ")
                        if r == player.chips:
                            player.Allin()
                            self.allinPlayers += [player]
                            self.rotation.remove(player)
                            print(player)
                            break
                        elif r > player.chips:
                            print("You do not have enough chips to raise by that amount. \n")
                            continue
                        elif r >= self.currentBet:
                            player.Raise(self.currentBet, r)
                            self.stay(player)
                            self.currentBet += r
                            print("Player", player.name, "has raised to", self.currentBet, "\n")
                            break
                        else:
                            print("You must raise by at least as much as the current bet:", self.currentBet,"\n")
                            continue
                
                # Player goes all-in
                elif x == 'a':
                    player.Allin()
                    if player.bet > self.currentBet:
                        self.currentBet = player.bet
                    self.allinPlayers += [player]
                    self.rotation.remove(player)
                    print(player)
                
                # Player folds            
                elif x == 'f':
                    self.fold(player)
                    print("Player", player.name, "has folded. \n")
            
            # Remove folded players from rotation
            for player in self.foldedPlayers:
                self.rotation.remove(player)
            
            # Clear foldedPlayers
            self.foldedPlayers = []

            # If everyone left in the rotation matches the current bet, end the rotation
            if all(player.bet == self.currentBet for player in self.rotation):
                break
            
            # Prevent the last player from betting at the end of the next cycle (unless someone raises again)
            self.rotation[-1].canBet = False

    def stay(self, stayPlayer):
        """ Changes the pots to represent a player calling or raising"""
        # Add the player to any pots below the current pot that the player is not already in
        for pot in self.pots[:-1]:
            if not stayPlayer.inPot(pot):
                pot.addPlayer(stayPlayer)

        # Add the player to the current pot if they aren't in it        
        if not stayPlayer.inPot(self.pots[-1]):
            self.pots[-1].addPlayer(stayPlayer)

        # If they are, increase the bet to stay in the pot as necessary
        else:
            self.pots[-1].increaseBet(stayPlayer.bet - self.currentBet)
    
    def fold(self, foldPlayer):
        """ Changes the pots and table to reflect a player folding"""
        # Remove the folded player from all the pots
        for pot in self.pots:
            pot.removePlayer(foldPlayer)
        # Add them to the folded players list
        self.foldedPlayers += [foldPlayer]
    
    def allIn(self, allinPlayer):
        return 0

def main():
    # Initialize the poker table
    table = Table()

    # Get the players and blinds
    table.getPlayers()
    table.getBlinds()

    # Begin looping through rounds until only one player remains with chips
    round = 0
    while True:
        round += 1
        print("\nRound", round)

        table.getPreFlopRotation(round)
        table.preflop

def get_int(s):
    """ Returns an integer casting of user input (displays the string s 
    to the user. Validates input to make sure that a non-negative integer
    is input."""
    while(True):
        try:
            r = int(input(s))
        except:
            print("Please pick a non-negative integer.\n")
            continue
        if r < 0:
            print("Please pick a non-negative integer.\n")
            continue
        else:
            return r

def chipMSort(L):
    """Runs mergesort on a list of players to put them in order
    of least to greatest chips"""
    if L == []:
        return []
    elif len(L) == 1:
        return [L[0]]
    else:
        return chipMerge(chipMSort(L[0:int(len(L)/2)]), chipMSort(L[int(len(L)/2):]))

def chipMerge(L1, L2):
    """Helper function for chipMSort"""
    if L1 == [] or L2 == []:
        return L1 + L2
    elif L1[0].chips < L2[0].chips:
        return [L1[0]] + chipMerge(L1[1:], L2) 
    elif L2[0].chips < L1[0].chips:
        return [L2[0]] + chipMerge(L1, L2[1:])
    else:
        return [L1[0]] + [L2[0]]

def preflopTest1():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 100)
    p4 = Player("Deandra", 100)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(players, smallBlind = 1, bigBlind = 2)

    # Do a preflop runthrough
    round = 1
    print("\nRound", round)

    table.getPreFlopRotation(round)
    table.preflop()

def preflopTest2():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 200)
    p4 = Player("Deandra", 100)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(players, smallBlind = 100, bigBlind = 200)

    # Do a preflop runthrough
    round = 1
    print("\nRound", round)

    table.getPreFlopRotation(round)
    table.preflop()

def sortTest():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 300)
    p2 = Player("Brett", 200)
    p3 = Player("Cindy", 500)
    p4 = Player("Deandra", 600)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Run sort and print the list
    print(chipMSort(players))

def rotation_test(blind2, playercount):
    preflop_rotation = []
    for i in range(blind2 + 1, playercount):
        preflop_rotation += [i]
    for i in range(blind2 + 1):
        preflop_rotation += [i]
    return preflop_rotation

if __name__ == "__main__" and debug == False:
    main()
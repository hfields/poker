# Huey Fields
# 12/23/16

import functools
from cards import *

debug = True

class Player:
    """ Creates a representation of a player according to 4 traits: 
    their name, how many chips they have, their current bet, their cards, whether 
    or not they've won the current pot, and whether or not they've folded."""
    def __init__(self, name = '', chips = 0, bet = 0, won = False, folded = False, allin = False, canBet = True, hand = None):
        self.name = name
        self.chips = chips
        self.bet = bet
        self.won = won
        self.folded = folded
        self.allin = allin
        self.canBet = canBet
        self.hand = hand
    
    def __repr__(self):
        """ Returns a string describing the given player"""
        if self.allin:
            return "Player " + self.name + " is all in with " + str(self.bet) + " chips."
        elif self.folded:
            return "Player " + self.name + " has folded."
        else:
            return "Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips."

    def resolveBet(self, pot):
        """ Resolves a completed bet by awarding a pot to the winner
        or reinitializing the bet to 0 for a loser"""
        # Award chips and reset bets
        if self.won == True:
            self.bet = 0
            self.chips += pot
        else:
            self.bet = 0

        # Reset flags
        self.folded = False
        self.allin = False
        self.canBet = True
        self.won = False

    def Call(self, currentBet):
        """ Increases a player's bet to call"""
        self.chips -= currentBet - self.bet
        self.bet = currentBet     

    def Raise(self, currentBet, raiseAmount):
        """ Increases a player's bet to raise by a specified amount"""
        self.chips -= currentBet + raiseAmount - self.bet
        self.bet = currentBet + raiseAmount

    def allIn(self):
        """ Increase a player's bet so that they are all-in"""
        self.allin = True
        self.bet += self.chips
        self.chips = 0
    
    def fold(self):
        """ Set a player's folded flag to True"""
        self.folded = True

    def inPot(self, pot):
        """ Return True if the player is in a certain pot, False
        if not"""
        return self in pot.Players

class Pot:
    """ Creates a representation of a pot. This includes the number of chips
    in the pot, the number of chips per player, a list of the players in the
    pot, the contributions each player has made to the pot, whether the pot 
    is the main pot or a side pot, and whether or not the pot is the current 
    pot
    """
    def __init__(self, amount = 0, amountPerPlayer = 0, Players = [], mainPot = True, currentPot = False):
        self.amount = amount
        self.Players = Players
        self.contributions = {}
        for player in Players:
            self.contributions[player] = player.bet
        self.mainPot = mainPot
        self.currentPot = currentPot

        # By default, make amountPerPlayer the amount divided by the number of Players
        if amountPerPlayer == 0:
            self.amountPerPlayer = amount // len(Players)
        else:
            self.amountPerPlayer = amountPerPlayer
        

    def __repr__(self):
        """ Returns a string describing the given pot"""
        # Create a string to be filled up and returned
        s = str(self.amount) + " chips "
        
        if len(self.Players) == 0:
            s += "floating in the ether"

        elif len(self.Players) == 1:
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

    def setAmountPerPlayer(self, newAmount):
        """ Sets the amountPerPlayer to a certain amount"""
        self.amountPerPlayer = newAmount

    def increaseBet(self, raisePlayer, inc):
        """ Increases the bet required to stay in the pot (amountPerPlayer) by inc
        and adjusts the amount of chips in the pot and contribution of the player 
        raising accordingly"""
        # Only allow the bet to be raised for the current Pot
        if self.currentPot:
            self.amount += inc + (self.amountPerPlayer - self.contributions[raisePlayer])
            self.contributions[raisePlayer] += inc + (self.amountPerPlayer - self.contributions[raisePlayer])
            self.amountPerPlayer += inc

    def reduceBet(self, dec):
        """ Reduces the bet required to stay in the pot (amountPerPlayer) by dec
        and adjusts the amount of chips in the pot and the contributions of each
        player accordingly"""
        self.amountPerPlayer -= dec

        for player in self.Players:
            self.amount -= dec
            self.contributions[player] -= dec

    def addPlayer(self, newPlayer, currentBet):
        """ Adds a player to the pot by increasing the amount by that player's
        bet, adding that player to the list of players in the pot, and changing
        amountPerPlayer as needed. If the pot is not the current pot, we just
        change the amount in the pot by amountPerPlayer"""
        if self.currentPot and newPlayer.bet > currentBet:
            self.Players += [newPlayer]
            self.contributions[newPlayer] = 0
            self.increaseBet(newPlayer, newPlayer.bet - currentBet)
        else:
            self.amount += self.amountPerPlayer
            self.Players += [newPlayer]
            self.contributions[newPlayer] = self.amountPerPlayer
    
    def stayIn(self, allinPlayer):
        """ Increases the given player's contribution to this pot to the
        amountPerPlayer, and changes the amount in the pot accordingly"""
        self.amount += self.amountPerPlayer - self.contributions[allinPlayer]
        self.contributions[allinPlayer] = self.amountPerPlayer
    
    def foldPlayer(self, fPlayer):
        """ Folds a player from the pot by removing that player from the list 
        of players in the pot and their contributions from the contribution 
        dictionary"""
        if fPlayer.inPot(self):
            del self.contributions[fPlayer]
            self.Players.remove(fPlayer)

    def removePlayer(self, remPlayer):
        """ Removes a player from the pot by removing that player from the list 
        of players in the pot and their contributions from the contribution 
        dictionary, then reducing the amount of the pot"""
        if remPlayer.inPot(self):
            self.amount -= self.contributions[remPlayer]
            del self.contributions[remPlayer]
            self.Players.remove(remPlayer)

    def lastPlayer(self):
        """ Returns the last Player in the Pot, if there is one. Otherwise
        returns None"""
        if len(self.Players) == 1:
            return self.Players[0]
        else:
            return None

    def resolve(self, winPlayers):
        """ Resolves the pot in favor of the winPlayers"""
        # Print a message declaring the winning player(s)
        if len(winPlayers) == 1:
            print("Player", winPlayers[0].name, "has won the pot.\n")

        else:
            s = "Players "
            for winPlayer in winPlayers[0:-1]:
                s += winPlayer.name + ", "
            
            s += "and " + winPlayers[-1].name + " split the pot.\n"
            print(s)

        # Set winning player flags
        for winPlayer in winPlayers:
            winPlayer.won = True

        # Find an even amount to award each player
        wonChips = self.amount // len(winPlayers)

        # If amount is not evenly divisible, keep track of the odd chips
        oddChips = self.amount % len(winPlayers)
        
        # Resolve bets for all Players in the pot
        for player in self.Players:
            # Award the odd chips to the Players at the beginning of winPlayers
            if oddChips > 0:
                player.resolveBet(wonChips + 1)
                oddChips -= 1
            else:
                player.resolveBet(wonChips)

class Table:
    """ Creates a representation of a poker table. This includes 7 lists of 
    Player objects: a list of players still in the game, a list of all players,
    a list of players that have gone bankrupt, a list of players that have folded, 
    a list of players who are currently all-in, a list of players who are all-in 
    whose bets have been resolved to pots, and a list of players in the current 
    betting rotation. The table also keeps track of the small blind, big blind, 
    and current bet as integers, and keeps a list of all pots on the table (main 
    pot and side pots)
    """
    def __init__(self, Players = [], allPlayers = [], bankruptPlayers = [], foldedPlayers = [], allinPlayers = [], resolvedAllinPlayers = [], rotation = [], smallBlind = 0, bigBlind = 0, currentBet = 0, pots = []):
        self.Players = Players
        self.allPlayers = allPlayers
        self.bankruptPlayers = bankruptPlayers
        self.foldedPlayers = foldedPlayers
        self.allinPlayers = allinPlayers
        self.resolvedAllinPlayers = resolvedAllinPlayers
        self.rotation = rotation
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        self.currentBet = currentBet
        self.pots = pots

    def __del__(self):
        """ When deleting the Table, delete all of the Players within it as well."""
        for player in self.Players:
            del player
        for pot in self.pots:
            del pot

    def getPlayerByString(self, name):
        """ Returns the player whose name matches the given
        input. Returns None if the player doesn't exist"""
        for player in self.Players:
            if player.name == name:
                return player
        return None

    def allPlayersAllin(self):
        """ Returns True if all Players left unfolded are all-in.
        False otherwise"""
        return all(player.allin or player.folded for player in self.Players)

    def lastPlayer(self):
        """ Returns True if there is one or fewer players left in the rotation"""
        count = 0
        for player in self.rotation:
            if not player.folded and not player.allin:
                count += 1

        return count <= 1

    def allPlayersFolded(self):
        """ Returns True if all players but one have folded"""
        count = 0
        for player in self.Players:
            if not player.folded:
                count += 1

        return count == 1

    def winningPlayer(self):
        """ Returns the last Player with chips. If more than one Player
        still have chips, return None."""
        numPlayers = 0
        winPlayer = None

        for player in self.Players:
            # For every Player with chips, increment numPlayers and set winPlayer to the current Player
            if player.chips > 0:
                numPlayers += 1
                winPlayer = player

            # Break out of the loop if we exceed one Player with chips left
            if numPlayers > 1:
                break
        
        # If there is only one Player with chips, return them, otherwise return None
        if numPlayers == 1:
            return winPlayer
        
        else:
            return None

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
                elif "," in name or " " in name:
                    print("Player names cannot have spaces or commas. Please choose another name.\n")
                    continue
                else:
                    playernames += [name]
                    break

        while True:
            startChips = get_int("How many chips should each player start with? ")
            if startChips < 2:
                print("Please choose a higher number for starting chips.\n")
                continue
            else:
                break
        
        # Fill up Players and allPlayers
        for player in playernames:
            p = Player(player, startChips)
            self.Players += [p]
            self.allPlayers += [p]
    
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
    
    def getPreFlopRotation(self, Round):
        """ Uses the Round number to determine the (pre-flop) betting rotation."""
        # Set indices in player list for dealer and blinds
        playerCount = len(self.allPlayers)
        dealer = (Round - 1) % playerCount

        # If the Player who should be the dealer is out, cycle to the next Player
        while(self.allPlayers[dealer] in self.bankruptPlayers):
            dealer = (dealer + 1) % playerCount

        dealer = self.Players.index(self.allPlayers[dealer])

        playerCount = len(self.Players)

        if (playerCount > 2):
            blind1 = (dealer + 1) % playerCount
            blind2 = (dealer + 2) % playerCount
        else:
            blind1 = (dealer + 1) % playerCount
            blind2 = dealer
        
        print("Player", self.Players[dealer].name, "is the dealer.\n")

        # Update self.rotation with the Players in their preflop rotation order
        for i in range((blind2 + 1) % playerCount, playerCount):
            self.rotation += [self.Players[i]]
        for i in range((blind2 + 1) % playerCount):
            self.rotation += [self.Players[i]]

    def getRotation(self, Round):
        """ Uses the Round number to determine the betting rotation."""
        # Set indices in player list for the dealer
        playerCount = len(self.Players) - len(self.foldedPlayers) - len(self.resolvedAllinPlayers)
        dealer = (Round - 1) % playerCount

        # Create a temporary filtered list of players who are still in the game
        filtPlayers = [player for player in self.Players if player not in self.foldedPlayers and player not in self.resolvedAllinPlayers]

        # Update self.rotations with the Players in their regular rotation order
        for i in range((dealer + 1) % playerCount, playerCount):
            self.rotation += [filtPlayers[i]]
        for i in range((dealer + 1) % playerCount):
            self.rotation += [filtPlayers[i]]

    def preflop(self):
        """ Handles the pre-flop betting rotation"""
        # Handle small blind
        if self.rotation[-2].chips > self.smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and starts with a bet of", self.smallBlind, "chips.")
            self.rotation[-2].Call(self.smallBlind)
        elif self.rotation[-2].chips == self.smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and is all in with", self.smallBlind, "chips.")
            self.rotation[-2].allIn()
            self.allinPlayers += [self.rotation.pop(-2)]
        else:
            print("Player", self.rotation[-2].name, "is small blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-2].chips, "chips.")
            self.rotation[-2].allIn()
            self.allinPlayers += [self.rotation.pop(-2)]
        
        # Handle big blind
        if self.rotation[-1].chips > self.bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and starts with a bet of", self.bigBlind, "chips.\n")
            self.rotation[-1].Call(self.bigBlind)
        elif self.rotation[-1].chips == self.bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and is all in with", self.bigBlind, "chips.\n")
            self.rotation[-1].allIn()
            self.allinPlayers += [self.rotation.pop(-1)]
        else:
            print("Player", self.rotation[-1].name, "is big blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-1].chips, "chips.\n")
            self.rotation[-1].allIn()
            self.allinPlayers += [self.rotation.pop(-1)]

        # Set the currentBet to the highest bet made by the players in the blinds and create the pots
        if self.allinPlayers == []:
            self.currentBet = self.bigBlind
        elif len(self.allinPlayers) == 1:
            self.currentBet = max(self.rotation[-1].bet, self.allinPlayers[0].bet)
        else:
            self.currentBet = max(self.allinPlayers[0].bet, self.allinPlayers[1].bet)
            
        self.createPots()

        # If bettingRotation exited with a True, return True (to end betting)
        if self.bettingRotation():
            # Reset rotation
            self.rotation = []
            return True

        # Reset rotation
        self.rotation = []

        # Print info
        self.playerInfo(self.Players)
        self.potInfo()
        print("\n")

        return False

    def postflop(self):
        """ Handles betting rotations past the pre-flop rotation"""
        # Reset currentBet and player bets
        self.currentBet = 0
        for player in self.Players:
            player.bet = 0

        # If bettingRotation exited with a True, return True (to end betting)
        if self.bettingRotation():
            # Reset rotation
            self.rotation = []
            return True

        # Reset rotation
        self.rotation = []

        # Print info
        self.playerInfo(self.Players)
        self.potInfo()
        print("\n")

        return False

    def bettingRotation(self):
        """ Handles a single betting rotation. Returns True if only 1 player
        is still in the pot, False otherwise"""
        # Continue until all bets are settled
        while True:
            for player in self.rotation:
                # If there is one player or none left in the rotation and the remaining player does not need to bet, return True
                if self.allPlayersFolded() or (self.lastPlayer() and player.bet >= self.currentBet):
                    return True

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
                        x = str(input(player.name + ", what action would you like to take? You do not have enough chips to raise. Type in 'c' to call (all-in) or 'f' to fold. "))
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
                        x = str(input(player.name + ", what action would you like to take? You do not have enough chips to raise. Type in 'c' to call, 'a' to go all-in, or 'f' to fold. "))
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
                    # Prevent the player from betting again until someone else raises
                    player.canBet = False

                    if self.currentBet == player.bet:
                        print("Player", player.name, "has checked. \n")
                    elif self.currentBet - player.bet >= player.chips:
                        self.allIn(player)
                        print(player, "\n")
                    else:
                        print("Player", player.name, "has called. \n")
                        player.Call(self.currentBet)
                        self.stay(player)
                
                # Player raises
                elif x == 'r':
                    while True:
                        # Re-allow all other players to bet
                        for betPlayer in self.Players:
                            betPlayer.canBet = True
                        
                        # Prevent the player from betting again until someone else raises
                        player.canBet = False

                        r = get_int("How much do you want to raise by? ")
                        if r == player.chips - (self.currentBet - player.bet):
                            self.allIn(player)
                            print(player, "\n")
                            break
                        elif r > player.chips - (self.currentBet - player.bet):
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
                    # If allIn raises the currentBet, re-allow all other players to bet
                    if player.chips + player.bet > self.currentBet:
                        for betPlayer in self.Players:
                            betPlayer.canBet = True

                    self.allIn(player)
                    print(player, "\n")
                
                # Player folds            
                elif x == 'f':
                    self.fold(player)
                    print(player, "\n")
            
            # Remove folded players from rotation
            for player in self.foldedPlayers:
                if player in self.rotation:
                    self.rotation.remove(player)
            
            # Remove all-in players from rotation and move them from allinPlayers to resolved players
            for player in self.allinPlayers:
                self.rotation.remove(player)
                self.resolvedAllinPlayers += [player]

            # Clear allinPlayers
            self.allinPlayers = []

            # If everyone left in the rotation has met the current bet, end the rotation
            if all(player.bet >= self.currentBet for player in self.rotation):
                # Reallow betting for next rotation
                for player in self.rotation:
                    player.canBet = True
                
                # Return whether or not there is a single or no players left in the rotation
                return self.lastPlayer()

    def getWinners(self, pstrings, pot):
        """ Returns a list of winning Players based on a list of their names. 
        Will print an error message and return None to signify an invalid player
        name in pstrings """
        # Initialize list of players
        players = []

        # Lookup players by their name and add them to a list of winning players
        for pstring in pstrings:
            player = self.getPlayerByString(pstring)

            # Print an error message if the given Player does not exist
            if player == None:
                print("Player", pstring, "does not exist. Please input a valid name.\n")
                return None

            # If the Player exists and is in the pot, add them to the players
            elif player.inPot(pot):
                players += [player]

            # Print an error message if the given Player is not in the Pot
            else:
                print("This player is not in this pot. Please input a valid name.\n")
                return None

        return players

    def resolvePots(self, board = None):
        """ Resolves all of pots at the end of a Round."""
        # Print pot info
        self.potInfo()
        print("\n")

        # Create a variable for keeping track of the last Players to win one of the pots
        lastWinners = []

        for pot in self.pots:
            print(pot)

            # Check to see if there is only one player in the pot and store them in a variable
            lastPlayer = pot.lastPlayer()

            # If there is only one player in the pot, automatically resolve it in their favor
            if lastPlayer != None:
                pot.resolve([lastPlayer])

            else: 
                while True:
                    # Filter lastWinners based on whether or not they are in the pot
                    lastWinners = list(filter(lambda x: x.inPot(pot), lastWinners))
                    
                    # If there are lastWinners in the pot, automatically resolve it in their favor
                    if lastWinners != []:
                        pot.resolve(lastWinners)
                        
                        # Delete the pot object
                        del pot
                        break

                    # If a board argument has been provided, automatically resolve the pot based on the Hands of the players in the pot and the board
                    elif board != None:
                        # Create a list of the hands of the players in the pot
                        hands = list(map(lambda x: x.hand, pot.Players))
                        
                        # Find a list of the players that have won the pot
                        winners = []
                        for i in HandHelper.findWinner(hands, board):
                            winners += [pot.Players[i]]

                        # Resolve the pots in favor of the winners and save them as the lastWinners
                        pot.resolve(winners)
                        lastWinners = winners
                            
                        # Delete the pot object and break
                        del pot
                        break
                    
                    else:
                        p = str(input("Which player won this pot? (If multiple players split the pot, separate their names with a comma and a space) "))

                        # Print an error if nothing was entered
                        if p == "":
                            print("Please enter at least one player.\n")
                            continue
                        
                        # Convert input to list of strings
                        pstrings = p.split(", ")

                        # Get a list of players from pstrings
                        winners = self.getWinners(pstrings, pot)

                        # If we had an invalid player in our input, get the input again
                        if winners == None:
                            continue

                        # Resolve the pots in favor of the winners and save them as the lastWinners
                        pot.resolve(winners)
                        lastWinners = winners
                            
                        # Delete the pot object and break
                        del pot
                        break

        # Check if players are bankrupt
        for player in self.Players:
            # Resolve bets for folded players
            if player.folded:
                player.resolveBet(0)

            elif player.allIn:
                player.resolveBet(0)

            if player.chips == 0:
                self.bankruptPlayers += [player]
                print("Player", player.name, "has been eliminated from play")

        # Remove bankrupt players from players list
        for player in self.bankruptPlayers:
            if player in self.Players:
                self.Players.remove(player)

        # Reset folded players, resolvedAllInPlayers, and the pots list
        self.foldedPlayers = []
        self.resolvedAllinPlayers = []
        self.pots = []

        # Print the players
        self.playerInfo(self.Players)
    
    def stay(self, stayPlayer):
        """ Makes a player call/raise and changes the pots accordingly"""
        # Add the player to any pots below the current pot that the player is not already in
        for pot in self.pots[:-1]:
            if not stayPlayer.inPot(pot):
                pot.addPlayer(stayPlayer, self.currentBet)
            elif pot.contributions[stayPlayer] != pot.amountPerPlayer:
                pot.stayIn(stayPlayer)

        # Add the player to the current pot if they aren't in it        
        if not stayPlayer.inPot(self.pots[-1]):
            # If there are any all-in players in the current pot and stayPlayer has raised, create a new side pot
            if not all(not player.allin for player in self.pots[-1].Players) and stayPlayer.bet > self.currentBet:
                self.addSidePot(stayPlayer.bet - self.currentBet, stayPlayer)
                self.pots[-2].addPlayer(stayPlayer, self.currentBet)
            else:
                self.pots[-1].addPlayer(stayPlayer, self.currentBet)

        # If they are, increase the bet to stay in the pot as necessary
        else:
            # If there are any all-in players in the current pot and stayPlayer has raised, create a new side pot
            if not all(not player.allin for player in self.pots[-1].Players) and stayPlayer.bet > self.currentBet:
                self.addSidePot(stayPlayer.bet - self.currentBet, stayPlayer)
                self.pots[-2].addPlayer(stayPlayer, self.currentBet)
            else:
                if stayPlayer.bet > self.currentBet:
                    self.pots[-1].increaseBet(stayPlayer, stayPlayer.bet - self.currentBet)
                else:
                    self.pots[-1].stayIn(stayPlayer)

    def allIn(self, allinPlayer):
        """ Puts a player all-in and changes the pots accordingly"""
        allinPlayer.allIn()
        
        # Initialize a sum to keep track of how many chips are needed to get into each successive pot
        betSum = 0

        # Iterate through all pots
        for pot in self.pots:
            # Run a special case for the current Pot
            if pot.currentPot:
                # Actions will change based on whether or not the allinPlayer is in the pot
                if allinPlayer.inPot(pot):
                    # If the player has exactly the amount of chips to stay in the pot, keep them in
                    if allinPlayer.bet == self.currentBet:
                        pot.stayIn(allinPlayer)
                        break

                    # If the player has less than the amount of chips needed to stay in the pot, remove them and create a new pot
                    elif allinPlayer.bet < self.currentBet:
                        pot.removePlayer(allinPlayer)
                        self.insertPot(allinPlayer, allinPlayer.bet - betSum, pot)
                        break

                    # If the player has more chips than the current bet, act as if the player has raised.
                    else:
                        # If there are any all-in players (other than the player that just went all-in) in the current pot and allinPlayer has raised, create a new side pot
                        if not all(not player.allin for player in list(filter(lambda x: x.name != allinPlayer.name, pot.Players))):
                            self.addSidePot(allinPlayer.bet - self.currentBet, allinPlayer)
                            self.pots[-2].stayIn(allinPlayer)
                        else:
                            pot.increaseBet(allinPlayer, allinPlayer.bet - self.currentBet)
                        break

                else:
                    # If the player has the exact amount of chips needed to get into the pot, add them and break
                    if allinPlayer.bet == self.currentBet:
                        pot.addPlayer(allinPlayer, self.currentBet)
                        break

                    # If the player has less than the amount of chips needed to get into the pot, insert a new pot and break
                    elif allinPlayer.bet < self.currentBet:
                        self.insertPot(allinPlayer, allinPlayer.bet - betSum, pot)
                        break

                    # If the player has more chips than the current bet, act as if the player has raised.
                    else:
                        # If there are any all-in players in the current pot and allinPlayer has raised, create a new side pot
                        if not all(not player.allin for player in pot.Players):
                            self.addSidePot(allinPlayer.bet - self.currentBet, allinPlayer)
                            self.pots[-2].addPlayer(allinPlayer, self.currentBet)
                        else:
                            pot.addPlayer(allinPlayer, self.currentBet)
                        break

            else:
                # Actions will change based on whether or not the allinPlayer is in the pot
                if allinPlayer.inPot(pot):
                    # If the player is already fully in the pot, skip it and increment betsum
                    if pot.contributions[allinPlayer] == pot.amountPerPlayer:
                        betSum += pot.amountPerPlayer

                    # If the player has the exact amount of chips needed to stay in the pot, keep them in and break 
                    elif allinPlayer.bet == betSum + pot.amountPerPlayer :
                        pot.stayIn(allinPlayer)
                        break

                    # If the player has more than the amount of chips needed to get into the pot, keep them in and increment betsum
                    elif allinPlayer.bet > betSum + pot.amountPerPlayer:
                        pot.stayIn(allinPlayer)
                        betSum += pot.amountPerPlayer

                    # If the player has less than the amount of chips needed to stay in the pot, remove them,
                    # insert a new pot, and break
                    else:
                        pot.removePlayer(allinPlayer)
                        self.insertPot(allinPlayer, allinPlayer.bet - betSum, pot)
                        break
                
                else:
                    # If the player has the exact amount of chips needed to get into the pot, add them and break 
                    if allinPlayer.bet == betSum + pot.amountPerPlayer:
                        pot.addPlayer(allinPlayer, self.currentBet)
                        break

                    # If the player has more than the amount of chips needed to get into the pot, add them and increment betsum
                    elif allinPlayer.bet > betSum + pot.amountPerPlayer:
                        pot.addPlayer(allinPlayer, self.currentBet)
                        betSum += pot.amountPerPlayer

                    # If the player has less than the amount of chips needed to get into the pot, insert a new pot and break
                    else:
                        self.insertPot(allinPlayer, allinPlayer.bet - betSum, pot)
                        break

        # If the player has raised with their all-in, increase the currentBet
        if allinPlayer.bet > self.currentBet:
            self.currentBet = allinPlayer.bet

        self.allinPlayers += [allinPlayer]
    
    def fold(self, foldPlayer):
        """ Folds a player from the pots and changes the pots accordingly"""
        # Set the folded flag
        foldPlayer.fold()
        # Remove the folded player from all the pots
        for pot in self.pots:
            pot.foldPlayer(foldPlayer)
        # Add them to the folded players list
        self.foldedPlayers += [foldPlayer]

    def createPots(self):
        # Sort the allinPlayers from least to greatest
        self.allinPlayers = chipMSort(self.allinPlayers)
        
        # Iterate through the players who are all-in but haven't had their bets put into pots yet
        for player in self.allinPlayers:
            i = self.allinPlayers.index(player)
            
            # If there are no pots so far, create the main pot
            if self.pots == []:
                self.pots += [Pot(amount = player.bet * (len(self.allinPlayers) - i), Players = self.allinPlayers[i:], mainPot = True)]
            
            # Otherwise, create the next side pot
            else:
                self.pots += [Pot(amount = player.bet - self.pots[i - 1].amountPerPlayer * (len(self.allinPlayers) - i), Players = self.allinPlayers[i:], mainPot = False)]

            # Move the player to resolvedAllinPlayers
            self.resolvedAllinPlayers += [player]
        
        self.allinPlayers = []
        
        # If there are no pots so far, create the main pot with the blinds
        if self.pots == []:
            self.pots += [Pot(amount = self.rotation[-2].bet + self.rotation[-1].bet, Players = self.rotation[-2:], mainPot = True)]
            self.pots[-1].setAmountPerPlayer(self.bigBlind)

        # Set the latest pot's currentPot flag to True
        self.pots[-1].currentPot = True
    
    def addSidePot(self, newAmount, newPlayer):
        """ Creates a new side pot to be the new current pot 
        for the Round"""
        # Set currentPot to false for the old current pot
        self.pots[-1].currentPot = False

        # Add a new side pot with just the latest player in it
        self.pots += [Pot(amount = newAmount, Players = [newPlayer], mainPot = False, currentPot = True)]

    def insertPot(self, newPlayer, newAmountPerPlayer, nextPot):
        """ Create a new pot right before the nextPot"""
        # Keep track of the new number of chips and keep a list of players that can be bumped down to the inserted pot
        newAmount = newAmountPerPlayer
        bumpedPlayers = []

        # Add up the contributions of each of the players in the next pot to the new inserted pot
        for player in nextPot.Players:
            # If a player hasn't contributed enough to nextPot, bump them from nextPot
            if nextPot.contributions[player] <= newAmountPerPlayer:
                newAmount += nextPot.contributions[player]
                bumpedPlayers += [player]
                
            else:
                newAmount += newAmountPerPlayer

        # Remove bumped players from nextPot
        for player in bumpedPlayers:
            nextPot.removePlayer(player)

        # Reduce the bet of nextPot to adjust for the addition of the new Pot and make it a sidePot
        nextPot.reduceBet(newAmountPerPlayer)
        nextPot.mainPot = False

        # Add a new Pot to self.pots
        i = self.pots.index(nextPot)

        self.pots.insert(i, Pot(amount = newAmount, amountPerPlayer = newAmountPerPlayer, Players = nextPot.Players + bumpedPlayers + [newPlayer], mainPot = i == 0, currentPot = False))

def main():
    # Initialize the poker table
    table = Table()

    # Get the players and blinds
    table.getPlayers()
    table.getBlinds()

    gameLoop(table)

def gameLoop(table):
    """ Function for running the main game loop"""
    # Begin looping through rounds until only one player remains with chips
    Round = 0
    while True:
        Round += 1
        print("\nRound", Round)
        # Create a flag indicating whether we should stop the betting and skip to the end
        stopBetting = False

        # Pre-flop
        input("Pre-flop: Press enter \n")
        table.getPreFlopRotation(Round)
        stopBetting = table.preflop() 
        stopBetting = stopBetting or table.allPlayersAllin()

        # Flop
        if (not stopBetting):
            input("Flop: Deal the flop and press enter \n")
            table.getRotation(Round)
            stopBetting = table.postflop()
            stopBetting = stopBetting or table.allPlayersAllin()

        # Turn
        if (not stopBetting):
            input("Turn: Deal the turn and press enter \n")
            table.getRotation(Round)
            stopBetting = table.postflop()
            stopBetting = stopBetting or table.allPlayersAllin()

        # River
        if (not stopBetting):
            input("River: Deal the river and press enter \n")
            table.getRotation(Round)
            table.postflop()

        # Resolve bets
        table.resolvePots()

        # If there is one Player left with chips, end the game
        winner = table.winningPlayer()
        if not winner == None:
            print("Player", winner.name, "has won!")
            break

    del table

def get_int(s):
    """ Returns an integer casting of user input (displays the string s 
    to the user. Validates input to make sure that a positive integer
    is input."""
    while(True):
        try:
            r = int(input(s))
        except:
            print("Please pick a positive integer.\n")
            continue
        if r <= 0:
            print("Please pick a positive integer.\n")
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

def listCopy(L1):
    """ Creates and returns a deep copy of L1"""
    L2 = []

    for item in L1:
        L2 += [item]

    return L2

def preflopTest1():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 100)
    p4 = Player("Deandra", 100)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 1, bigBlind = 2)

    # Do a preflop runthrough
    Round = 1
    print("\nRound", Round)

    table.getPreFlopRotation(Round)
    table.preflop()

    del table

def preflopTest2():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 200)
    p4 = Player("Deandra", 100)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 100, bigBlind = 200)

    # Do a preflop runthrough
    Round = 1
    print("\nRound", Round)

    table.getPreFlopRotation(Round)
    table.preflop()

    del table

def preflopTest3():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 500)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 200)
    p4 = Player("Deandra", 500)
    p5 = Player("Egbert", 600)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 100, bigBlind = 200)

    # Do a preflop runthrough
    Round = 1
    print("\nRound", Round)

    table.getPreFlopRotation(Round)
    table.preflop()

    del table

def gameTest1():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)
    p3 = Player("Cindy", 100)
    p4 = Player("Deandra", 100)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 1, bigBlind = 2)

    gameLoop(table)

def gameTest2():
    # Initialize 5 example players and place them in a list
    p1 = Player("Andrew", 80)
    p2 = Player("Brett", 600)
    p3 = Player("Cindy", 1200)
    p4 = Player("Deandra", 500)
    p5 = Player("Egbert", 100)
    players = [p1, p2, p3, p4, p5]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 1, bigBlind = 2)

    gameLoop(table)

def gameTest3():
    # Initialize 2 example players and place them in a list
    p1 = Player("Andrew", 100)
    p2 = Player("Brett", 100)

    players = [p1, p2]

    # Initialize a table with these players, a small blind of 1 and a big blind of 2
    table = Table(Players = players, allPlayers = listCopy(players), smallBlind = 1, bigBlind = 2)

    gameLoop(table)

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
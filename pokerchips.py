# Huey Fields
# 12/23/16

import functools

debug = True

class Player:
    """ Creates a representation of a player according to 4 traits: 
    their name, how many chips they have, their current bet, whether 
    or not they've won the current pot, and whether or not they've folded."""
    def __init__(self, name = '', chips = 0, bet = 0, won = False, folded = False, allin = False):
        self.name = name
        self.chips = chips
        self.bet = bet
        self.won = won
        self.folded = folded
        self.allin = allin
    
    def __repr__(self):
        """ Returns a string describing the given player"""
        if self.allin == True:
            return "Player " + self.name + " is all in with " + self.bet + " chips."
        else:
            return "Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips."
    
    def printInfo(self):
        """ Prints a string describing the given player"""
        if self.allin == True:
            print("Player " + self.name + " is all in with " + self.bet + " chips.")
        else:
            print("Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips.")

    def resolveBet(self, pot):
        """ Resolves a completed bet by awarding the pot to the winner
        or reinitializing the bet to 0 for a loser"""
        if self.won == True:
            self.bet = 0
            self.chips += pot
        else:
            self.bet = 0

    def Call(self, current_bet):
        """ Increases a player's bet to call"""
        self.chips -= current_bet - self.bet
        self.bet = current_bet     

    def Raise(self, current_bet, raise_amount):
        """ Increases a player's bet to raise by a specified amount"""
        self.chips -= current_bet + raise_amount - self.bet
        self.bet = current_bet + raise_amount

    def Allin(self):
        """ Increase a player's bet so that they are all-in"""
        self.allin = True
        self.bet += self.chips
        self.chips = 0

class Table:
    """ Creates a representation of a poker table. This includes 5 lists of 
    Player objects: a full list of players, a list of players that have gone
    bankrupt, a list of players that have folded, a list of players who are
    currently all-in, and a list of players in the current betting rotation.
    The table also keeps track of the small blind, big blind, and current bet 
    as integers, and keeps a list of all pots on the table (main pot and side pots)
    """
    def __init__(self, Players = [], bankruptPlayers = [], foldedPlayers = [], allinPlayers = [], rotation = [], smallBlind = 0, bigBlind = 0, currentBet = 0, pots = []):
        self.Players = Players
        self.bankruptPlayers = bankruptPlayers
        self.foldedPlayers = foldedPlayers
        self.allinPlayers = allinPlayers
        self.rotation = rotation
        self.smallBlind = smallBlind
        self.bigBlind = bigBlind
        self.currentBet = currentBet
        self.pots = pots
    
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
            s = "Player " + str(i + 1) + ", what is your name? "
            name = input(s)
            playernames += [str(name)]
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
        # Set the main pot to the sum of the blinds and the currentBet to the big blind
        self.pots += [self.bigBlind + self.smallBlind]
        self.currentBet = self.bigBlind
        
        # Handle small blind
        if self.rotation[-2].chips > self.smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and starts with a bet of", self.smallBlind, "chips.")
            self.rotation[-2].Call(self.smallBlind)
        elif self.rotation[-2].chips == smallBlind:
            print("Player", self.rotation[-2].name, "is small blind, and is all in with", self.smallBlind, "chips.")
            self.rotation[-2].Allin()
            self.allinPlayers += self.rotation[-2]
            self.rotation.remove(-2)
        else:
            print("Player", self.rotation[-2].name, "is small blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-2].chips, "chips.")
            self.rotation[-2].Allin()
            self.allinPlayers += self.rotation[-2]
            self.rotation.remove(-2)
        
        # Handle big blind
        if self.rotation[-1].chips > self.bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and starts with a bet of", self.bigBlind, "chips.\n")
            self.rotation[-1].Call(self.bigBlind)
        elif self.rotation[-1].chips == bigBlind:
            print("Player", self.rotation[-1].name, "is big blind, and is all in with", self.bigBlind, "chips.\n")
            self.rotation[-1].Allin()
            self.allinPlayers += self.rotation[-1]
            self.rotation.remove(-1)
        else:
            print("Player", self.rotation[-1].name, "is big blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", self.rotation[-1].chips, "chips.\n")
            self.rotation[-1].Allin()
            self.allinPlayers += self.rotation[-1]
            self.rotation.remove(-1)
        
        playerInfo(self.Players)

    #def bettingRotation(self):






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


    """
        # Single betting rotation (pre-flop). Does a betting rotation and returns the updated player info to be passed onto the next betting rotation
        updated_info = betting_rotation(players, preflop_rotation, allinplayers, current_bet, pot)
        players = updated_info[0]
        allinplayers = updated_info[1]
        current_bet = updated_info[2]
        pot = updated_info[3]

        # Re-initialize pre-flop rotation list and make a regular rotation list (exluding any all-in players).
        preflop_rotation = []
        rotation = []

        for i in range(blind2 + 1, playercount):
            preflop_rotation += [i]
        for i in range(blind2 + 1):
            preflop_rotation += [i]

        for i in range(dealer + 1, playercount):
            rotation += [i]
        for i in range(dealer + 1):
            rotation += [i]

        for i in allinplayers:
            preflop_rotation.remove(i)
            rotation.remove(i)
        
        # If more betting needs to continue, conduct additional rotations
        while all(player.chips == players[preflop_rotation[0]].chips for player in [players[i] for i in preflop_rotation]) == False:
            updated_info = betting_rotation(players, preflop_rotation, allinplayers, current_bet, pot)
            players = updated_info[0]
            allinplayers = updated_info[1]
            current_bet = updated_info[2]
            pot = updated_info[3]
    
        # After pre-flop betting has finished, handle side pots, if applicable
        if len(allinplayers) > 0:
            for player in [players[i] for i in allinplayers]:
                allinbets += [player.bet]
            for player in [players[i] for i in preflop_rotation]:
                bets += [player.bet]
            sidepots = []
            for allinplayer in [players[i] for i in allinplayers]:
                if allinplayer.bet <= max(allinbets[:allinbets.index(player.bet)] + allinbets[allinbets.index(player.bet) + 1:] + [bets]):
                    sidepot = 0
                    for player in players:
                        if player.bet > allinplayer.bet:
                            sidepot += allinplayer.bet
                        else:
                            sidepot += player.bet
                    sidepots += [sidepot]
        
        if len(sidepots) > 0:
            for i in range(len(sidepots)):
                print("A sidepot of", sidepots[i], "has been made. \n")

        print("Betting is finished. Deal the flop.\n")
        
        # Single betting rotation (flop)
        betting_rotation(rotation, allinplayers, current_bet, pot)

        # If more betting needs to continue, conduct additional rotations
        while all(player.chips == rotation[0].chips for player in rotation) == False:
            bets = []
            for player in rotation:
                bets += [player.bet]
            betting_rotation(rotation[:bets.index(max(bets))], allinplayers, current_bet, pot)
    
        # Handle side pots, if applicable
        flop_allin = len(allinplayers)
        if flop_allin > preflop_allin:
            allinbets = []
            bets = []
            for player in allinplayers:
                allinbets += [player.bet]
            for player in rotation:
                bets += [player.bet]
            sidepots = []
            for allinplayer in allinplayers:
                if allinplayer.bet <= max(allinbets[:allinbets.index(player.bet)] + allinbets[allinbets.index(player.bet) + 1:] + [bets]):
                    sidepot = 0
                    for player in players:
                        if player.bet > allinplayer.bet:
                            sidepot += allinplayer.bet
                        else:
                            sidepot += player.bet
                    sidepots += [sidepot]
        
        if len(sidepots) > 0:
            for i in range(len(sidepots)):
                print("A sidepot of", sidepots[i], "has been made. \n")






        # Find winner
        for player in players:
            player.resolveBet(pot)
    """
        
        
def betting_rotation(players, rotation, allinplayers, current_bet, pot):
    """ Handles a single betting rotation"""
    for i in rotation:
        while True:
            print("The current pot size is", pot, "and the current bet is", current_bet, "\n")
            players[i].printInfo()

            # Player has not enough or just enough chips to match the current bet
            if players[i].chips <= current_bet - players[i].bet:
                while True:
                    x = str(input("Player", players[i].name, "what action would you like to take? You do not have enough chips to raise. Type in 'c' to call (all-in) or 'f' to fold."))
                    if x == 'c' or x == 'f':
                        break
                    # Debugger only command. Exits main function
                    elif x == 'q' and debug == True:
                        return
                    # Invalid character entered
                    else:
                        print("Please input a valid character. 'c' to call (all-in) or 'f' to fold. \n")
                        continue
            
            # Player has enough chips to call but not to raise
            elif players[i].chips < 2 * current_bet - players[i].bet:
                while True:
                    x = str(input("Player", players[i].name, "what action would you like to take? You do not have enough chips to raise. Type in 'c' to call, 'a' to go all-in, or 'f' to fold."))
                    if x == 'c' or x == 'a' or x == 'f':
                        break
                    # Debugger only command. Exits main function
                    elif x == 'q' and debug == True:
                        return
                    # Invalid character entered
                    else:
                        print("Please input a valid character. 'c' to call (all-in) or 'f' to fold. \n")
                        continue
            else:
                while True:
                    x = str(input("Player", players[i].name, "what action would you like to take? Type in 'c' to call/check, 'r' to raise, 'a' to go all in, or 'f' to fold. "))
                    if x == 'c' or x == 'r' or x == 'a' or x == 'f':
                        break
                    # Debugger only command. Exits main function
                    elif x == 'q' and debug == True:
                        return
                    # Invalid character entered
                    else:
                        print("Please input a valid character. 'c' to call, 'r' to raise, 'a' to go all-in, or 'f' to fold. \n")
                        continue
            
            # Player calls/checks
            if x == 'c':
                if current_bet == 0:
                    print("Player", players[i].name, "has checked. \n")
                    players[i].printInfo()
                    break
                elif current_bet - players[i].bet >= players[i].chips:
                    players[i].Allin()
                    rotation.remove(i)
                    allinplayers += [i]
                    players[i].printInfo()
                    break
                else:
                    print("Player", players[i].name, "has called. \n")
                    pot += current_bet - players[i].bet
                    players[i].call(current_bet)
                    break
            
            # Player raises
            elif x == 'r':
                while True:
                    r = get_int("How much do you want to raise by?")
                    if r == players[i].chips:
                        players[i].Allin()
                        rotation.remove(i)
                        allinplayers += [i]
                        players[i].printInfo()
                        break
                    elif r > players[i].chips:
                        print("You do not have enough chips to raise by that amount. \n")
                        continue
                    elif r >= current_bet:
                        pot += current_bet + r - players[i].bet
                        players[i].Raise(current_bet, raise_amount)
                        current_bet += r
                        print("Player", player.name, "has raised to", current_bet, "\n")
                        players[i].printInfo()
                        break
                    else:
                        print("You must raise by at least as much as the current bet:", current_bet,"\n")
                        continue
            
            # Player goes all-in
            elif x == 'a':
                pot += players[i].chips
                players[i].Allin()
                rotation.remove(i)
                allinplayers += [i]
                players[i].printInfo()
                break
            
            # Player folds            
            elif x == 'f':
                print("Player", players[i].name, "has folded. \n")
                rotation.remove(i)
                break

    return [players, allinplayers, current_bet, pot]

def playerInfo(players):
    """ Prints out important player info"""    
    for player in players:
        player.printInfo()

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
    if len(L) == 1:
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

def preflopTest():
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
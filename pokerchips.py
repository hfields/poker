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
        if player.allin == True:
            return "Player " + self.name + " is all in with " + self.bet + " chips."
        else:
            return "Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips."
    
    def printInfo(self):
        """ Prints a string describing the given player"""
        if player.allin == True:
            print("Player " + self.name + " is all in with " + self.bet + " chips.")
        else:
            print("Player " + self.name + " has " + str(self.chips) + " chips and is betting " + str(self.bet) + " chips.")

    def resolve_bet(self, pot):
        """ Resolves a completed bet by either adding or subtracting 
        chips from the given player"""
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
    def __init__(self, Players = [], foldedPlayers = [], pot = 0):
        self.Players = Players
        self.pot = pot


def main():
    
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
    startchips = get_int("How many chips should each player start with? ")
    
    # Create an array of all the players
    players = []
    for player in playernames:
        players += [Player(player, startchips)]
    
    # Get the amount for big blind and small blind
    while True:
        b = get_int("How much should big blind be (small blind will be half of big blind, rounding down)? ")
        if b <= startchips:
            big_blind = b
            small_blind = round(b/2)
            break
        else:
            print("Big blind cannot be greater than the amount of chips each player starts with.\n")
            continue

    Round = 0
    while True:
        Round += 1
        print("\nRound", Round)
        pot = big_blind + small_blind
        current_bet = big_blind
        dealer = Round % playercount - 1
        
        # Set indices in player list for dealer and blinds
        if (playercount > 2):
            blind1 = dealer - 1
            blind2 = dealer - 2
        else:
            blind1 = dealer - 1
            blind2 = dealer
        print("Player", players[dealer].name, "is the dealer.")

        # Create a list of player indices in their pre-flop rotation order and create an empty list for the indices of players that are all-in.
        preflop_rotation = []
        for i in range(blind2 + 1, playercount):
            preflop_rotation += [i]
        for i in range(blind2 + 1):
            preflop_rotation += [i]
        allinplayers = []

        # Handle small blind
        if players[blind1].chips > small_blind:
            print("Player", players[blind1].name, "is small blind, and starts with a bet of", small_blind, "chips.\n")
            players[blind1].call(small_blind)
        elif players[blind1].chips == small_blind:
            print("Player", players[blind1].name, "is small blind, and is all in with", small_blind, "chips.\n")
            players[blind1].Allin()
            allinplayers += [blind1]
            preflop_rotation.remove(blind1)
        else:
            print("Player", players[blind1].name, "is small blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", players[blind1].chips, "chips.\n")
            players[blind1].Allin()
            allinplayers += [blind1]
            preflop_rotation.remove(blind1)
        
        # Handle big blind
        if players[blind2].chips > big_blind:
            print("Player", players[blind2].name, "is big blind, and starts with a bet of", big_blind, "chips.\n")
            players[blind2].call(big_blind)
        elif players[blind2].chips == big_blind:
            print("Player", players[blind2].name, "is small blind, and is all in with", big_blind, "chips.\n")
            players[blind2].Allin()
            allinplayers += [blind2]
            preflop_rotation.remove(blind2)
        else:
            print("Player", players[blind2].name, "is big blind, but they do not have enough chips to bet the full amount. Instead, they are all-in with a bet of", players[blind2].chips, "chips.\n")
            players[blind2].Allin()
            allinplayers += [blind2]
            preflop_rotation.remove(blind2)
        
        player_info(players)

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
            player.resolve_bet(pot)
        
        
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

def player_info(players):
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
            print("Don't be a bitch. Pick a non-negative integer.\n")
            continue
        if r < 0:
            print("Don't be a bitch. Pick a non-negative integer.\n")
            continue
        else:
            return r


if __name__ == "__main__" and debug == False:
    main()

def rotation_test(blind2, playercount):
    preflop_rotation = []
    for i in range(blind2 + 1, playercount):
        preflop_rotation += [i]
    for i in range(blind2 + 1):
        preflop_rotation += [i]
    return preflop_rotation
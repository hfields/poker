from fbchat.models import *
from fbchat import log, Client
from pokergui import *

class FBPokerBot(Client):
    def __init__(self, email, password, currentPlayer = None, gameThread = None, application = None):
        """ Create a new PokerBot. Inherits from Client class of fbchat library. Additional
        attributes are currentPlayer (the player currently betting), gameThread (the facebook
        messenger thread that comprises the players of the game), and application (the pokergui
        application that handles the actual game)"""
        Client.__init__(self, email, password, max_tries=1)
        self.currentPlayer = currentPlayer
        self.gameThread = gameThread
        self.application = application

    def startGame(self, window, ids):
        """ Starts the online game by setting up the GUI application and creating a group chat"""
        self.application = Application(master = window, bot = self)
        self.gameThread = self.createGroup("Welcome to poker.", ids)

        for i in range(self.application.table.allPlayers):
            self.application.table.allPlayers[i].onlineId = ids[i]

        window.mainloop()
        
        self.application.proceed()

    def dealPlayer(self, player):
        """ Tells a player the contents of their hand"""
        self.send(Message(text="You have been dealt: " + str(player.hand)), thread_id=player.fbid, thread_type=ThreadType.USER)

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        """ Handles the bot being messaged while listening."""
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        
        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
        
        # Don't reply if the bot has messaged itself or if the bot has been messaged from a group
        if author_id != self.uid and thread_type != ThreadType.GROUP:
            text = message_object.text.split()

            # If !help has been detected, show available options
            if text[0] == "!help":
                if self.currentPlayer.fbid == author_id:
                    start = "The action is currently on you. "
                else:
                    start = "The action is currently on " + self.currentPlayer.name + ". "

                self.send(Message(text=start + "\nAvailable commands: \n !help- show options \n !stacks- show stack sizes \n !pots- show pots \n !bets- show current bets"),\
                    thread_id=thread_id, thread_type=ThreadType.USER)

            # If prompted, show stack sizes
            elif text[0] == "!stacks":
                message = ""

                for player in self.application.table.Players:
                    message += player.name + ": " + str(player.chips) + "\n"

                self.send(Message(text=message), thread_id=thread_id, thread_type=ThreadType.USER)

            # If prompted, show pots
            elif text[0] == "!pots":
                message = ""

                for pot in self.application.table.pots:
                    message += str(pot) + "\n"

                self.send(Message(text=message), thread_id=thread_id, thread_type=ThreadType.USER)

            # If prompted, show bets
            elif text[0] == "!bets":
                message = ""

                for player in self.application.table.Players:
                    message += player.name + ": " + str(player.bet) + "\n"

                message += self.application.currentBet.get()

                self.send(Message(text=message), thread_id=thread_id, thread_type=ThreadType.USER)
                    
            # If the current player has messaged the bot, parse their input to see how they have bet
            elif author_id == self.currentPlayer.fbid:
                
                # Handle calling, going all-in, or folding
                if text[0] == 'c' or text[0] == 'a' or text[0] == 'f':
                    # Set bet in application
                    self.application.setBet(self.currentPlayer, text[0])
                    
                    # Find the proper string for the action taken
                    action = ""

                    if text == 'c':
                        action = "called"
                    
                    elif text == 'a':
                        action = "raised"

                    else:
                        action = "folded"

                    # Send a message to the gameThread and the current player, stop listening, and proceed the application
                    self.send(Message(text="Player " + self.currentPlayer.name + " has " + action + "\n" + self.application.potString.get() + "\n" + self.application.currentBet.get()),\
                        thread_id=self.gameThread, thread_type=ThreadType.GROUP)
                    self.send(Message(text="You have " + action), thread_id=thread_id, thread_type=ThreadType.USER)

                    self.stopListening()
                    self.application.proceed()
                    
                # Handle raising
                elif text[0] == 'r':
                    # Check to see if the raise amount is valid
                    try:
                        raiseAmount = int(text[1])

                        # If the raiseAmount is too low, notify the player
                        if raiseAmount != self.currentPlayer.chips - (self.application.table.currentBet - self.currentPlayer.bet)\
                            and raiseAmount <= self.application.table.currentBet:

                            self.send(Message(text="Invalid raise amount. Please raise at least as much as the current bet (or go all-in)."),\
                                thread_id=thread_id, thread_type=ThreadType.USER)

                        else:
                            # Set bet in application
                            self.application.setBet(self.currentPlayer, text[0], raiseAmount)

                            # Send a message to the gameThread and the current player, stop listening, and proceed the application
                            self.send(Message(text="Player " + self.currentPlayer.name + " has " + action), thread_id=self.gameThread, thread_type=ThreadType.GROUP)
                            self.send(Message(text="You have " + action), thread_id=thread_id, thread_type=ThreadType.USER)

                            self.stopListening()
                            self.application.proceed()

                    except:
                        self.send(Message(text="Invalid raise amount. Please provide a valid integer."), thread_id=thread_id, thread_type=ThreadType.USER)

            # If the wrong player has responded, notify them that it is not their turn
            else:
                self.send(Message(text="It is not your turn. The current player is " + self.currentPlayer.name), thread_id=thread_id, thread_type=ThreadType.USER)
    
    def findIds(self, names):
        """ Takes in a list of player names and returns a string-string 
        dictionary of ID suggestions for each name"""
        idSuggestions = {}
        for name in names:
            idSuggestion = self.searchForUsers(name)
            idSuggestions[name] = idSuggestion

        return idSuggestions

    def updateBoard(self, state, board):
        """ Send a message to the gameThread updating players on the state of the board"""
        self.send(Message(text="Dealing the " + state + ".\n The board is now " + str(board)), thread_id=self.gameThread, thread_type=ThreadType.GROUP)

    def declareWinners(self, winners, potAmount):
        """ Messages the group chat with the winner of a pot"""
        start = "Player " + winners[0].name + " has"

        if len(winners) > 1:
            start = "Players "
            for winner in winners[:-1]:
                start += winner.name + ", "

            start += "and " + winners[-1].name + " have"

        self.send(Message(text=start + " won the pot (" + potAmount + " chips)"), thread_id=self.gameThread, thread_type=ThreadType.GROUP)

    def getPlayerResponse(self, player):
        """ Set the currentPlayer, prompt them to bet, and listen for a response"""
        self.currentPlayer = player
        self.send(Message(text="It is " + player.name + '\'s turn to bet.'), thread_id=self.gameThread, thread_type=ThreadType.GROUP)
        self.send(Message(text="Player " + player.name + ', it is your turn to bet. Reply "c" to call, "a" to go all-in, "f" to fold, and "r <amount>" to raise.'),\
            thread_id=player.fbid, thread_type=ThreadType.USER)
        self.listen()

def test():
    email = input("Input facebook email: ")
    password = input("Input facebook password: ")

    client = FBPokerBot(email, password)
    while True:
        name = input("Input name: ")
        if name == "quit":
            break
        
        else:
            print(client.searchForUsers(name))

if __name__ == "__main__":
    test()
from discord import *
from pokergui import *
import asyncio
from poker import *

TOKEN = ""
channelId = ""

class DiscordPokerBot(Client):
    def __init__(self, token, channelId, table, currentPlayer = None, application = None, names = None):
        """ Create a new PokerBot. Inherits from Client class of discord.py library. Additional
        attributes are currentPlayer (the player currently betting), gameThread (the facebook
        messenger thread that comprises the players of the game), and application (the pokergui
        application that handles the actual game)"""
        Client.__init__(self)
        self.application = Application(table = table, bot = self)
        self.token = token
        self.channelId = channelId
        self.currentPlayer = currentPlayer
        self.names = names
        self.state = "findIds"
        self.run(token)

    async def on_ready(self):
        self.gameThread = self.get_channel(self.channelId)
        await self.send_message(self.gameThread, "Get ready for Poker!")
        self.joinIndex = 0
        await self.send_message(self.gameThread, "Player " + self.names[self.joinIndex] + '! Type "!join" to join the game!')

    async def dealPlayer(self, player):
        """ Tells a player the contents of their hand"""
        user = await(self.get_user_info(player.onlineId))
        await self.send_message(user, player.name + ", you have been dealt: " + str(player.hand))
        for card in player.hand.cards:
            #with open("Cards/" + repr(card) + ".png", 'rb') as picture:
            await self.send_file(user, "Cards/" + repr(card) + ".png")

    async def on_message(self, message):
        """ Handles the bot being messaged while listening."""
        # Don't reply if the bot has messaged itself or if the bot has been messaged from a group
        if message.author != self.user:
            text = message.content.split()

            # If we are finding Ids, check to see if a member is joining under a particular name
            if self.state == "findIds":
                if text[0] == "!join":
                    self.application.table.allPlayers[self.joinIndex].onlineId = message.author.id    
                    self.joinIndex += 1

                    # If everyone has joined, proceed the application
                    if self.joinIndex == len(self.names):
                        self.state = "game"
                        await self.send_message(self.gameThread, "Starting game!")
                        await self.application.proceed()

                    else:
                        await self.send_message(self.gameThread, "Player " + self.names[self.joinIndex] + '! Type "!join" to join the game!')

            elif self.state == "game":
                # If !help has been detected, show available options
                if text[0] == "!help":
                    user = await self.get_user_info(self.currentPlayer.onlineId)
                    if user == message.author:
                        start = "The action is currently on you. "
                    else:
                        start = "The action is currently on " + self.currentPlayer.name + ". "

                    await self.send_message(message.channel, start + "\nAvailable commands: \n !help- show options \n !stacks- show stack sizes \n !pots- show pots \n !bets- show current bets")

                # If prompted, show stack sizes
                elif text[0] == "!stacks":
                    info = ""

                    for player in self.application.table.Players:
                        info += player.name + ": " + str(player.chips) + "\n"

                    await self.send_message(message.channel, info)

                # If prompted, show pots
                elif text[0] == "!pots":
                    info = ""

                    for pot in self.application.table.pots:
                        info += str(pot) + "\n"

                    await self.send_message(message.channel, info)
                
                # If prompted, show bets
                elif text[0] == "!bets":
                    info = ""

                    for player in self.application.table.Players:
                        info += player.name + ": " + str(player.bet) + "\n"

                    info += self.application.currentBet

                    await self.send_message(message.channel, info)
                        
                # If the current player has messaged the bot, parse their input to see how they have bet
                elif message.author.id == self.currentPlayer.onlineId:
                    
                    # Handle calling, going all-in, or folding
                    if text[0] == 'c' or text[0] == 'a' or text[0] == 'f':
                        # Find the proper string for the action taken
                        action = ""
                        name = self.currentPlayer.name

                        if text[0] == 'c':
                            action = "called"
                        
                        elif text[0] == 'a':
                            action = "gone all-in"

                        else:
                            action = "folded"

                        # Send a message to the current player
                        await self.send_message(message.channel, "You have " + action)
                        
                        # Set bet in application and send a message to the gameThread
                        await self.application.setBet(self.currentPlayer, text[0])
                        await self.send_message(self.gameThread, "Player " + name + " has " + action + "\n" + self.application.potString + "\n" + self.application.currentBet)
                        
                    # Handle raising
                    elif text[0] == 'r':
                        # Check to see if the raise amount is valid
                        try:
                            raiseAmount = int(text[1])

                            # If the raiseAmount is too low, notify the player
                            if raiseAmount != self.currentPlayer.chips - (self.application.table.currentBet - self.currentPlayer.bet)\
                                and raiseAmount <= self.application.table.currentBet:

                                await self.send_message(message.channel, "Invalid raise amount. Please raise at least as much as the current bet (or go all-in).")

                            else:
                                name = self.currentPlayer

                                # Send a message to the current player
                                
                                await self.send_message(message.channel, "You have raised by " + str(raiseAmount))
                                
                                # Set bet in application and send a message to the gameThread
                                await self.application.setBet(self.currentPlayer, text[0], raiseAmount)
                                await self.send_message(self.gameThread, "Player " + name + " has raised by " + str(raiseAmount))

                        except Exception as e:
                            print(e)
                            await self.send_message(message.channel, "Invalid raise amount. Please provide a valid integer.")

                    # Proceed to the next Player (or to the end of betting)
                    await self.application.proceed()

                # If the wrong player has responded, notify them that it is not their turn
                else:
                    await self.send_message(message.channel, "It is not your turn. The current player is " + self.currentPlayer.name)

    async def updateBoard(self, state, board):
        """ Send a message to the gameThread updating players on the state of the board"""
        await self.send_message(self.gameThread, "Dealing the " + state + ".\nThe board is now " + str(board))

    async def sendMessagetoGamethread(self, message):
        """ Send the given message to the gameThread. Used so that outside functions can easily send
        any message to the gameThread."""
        await self.send_message(self.gameThread, message)

    async def declareWinners(self, winners, potAmount):
        """ Messages the group chat with the winner(s) of a pot"""
        start = "Player " + winners[0].name + " has"

        if len(winners) > 1:
            start = "Players "
            for winner in winners[:-1]:
                start += winner.name + ", "

            start += "and " + winners[-1].name + " have"

        await self.send_message(self.gameThread, start + " won the pot (" + str(potAmount) + " chips)")

    async def endGame(self, winner):
        """ Send a message to the gameThread congratulating the winner of the game"""
        await self.send_message(self.gameThread, "Congratulations! " + winner.name + " has won!")
        await self.logout()
        await self.close()

    async def getPlayerResponse(self, player):
        """ Set the currentPlayer, message the group chat, and prompt them to bet"""
        self.currentPlayer = player
        user = await self.get_user_info(self.currentPlayer.onlineId)
        await self.send_message(self.gameThread, "It is " + player.name + '\'s turn to bet.')
        await self.send_message(user, "Player " + player.name + ', it is your turn to bet. Reply "c" to call, "a" to go all-in, "f" to fold, and "r <amount>" to raise.')

def test():
    # Grab info from logininfo.txt
    global TOKEN, channelId
    f = open("logininfo.txt", "r")
    info = f.readlines()
    TOKEN = info[2][:-1]
    channelId = info[3]

    table = Table()
    client = DiscordPokerBot(token = TOKEN, table = table, channelId = channelId)
    client.run(client.token)

if __name__ == "__main__":
    test()
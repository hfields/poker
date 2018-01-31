# Huey Fields
# 1/30/18

import unittest
from pokerchips import Table
from pokerchips import Player
from pokerchips import Pot

class TestPokerChips(unittest.TestCase):
    """ Test cases for pokerchips"""
    
    def testPreflop1(self):
        """ Tests preflop"""
        players = [Player("Andrew", 100), Player("Brett", 100), Player("Cindy", 100), Player("Deandra", 100), Player("Egbert", 100)]
        correctPlayers = [Player("Andrew", 100), Player("Brett", 99, 1), Player("Cindy", 98, 2), Player("Deandra", 100), Player("Egbert", 100)]
        correctPots = [Pot(3, [correctPlayers[1], correctPlayers[2]])]

        # Initialize a table with these players, a small blind of 1 and a big blind of 2
        table = Table(players, smallBlind = 1, bigBlind = 2)

        # Do a preflop runthrough
        Round = 1
        print("\nRound", Round)

        table.getPreFlopRotation(Round)
        table.preflop()
        self.assertEqual(table.Players, correctPlayers)
        self.assertEqual(table.pots, correctPots)

    def testPreflop2(self):
        """ Tests preflop"""
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
        Round = 1
        print("\nRound", Round)

        table.getPreFlopRotation(Round)
        table.preflop()
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
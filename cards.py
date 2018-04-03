# Huey Fields
# 3/16/18

import random
import functools

debug = True

# TODO: Change card class to an Enum to prevent nonsensical cards
class Card:
    """ Creates a representation of a standard playing card
    using an integer to represent its value and a string to 
    represent its suit. Values past 10 represent the face cards,
    and 14 represents an Ace"""
    def __init__(self, value = 0, suit = ""):
        self.value = value
        self.suit = suit

    def __repr__(self):
        """ Returns a string describing the given card"""
        if self.value <= 10:
            return str(self.value) + " of " + self.suit + "s"
        else:
            vals = ["Jack", "Queen", "King", "Ace"]
            return vals[self.value - 11] + " of " + self.suit + "s"

    def __eq__(self, other):
        """ Returns whether two cards are equal"""
        return self.value == other.value and self.suit == other.suit

    def __gt__(self, other):
        """ Returns whether a card is considered "greater" than
        another card. Cards with higher values are considered greater.
        For cards of the same value, we arbitrarily determine Spades as
        the "greatest" suit, followed by Diamonds, Hearts, and Clubs"""
        # Create list of possible suits for reference later
        suits = ["Club", "Heart", "Diamond", "Spade"]

        if self.value != other.value:
            return self.value > other.value
        else:
            return suits.index(self.suit) > suits.index(other.suit)

    def __lt__(self, other):
        """ Returns whether a card is considered "less" than
        another card. Cards with lower values are considered less.
        For cards of the same value, we arbitrarily determine Spades as
        the "greatest" suit, followed by Diamonds, Hearts, and Clubs """
        # Create list of possible suits for reference later
        suits = ["Club", "Heart", "Diamond", "Spade"]

        if self.value != other.value:
            return self.value < other.value
        else:
            return suits.index(self.suit) < suits.index(other.suit)


class Deck:
    """ Creates a representation of a deck of 52 standard
    playing cards with two lists to represent dealt and 
    undealt cards. Contains methods for randomly drawing cards"""
    def __init__(self):
        # Create lists of all possible cards to iterate through and add to the deck
        # TODO: Just use an iterator from the Enum when card is changed to an Enum
        suits = ["Club", "Heart", "Diamond", "Spade"]
        
        self.undealt = []
        self.dealt = []

        for value in range(2, 15):
            for suit in suits:
                card = Card(value, suit)
                self.undealt += [card]

    def __repr__(self):
        """ Returns a string representing the given deck"""
        s = "Dealt cards: \n"
        for card in self.dealt:
            s += str(card) + "\n"
        s += "\nUndealt cards: \n"
        for card in self.undealt:
            s += str(card) + "\n"
        return s

    def reset(self):
        """ Resets a deck as if no cards had been dealt."""
        self.undealt += self.dealt
        self.dealt = []

    def deal(self, numCards):
        """ Returns an array of numCards cards randomly selected
        from the undealt cards of the deck. Cards dealt here will
        be moved to the dealt list. Function will print a message
        and return an empty list if there are not enough cards left
        in undealt to return """
        if numCards > len(self.undealt):
            print("Not enough cards left undealt in this deck.\n")
            return[]
        else:
            # Generate a random sample of numCards cards from undealt (without replacement)
            randCards = random.sample(self.undealt, numCards)

            # Remove dealt cards from undealt and add them to dealt
            for card in randCards:
                self.undealt.remove(card)
                self.dealt += [card]
            
            return randCards

    def burn(self):
        """ Randomly burns a card, moving it from dealt to undealt 
        without doing anything else with it."""
        randCard = random.choice(self.undealt)
        self.undealt.remove(randCard)
        self.dealt += [randCard]

class Hand:
    """ Uses a list of Cards to represent a poker hand with the
    designated number of cards. Contains methods for determining
    the value of any 5-card hand that can be made from the hand's Cards
    and some amount of Cards on the board."""
    def __init__(self, numCards = 0, cards = []):      
        self.cards = cards
        self.numCards = numCards

    def __repr__(self):
        """ Returns a string representing the given hand"""
        s = ""
        for card in self.cards:
            s += str(card) + "\n"
        return s

    def fillHand(self, deck):
        """ Fills a hand with numCards cards from the given Deck"""
        self.cards = deck.deal(self.numCards)

    def findPair(self, board):
        """ Returns all five card hands that can be made from the 
        hand and the board containing one pair. Will not run if there
        are not enough cards in the hand and the board to make 5"""
        hands = []
        usedValues = []
        allCards = self.cards + board

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from least to greatest
        allCards.sort()

        # For each card in allCards, check if it has a pair
        for card in allCards:
            if not card.value in usedValues:
                # If so, add a 5-card hand containing that pair and the highest cards after it to hands
                if countByValue(allCards, card.value) == 2:
                    pair = list(filter(lambda x: x.value == card.value, allCards))
                    filtCards = list(filter(lambda x: x.value != card.value, allCards))
                    filtCards.reverse()
                    hands += [pair + filtCards[0:3]]
                    usedValues += [card.value]

        return hands

def countByValue(cards, value):
    """ Returns a count of how many time a certain value appears in
    a list of Cards"""
    count = 0
    for card in cards:
        if card.value == value:
            count += 1
    return count

def main():
    return 0

def pairTest():
    d = Deck()
    board = d.deal(5)
    print(board)
    h = Hand(2)
    h.fillHand(d)
    print(h.cards)
    return h.findPair(board)

if __name__ == "__main__" and debug == False:
    main()
# Huey Fields
# 3/16/18

# TODO: Change card class to an Enum to prevent nonsensical cards
class Card:
    """ Creates a representation of a standard playing card
    using strings to represent its value and suit"""
    def __init__(self, value = "", suit = ""):
        self.value = value
        self.suit = suit

    def __repr__(self):
        """ Returns a string describing the given card"""
        return self.value + " of " + self.suit


class Deck:
    """ Creates a representation of a deck of 52 standard
    playing cards with two lists to represent dealt and 
    undealt cards. Contains methods for randomly drawing cards"""
    def __init__(self):
        # Create lists of all possible cards to iterate through and add to the deck
        # TODO: Just use an iterator from the Enum when card is changed to an Enum
        suits = ["Clubs", "Hearts", "Diamonds", "Spades"]
        values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", 
                    "Jack", "Queen", "King", "Ace"]
        
        self.undealt = []
        self.dealt = []

        for suit in suits:
            for value in values:
                card = Card(value, suit)
                self.undealt += [card]
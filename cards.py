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

    def boardCombine(self, deck, boardNum):
        """ Returns a list of cards from the hand and with boardNum
        cards from the deck"""
        return self.cards + deck.deal(boardNum)
    

class HandHelper:
    """ HandHelper contains methods for finding the best possible 5-card
    poker hand that can be made out of an arbitrary number of cards, as 
    well as for comparing different 5-card hands. """

    suits = ["Club", "Heart", "Diamond", "Spade"]
    hands = ["Pair", "TwoPair", "ThreeOfAKind", "Straight", "Flush", "FullHouse", "FourOfAKind", "StraightFlush"]    

    @staticmethod
    def findPair(allCards):
        """ Returns best five card hand that can be made from the 
        given cards containing one pair. If there are no such hands, 
        will return None. Will not run if there are not enough cards 
        in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # For each card in allCards, check if it has a pair
        for card in allCards:
            # If so, return a 5-card hand containing that pair and the highest cards after it
            if countByValue(allCards, card.value) == 2:
                pair = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                return pair + filtCards[0:3]
        return None

    @staticmethod
    def findTwoPair(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing two pairs. If there are no such
        hands, will return None. Will not run if there are not enough 
        cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # For each card in allCards, check if it has a pair
        for card in allCards:
            if countByValue(allCards, card.value) == 2:
                pair1 = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                # If so, check the rest of the cards to see if there is another pair
                for filtCard in filtCards:
                    # Return a 5-card hand containing the pairs and the highest card after it
                    if countByValue(filtCards, filtCard.value) == 2:
                        pair2 = list(filter(lambda x: x.value == filtCard.value, filtCards))
                        filtCards = list(filter(lambda x: x.value != filtCard.value, filtCards))
                        return pair1 + pair2 + filtCards[0:1]
        return None

    @staticmethod
    def findThreeOfAKind(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a three of a kind. If there are 
        no such hands, will return None. Will not run if there are 
        not enough cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # For each card in allCards, check if there are three of that card in allCards
        for card in allCards:
            # If so, return a 5-card hand containing that three of a kind and the highest cards after it
            if countByValue(allCards, card.value) == 3:
                three = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                return three + filtCards[0:2]
        return None

    @staticmethod
    def findStraight(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a straight. If there are 
        no such hands, will return None. Will not run if there are 
        not enough cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # Initialize variables for keeping track of a possible straight
        lastCard = allCards[0]
        straight = [lastCard]

        # Iterate through the cards, keeping track of how many cards are in numerical order
        for card in allCards[1:]:
            # If the next card is in numerical order, continue building the straight
            if card.value == lastCard.value - 1:
                straight += [card]
                lastCard = card

            # If the next card has the same value, skip it and continue to the next card
            elif card.value == lastCard.value:
                continue

            # Otherwise, reset the straight and continue to the next card
            else:
                straight = [card]
                lastCard = card
                continue

            # As soon as we make a full straight, return it
            if len(straight) == 5:
                return straight
       
        # If there is an Ace in allCards, check for a "baby straight", where Ace is low
        if allCards[0].value == 14:
            # Rearrange allCards so that the first Ace is at the end
            allCards = allCards[1:] + allCards[:1]

            # Iterate through the cards, keeping track of how many cards are in numerical order
            for card in allCards[1:]:
                # If the next card is in numerical order, continue building the straight
                if card.value == lastCard.value - 1:
                    straight += [card]
                    lastCard = card

                # If the next card has the same value, skip it and continue to the next card
                elif card.value == lastCard.value:
                    continue

                # Otherwise, reset the straight and continue to the next card
                else:
                    straight = [card]
                    lastCard = card
                    continue

                # As soon as we make a full straight, return it
                if len(straight) == 5:
                    return straight

        return None

    # TODO: Make sure that the flush returned is the highest possible flush
    @staticmethod
    def findFlush(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a flush. If there are 
        no such hands, will return None. Will not run if there are 
        not enough cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # Filter allCards by suit, and return the first hand we find with 5 of the same suit
        for suit in HandHelper.suits:
            filtCards = list(filter(lambda x: x.suit == suit, allCards))
            if len(filtCards) >= 5:
                return filtCards[0:5]

        return None

    @staticmethod
    def findFullHouse(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a full house. If there are no such
        hands, will return None. Will not run if there are not enough 
        cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # For each card in allCards, check if it has a three of a kind
        for card in allCards:
            if countByValue(allCards, card.value) == 3:
                three = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                # If so, check the rest of the cards to see if there is a pair to complete the full house
                for filtCard in filtCards:
                    # Return a 5-card hand containing the pairs and the highest card after it
                    if countByValue(filtCards, filtCard.value) == 2:
                        pair = list(filter(lambda x: x.value == filtCard.value, filtCards))
                        filtCards = list(filter(lambda x: x.value != filtCard.value, filtCards))
                        return three + pair
        return None

    @staticmethod
    def findFourOfAKind(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a four of a kind. If there are 
        no such hands, will return None. Will not run if there are 
        not enough cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # For each card in allCards, check if there are four of that card in allCards
        for card in allCards:
            # If so, return a 5-card hand containing that four of a kind and the highest card after it
            if countByValue(allCards, card.value) == 4:
                four = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                return four + filtCards[0:1]
        return None

    # TODO: Finish writing findStraightFlush
    @staticmethod
    def findStraightFlush(allCards):
        """ Returns best five card hand that can be made from the 
        hand and the board containing a straight flush. If there are 
        no such hands, will return None. Will not run if there are 
        not enough cards in the hand and the board to make 5"""

        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # Filter allCards by suit, and return the first hand we find with 5 of the same suit
        for suit in HandHelper.suits:
            filtCards = list(filter(lambda x: x.suit == suit, allCards))
            if len(filtCards) >= 5:
                return filtCards[0:5]

        return None


def main():
    x = fullHouseTest()

    while (x == None):
        x = fullHouseTest()

    return x
    
def countByValue(cards, value):
    """ Returns a count of how many time a certain value appears in
    a list of Cards"""
    count = 0
    for card in cards:
        if card.value == value:
            count += 1
    return count

def pairTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findPair(cards)

def twoPairTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findTwoPair(cards)

def threeOfAKindTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findThreeOfAKind(cards)

def straightTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findStraight(cards)

def flushTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findFlush(cards)

def fullHouseTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findFullHouse(cards)

def fourOfAKindTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findFourOfAKind(cards)

def straightFlushTest():
    d = Deck()
    h = Hand(2)
    h.fillHand(d)
    cards = h.boardCombine(d, 5)
    print(cards)
    return HandHelper.findStraightFlush(cards)

if __name__ == "__main__" and debug == False:
    main()
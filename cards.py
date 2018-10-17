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
        """ Returns whether two cards are equal. Cards must have the
        same value and suit to be considered equal"""
        return self.value == other.value and self.suit == other.suit

    def eqVal(self, other):
        """ Returns whether two cards have equal value"""
        return self.value == other.value

    def __gt__(self, other):
        """ Returns whether a card is considered "greater" than
        another card. Cards with higher values are considered greater."""
        return self.value > other.value

    def __lt__(self, other):
        """ Returns whether a card is considered "less" than
        another card. Cards with lower values are considered less."""
        return self.value < other.value


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
    def __init__(self, numCards = 0, cards = [], faceUp = False):      
        self.cards = cards
        self.numCards = numCards
        self.faceUp = faceUp

    def __repr__(self):
        """ Returns a string representing the given hand"""
        s = ""
        for card in self.cards:
            s += str(card) + "\n"
        return s

    def flip(self):
        """ Flips the value of faceUp"""
        self.faceUp = not self.faceUp

    def equal(self, other, board):
        """ Checks to see if two hands are of equal value (i.e. can make
        the same value 5-card hand), given a board of community cards."""
        # Find the best 5-card hands that can be made by each Hand and the board
        bestHand1 = HandHelper.findBestHand(self.cards + board)
        bestHand2 = HandHelper.findBestHand(other.cards + board)

        # If the types of the best hands are different, return False
        if bestHand1[1] != bestHand2[1]:
            return False
        
        # If the types are the same, compare each of the cards in the best hands
        for i in range(5):
            # If any cards have different values, return False
            if bestHand1[0][i] != bestHand2[0][i]:
                return False

        return True

    def greater(self, other, board):
        """ Checks to see if a Hand is of greater value (i.e. can make
        a better 5-card hand), than another Hand given a board of 
        community cards."""
        # Find the best 5-card hands that can be made by each Hand and the board
        bestHand1 = HandHelper.findBestHand(self.cards + board)
        bestHand2 = HandHelper.findBestHand(other.cards + board)

        # If the types of the best hands are different, return whether bestHand1 is the more valuable type
        if bestHand1[1] != bestHand2[1]:
            return HandHelper.types.index(bestHand1[1]) > HandHelper.types.index(bestHand2[1])
        
        # If the types are the same, compare each of the cards in the best hands
        for i in range(5):
            # If any cards have different values, return whether bestHand1 has the higher value card
            if bestHand1[0][i] != bestHand2[0][i]:
                return bestHand1[0][i] > bestHand2[0][i]

        return True

    def less(self, other, board):
        """ Checks to see if a Hand is of greater value (i.e. can make
        a better 5-card hand), than another Hand given a board of 
        community cards."""
        # Find the best 5-card hands that can be made by each Hand and the board
        bestHand1 = HandHelper.findBestHand(self.cards + board)
        bestHand2 = HandHelper.findBestHand(other.cards + board)

        # If the types of the best hands are different, return whether bestHand1 is the less valuable type
        if bestHand1[1] != bestHand2[1]:
            return HandHelper.types.index(bestHand1[1]) < HandHelper.types.index(bestHand2[1])
        
        # If the types are the same, compare each of the cards in the best hands
        for i in range(5):
            # If any cards have different values, return whether bestHand1 has the lower value card
            if bestHand1[0][i] != bestHand2[0][i]:
                return bestHand1[0][i] < bestHand2[0][i]

        return True

    def fillHand(self, deck):
        """ Fills a Hand with numCards cards from the given Deck and returns this Hand"""
        self.cards = deck.deal(self.numCards)
        return self

    def boardCombine(self, deck, boardNum):
        """ Returns a list of cards from the hand and with boardNum
        cards from the deck"""
        return self.cards + deck.deal(boardNum)
    

class HandHelper:
    """ HandHelper contains methods for finding the best possible 5-card
    poker hand that can be made out of an arbitrary number of cards, as 
    well as for comparing different 5-card hands. """

    suits = ["Club", "Heart", "Diamond", "Spade"]
    types = ["High", "Pair", "TwoPair", "ThreeOfAKind", "Straight", "Flush", "FullHouse", "FourOfAKind", "StraightFlush"] 

    @staticmethod
    def findRepeats(numRepeats, allCards):
        """ Helper method for finding hands with repeated values 
        in a list of cards. Assuming the cards are sorted from
        greatest to least, returns the best five card hand containing
        the given number of repeats, or None if there aren't any."""
        
        # For each card in allCards, check if it has numRepeats repeats
        for card in allCards:
            # If so, return a 5-card hand containing those repeats and the highest cards after it
            if countByValue(allCards, card.value) == numRepeats:
                repeats = list(filter(lambda x: x.value == card.value, allCards))
                filtCards = list(filter(lambda x: x.value != card.value, allCards))
                return repeats + filtCards[0:(5 - numRepeats)]
        return None

    @staticmethod
    def findFlushes(allCards):
        """ Helper method for finding flushes and straight flushes.
        Returns a list of ordered (greatest to least) flushes that 
        can be made from every suit out of the cards in allCards."""
        flushes = []
        
        # Filter allCards by suit, and add all hands we find with 5 of the same suit
        for suit in HandHelper.suits:
            filtCards = list(filter(lambda x: x.suit == suit, allCards))
            filtLen = len(filtCards)

            # If there are enough cards in filtCards to make a flush, add any ordered flushes that can be made
            if filtLen >= 5:
                for i in range(filtLen - 5):
                    flushes += [filtCards[i:5 + i]]          

        return flushes

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

        return HandHelper.findRepeats(2, allCards)

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

        return HandHelper.findRepeats(3, allCards)

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

        # Find all the flushes we can make from allCards
        flushes = HandHelper.findFlushes(allCards)

        # If no flushes can be made, return None
        if flushes == []:
            return None
        
        # Return the highest flush in flushes
        else:
            highVals = list(map(lambda x: x[0], flushes))
            return flushes[highVals.index(max(highVals))]

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

        return HandHelper.findRepeats(4, allCards)

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

        # Find all the flushes we can make from allCards
        flushes = HandHelper.findFlushes(allCards)

        # If no flushes can be made, return None
        if flushes == []:
            return None
        
        else:
            # Find all flushes that are also straights
            straightFlushes = []
            for flush in flushes:
                straightFlush = HandHelper.findStraight(flush)
                if straightFlush != None:
                    straightFlushes += [straightFlush]

            # If no straight flushes can be made, return None
            if straightFlushes == []:
                return None

            else:
                # Return the highest value straight flush
                highVals = list(map(lambda x: x[0], straightFlushes))
                return straightFlushes[highVals.index(max(highVals))]

    # TODO: Current implementation repeats some operations for finding certain hands that have already been done to check better hands.
    @staticmethod
    def findBestHand(allCards):
        """ Returns a tuple with the best five card hand that can be 
            made from the hand and the board, as well as a string
            representing the type of hand. Will not run if there are 
            not enough cards in the hand and the board to make 5"""
        
        # Exit if there are not enough cards
        if len(allCards) < 5:
            print("Not enough cards to make a poker hand.\n")
            return

        # Sort allCards from greatest to least
        allCards.sort(reverse = True)

        # Run all the checks on the cards from findStraightFlush down to findPair
        checks = [HandHelper.findPair, HandHelper.findTwoPair, HandHelper.findThreeOfAKind, HandHelper.findStraight, HandHelper.findFlush, 
            HandHelper.findFullHouse, HandHelper.findFourOfAKind, HandHelper.findStraightFlush]
        numChecks = len(checks)

        for i in range(numChecks):
            hand = checks[-i - 1](allCards)
            
            # If we find a hand, return it and its type in a tuple
            if hand != None:
                return (hand, HandHelper.types[-i - 1])

        # If we don't have anything better than a high card, return the first 5 cards in allCards and its type ("high")
        return (allCards[0:5], HandHelper.types[0])

    @staticmethod
    def findWinner(hands, board):
        """ Returns the index of best hand out of a given array of hands,
        given the board. If there are multiple best hands, return an array
        of their indices."""

        winners = [0]

        for i in range(0, len(hands)):
            if hands[i].greater(hands[winners[-1]], board):
                winners = [i]
            elif hands[i].equal(hands[winners[-1]], board):
                winners += [i]

        return winners





def main():
    d = Deck()
    board = d.deal(5)
    print(board)
    h1 = Hand(2)
    h2 = Hand(2)
    h1.fillHand(d)
    h2.fillHand(d)
    print("Hand 1:")
    print(h1)
    print("Hand 2:")
    print(h2)
    print("Best Hand 1: ")
    print(HandHelper.findBestHand(h1.cards + board))
    print("Best Hand 2: ")
    print(HandHelper.findBestHand(h2.cards + board))
    return [h1.equal(h2, board), h1.greater(h2, board), h1.less(h2, board)]
    
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
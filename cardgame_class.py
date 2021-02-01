import random

CLUBS = "♣️"
DIAMONDS = "♦️"
HEARTS = "♥️"
SPADES = "♠️"

class Card:
    def __init__(self,val,suit):
        self.val = val
        self.suit = suit
        self.comparator = self.get_comparator()

    def __eq__(self, other):
        return self.val==other.val and self.suit==other.suit

    def __str__(self):
        return "{}{}".format(self.val,self.suit)

    def show(self):
        print(self)

    def get_comparator(self):
        if(self.suit==CLUBS): suit_add = 0
        elif(self.suit==DIAMONDS): suit_add = 13
        elif(self.suit==HEARTS): suit_add = 26
        elif(self.suit==SPADES): suit_add = 39
        value = self.val
        if(value=='A'): value = 13
        elif(value=='K'): value = 12
        elif(value=='Q'): value = 11
        elif(value=='J'): value = 10
        else: value -= 1
        return value+suit_add

class Deck:
    def __init__(self):
        self.cards = []
        self.build()

    def build(self):
        for suit in (CLUBS,DIAMONDS,HEARTS,SPADES):
            for val in range(1,14):
                if(val==1): val = 'A'
                elif(val==11): val = 'J'
                elif(val==12): val = 'Q'
                elif(val==13): val = 'K'
                self.cards.append(Card(val,suit))

    def rebuild(self):
        self.cards.clear()
        self.build()

    def show(self):
        print("Deck:")
        for card in self.cards:
            card.show()
        print("num cards={}".format(len(self.cards)))

    def shuffle(self):
        for i in range(len(self.cards)-1,0,-1): # 51 to 1, excl 0 for full set
            r = random.randint(0,i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawTop(self):
        return self.cards.pop()

    def sort(self):
        self.cards.sort(key=lambda card:card.comparator)


class Player:
    def __init__(self,name):
        self.name = name
        self.hand = []

    def draw(self,deck):
        card = deck.drawTop()
        self.insert(card)

    def insert(self,card):
        if(card in self.hand):
            print("card already in hand")
        else: self.hand.append(card)

    def sort(self):
        self.hand.sort(key=lambda card:card.comparator)

    def play(self,card):
        if(card not in self.hand):
            print("card not in hand")
        else:
            self.hand.remove(card)
            print("{} played".format(card))

    def showHand(self):
        print("{}'s hand:".format(self.name))
        for card in self.hand:
            card.show()
        print()

    def hand_to_string(self):
        string = ", ".join(str(x) for x in self.hand)
        print(string)
        return string

    def clear_hand(self):
        self.hand.clear()


def main():
    player = Player("r")
    player.insert(Card(2,SPADES))
    player.insert(Card('K',HEARTS))
    player.showHand()
    player.clear_hand()
    player.showHand()
    player.insert(Card('Q',CLUBS))
    player.showHand()


if __name__ == '__main__':
    main()

import cardgame_class as game

NOTRUMP = "NT"

class BridgePlayer(game.Player):
    def __init__(self,name):
        super().__init__(name)
        self.tricksWon = 0
        self.team = None

    def showHandSuit(self,suit):
        print("{}'s hand ({} only):".format(self.name,suit))
        for card in (c for c in self.hand if c.suit==suit):
            card.show()

    def getPlayable(self,suit,trump_suit,trump_broken):
        if(suit==None): # starting player
            if(trump_broken):
                print("starting player can play any card incl. trump (trump broken)")
                return self.hand
            else:
                print("starting player can play any card excl. trump (trump not broken)")
                set = []
                for card in (c for c in self.hand if c.suit != trump_suit):
                    set.append(card)
                return set
        set = []
        for card in (c for c in self.hand if c.suit==suit):
            set.append(card)
        if not set: # set is empty
            print("no cards of given suit left, can play any card incl. trump")
            return self.hand
        return set

    # only used at start of game after cards are dealt
    # also sorts the hand to aid with counting
    def getPoints(self):
        self.sort()
        points = 0
        countSame = 0
        currSuit = None
        for card in self.hand:
            if(card.suit==currSuit):
                countSame += 1
            else:
                countSame = 1
                currSuit = card.suit
            if(countSame > 4):
                points += 1

            if(card.val=='A'):
                points += 4
            elif(card.val=='K'):
                points += 3
            elif(card.val=='Q'):
                points += 2
            elif(card.val=='J'):
                points += 1

        return points

class Team:
    def __init__(self,members,tricksNeeded,name):
        self.name = name
        self.members = members
        self.tricksWon = 0
        self.tricksNeeded = tricksNeeded

    def print(self):
        print("team name: {}".format(self.name))
        print("players are: {}".format(self.members))
        print("tricks needed = {}".format(self.tricksNeeded))

def strToCard(str):
    str = str.upper()
    if(len(str)==2):
        try:
            value = int(str[0])
        except:
            value = str[0]

        if(str[1]=="C"):
            suit = game.CLUBS
        elif(str[1]=="D"):
            suit = game.DIAMONDS
        elif(str[1]=="H"):
            suit = game.HEARTS
        elif(str[1]=="S"):
            suit = game.SPADES

        return game.Card(value,suit)

    elif(len(str)==3):
        if(str[2]=="C"):
            suit = game.CLUBS
        elif(str[2]=="D"):
            suit = game.DIAMONDS
        elif(str[2]=="H"):
            suit = game.HEARTS
        elif(str[2]=="S"):
            suit = game.SPADES
        return game.Card(10,suit)
    else:
        print("invalid card input")

# list is sorted
def printCardsFromList(list):
    currSuit = None
    for card in list:
        if(card.suit!=currSuit):
            if(currSuit!=None):
                print()
            currSuit = card.suit
            if(currSuit==game.CLUBS): # extra tab for formatting
                print("{}".format(currSuit), end = "\t\t")
            else: print("{}".format(currSuit), end = "\t")
        print(card.val, end=" ")
    print("\n")

def main():
    player = BridgePlayer("test");
    player.insert(game.Card(2,game.SPADES))
    player.insert(game.Card(10,game.SPADES))
    player.insert(game.Card(3,game.SPADES))
    player.insert(game.Card(5,game.DIAMONDS))
    player.insert(game.Card('K',game.CLUBS))
    player.insert(game.Card('A',game.SPADES))
    player.insert(game.Card(6,game.HEARTS))

    player.sort()
    printCardsFromList(player.hand)
    playable = player.getPlayable(game.SPADES,game.HEARTS,True)
    printCardsFromList(playable)
    team = Team(["a"],7,"noobs")
    team.print()
    print(team.get_team_members_str())

if __name__ == '__main__':
    main()

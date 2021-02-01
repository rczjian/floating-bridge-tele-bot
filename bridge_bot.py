import json
import requests
import time
import urllib # so that special characters can be parsed properly
import chatbot_io as bot
import cardgame_class as cards
import bridge_classes as bridge
import random

# suit emojis
CLUBS = "♣️"
DIAMONDS = "♦️"
HEARTS = "♥️"
SPADES = "♠️"
NOTRUMP = "NT"

class BridgeBotPlayer(bridge.BridgePlayer):
    def __init__(self,name,username,user_id):
        super().__init__(name)
        self.username = username
        self.user_id = user_id

def register_players(chat_id):
    num_players = 0
    id_list = []
    player_list = []
    while num_players < 4:
        data = bot.listen()
        if data["text"] == "/register":
            if data["sender_id"] not in id_list:
                player = BridgeBotPlayer(data["sender_name"],data["sender_username"],data["sender_id"])
                id_list.append(data["sender_id"])
                player_list.append(player)
                num_players += 1
                bot.send_message(
                    "{} registered!\nregistered players:\n{}".format(
                        player.name,
                        "\n".join(player.name for player in player_list)
                    ),
                    chat_id
                )
            else:
                print("player already registered")
        else:
            print("not /register command")
            continue
    return player_list

# for testing
def register_players_test(chat_id):
    num_players = 0
    id_list = []
    player_list = []
    while num_players < 4:
        data = bot.listen()
        if data["text"] == "/register":
            if data["sender_id"] not in id_list:
                player = BridgeBotPlayer(data["sender_name"],data["sender_username"],data["sender_id"])
                id_list.append(data["sender_id"])
                player_list.append(player)
                num_players += 1
                bot.send_message(
                    "{} registered!\nregistered players:\n{}".format(
                        player.name,
                        "\n".join(player.name for player in player_list)
                    ),
                    chat_id
                )
            else:
                print("player already registered")
        else:
            print("not /register command")
            continue
    return player_list

# create indivdual keyboard based on player's hand
def hand_to_json_keyboard(player):
    # parse player.hand as list of lists
    cards_sorted = []
    suit_list = []
    currSuit = None
    for card in player.hand:
        if(card.suit!=currSuit):
            if suit_list: # is not empty
                cards_sorted.append(suit_list)
            currSuit = card.suit
            suit_list = []
        suit_list.append(str(card))
    cards_sorted.append(suit_list) # append the last list
    keyboard_js = bot.create_keyboard(
        cards_sorted,
        selective=True
    )
    return keyboard_js

def send_cards(player,chat_id):
    # send cards as keyboard
    bot.send_message(
        "@{}, check your custom keyboard for your cards".format(player.username),
        chat_id,
        hand_to_json_keyboard(player)
    )

def send_cards_to_all(players,chat_id):
    for i in range(4):
        send_cards(players[i],chat_id)
        # time.sleep(8) # for testing

def listen_for_user(player):
    while True:
        data = bot.listen_for_callback()
        if data["sender_id"] == player.user_id:
            break
        else:
            print("callback not from specified player")
            continue
    callback_data = data["callback_data"]
    message_id = data["message_id"]
    return callback_data, message_id

def get_current_bid(min_bids):
    if min_bids[0]==1:
        return "no bid"
    else:
        suit_idx = 4 # no trump if no change after loop
        num = min_bids[0]-1
        for i in range(1,5):
            if min_bids[i] < min_bids[i-1]:
                suit_idx = i-1
                num = min_bids[i]
                break
    if suit_idx == 0:
        suit = CLUBS
    elif suit_idx == 1:
        suit = DIAMONDS
    elif suit_idx == 2:
        suit = HEARTS
    elif suit_idx == 3:
        suit = SPADES
    elif suit_idx == 4:
        suit = NOTRUMP
    return "{}{}".format(num,suit)

def update_min_bids(min_bids,bid):
    bid_num = int(bid[0])
    bid_suit = bid[1:] # emoji is two characters
    if bid_suit==CLUBS:
        bid_suit_idx = 0
    elif bid_suit==DIAMONDS:
        bid_suit_idx = 1
    elif bid_suit==HEARTS:
        bid_suit_idx = 2
    elif bid_suit==SPADES:
        bid_suit_idx = 3
    elif bid_suit==NOTRUMP:
        bid_suit_idx = 4
    for i in range(5):
        if i<=bid_suit_idx:
            min_bids[i] = bid_num+1
        else:
            min_bids[i] = bid_num

def create_bidding_keyboard(min_bids):
    line1 = []
    for i in range(5):
        if i==0: suit = CLUBS
        elif i==1: suit = DIAMONDS
        elif i==2: suit = HEARTS
        elif i==3: suit = SPADES
        elif i==4: suit = NOTRUMP
        if min_bids[i]<8:
            line1.append("{}{}".format(min_bids[i],suit))
    line2 = ["pass"]
    if min_bids[4]<7:
        line2.append("other")
    keyboard = bot.create_inline_keyboard([line1,line2])
    return keyboard

def show_all_bid_options(chat_id,message_id,min_bids):
    all_bids = []
    list = []
    j = min_bids[0]
    for i in range(5):
        if i==0: suit = CLUBS
        elif i==1: suit = DIAMONDS
        elif i==2: suit = HEARTS
        elif i==3: suit = SPADES
        elif i==4: suit = NOTRUMP
        if i!=0 and min_bids[i] < min_bids[i-1]:
            list = []
            j = min_bids[i]
        list.append("{}{}".format(min_bids[i],suit))
    all_bids.append(list)
    j += 1
    while j < 8:
        list = []
        for i in range(5):
            if i==0: suit = CLUBS
            elif i==1: suit = DIAMONDS
            elif i==2: suit = HEARTS
            elif i==3: suit = SPADES
            elif i==4: suit = NOTRUMP
            list.append("{}{}".format(j,suit))
        all_bids.append(list)
        j += 1
    all_bids.append(["pass"])
    keyboard = bot.create_inline_keyboard(all_bids)
    bot.edit_message_markup(chat_id, message_id, keyboard)

def update_bid_message(main_line, log, chat_id, message_id, min_bids):
    new_text = main_line+"\n\n"+log
    bot.edit_message(new_text, chat_id, message_id, create_bidding_keyboard(min_bids))

def create_partner_keyboard():
    return bot.create_inline_keyboard([
        ["J{}".format(CLUBS),"Q{}".format(CLUBS),"K{}".format(CLUBS),"A{}".format(CLUBS)],
        ["J{}".format(DIAMONDS),"Q{}".format(DIAMONDS),"K{}".format(DIAMONDS),"A{}".format(DIAMONDS)],
        ["J{}".format(HEARTS),"Q{}".format(HEARTS),"K{}".format(HEARTS),"A{}".format(HEARTS)],
        ["J{}".format(SPADES),"Q{}".format(SPADES),"K{}".format(SPADES),"A{}".format(SPADES)],
        ["other"]
    ])

def show_all_partner_options(chat_id,message_id):
    all_cards = []
    for i in range(4):
        if i==0: suit = CLUBS
        elif i==1: suit = DIAMONDS
        elif i==2: suit = HEARTS
        elif i==3: suit = SPADES
        list = []
        for j in range(2,7):
            list.append("{}{}".format(j,suit))
        all_cards.append(list)
        list = []
        for j in range(7,11):
            list.append("{}{}".format(j,suit))
        all_cards.append(list)
        all_cards.append(["J{}".format(suit),"Q{}".format(suit),"K{}".format(suit),"A{}".format(suit)])
    keyboard = bot.create_inline_keyboard(all_cards)
    bot.edit_message_markup(chat_id, message_id, keyboard)

def get_card_from_str(string):
    try:
        value = int(string[0])
        if value==1:
            return cards.Card(10,string[2:])
    except:
        value = string[0]
    return cards.Card(value,string[1:])

def findPartner(card,players):
    if(card in players[0].hand): return 0
    elif(card in players[1].hand): return 1
    elif(card in players[2].hand): return 2
    else: return 3

def createTeams(bid_winner,partner,bid):
    team1_members = []
    team1_members.append(bid_winner)
    if(bid_winner!=partner):
        team1_members.append(partner)
    team2_members = [i for i in range(0,4) if i not in team1_members]

    team1_needs = bid+6
    team2_needs = 14-team1_needs

    team1 = bridge.Team(team1_members,team1_needs,"Team 1")
    team2 = bridge.Team(team2_members,team2_needs,"Team 2")

    return [team1,team2]

def allocateTeams(players,teams):
    for member in teams[0].members:
        players[member].team = 0
    for member in teams[1].members:
        players[member].team = 1

def isStrongerCard(played_card,winningCard,trump_suit):
    if(played_card.suit==winningCard.suit):
        return (played_card.comparator>winningCard.comparator)
    else:
        if(played_card.suit==trump_suit):
            return True
        else: # no trump or non-trump
            return False

def get_team_members_str(team,players):
    member_list = team.members
    if len(member_list)==1:
        string = players[member_list[0]].name
    elif len(member_list)==2:
        string = players[member_list[0]].name+" and "+players[member_list[1]].name
    else:
        string = players[member_list[0]].name+", "+players[member_list[1]].name+" and "+players[member_list[2]].name
    return string

def main():
    bot.clear_past_updates()

    while True:
        data = bot.listen()
        if(data["text"]=="/start"):
            print("game starting...")
            break
        else:
            print("invalid command, trying again")

    # lock in the group chat / cannot take indiv chat
    # updates from other chats will mess with the program
    chat_id = data["chat_id"]
    group_name = data["group_name"]

    # welcome + registration
    bot.send_message(
        "hi {}, welcome to bridge! those who are playing, please /register".format(group_name),
        chat_id
    )
    use_same_players = False
    while True:
        if not use_same_players:
            players = register_players(chat_id)
            # players = register_players_test(chat_id) # for testing purposes

        # start game: create deck and deal
        bot.send_message(
            "shuffling and dealing cards...",
            chat_id,
            bot.create_remove_keyboard()
        )
        deck = cards.Deck()
        while True:
            deck.rebuild()
            print("shuffling cards...")
            deck.shuffle()

            for i in range(4):
                players[i].clear_hand()
                players[i].tricksWon = 0

            # deal cards
            print("dealing cards...")
            for i in range(0,13):
                for j in range(0,4):
                    players[j].draw(deck)

            # sort cards and check if need to wash
            print("checking for wash...")
            need_wash = False
            for i in range(4):
                points = players[i].getPoints() # conveniently sorts the cards too
                if(points<4):
                    print("{} wash. reshuffling...".format(players[i].name))
                    bot.send_message(
                        "{} needs to wash! reshuffling and dealing ...".format(players[i].name),
                        chat_id
                    )
                    need_wash = True
                    break
            if need_wash:
                continue
            print("no need to wash")
            break

        send_cards_to_all(players,chat_id)

        # bidding using inline keyboard
        # so players can still see their cards in the reply keyboard
        skip_to_end = False
        currBidder = random.randint(0,3)
        print("player {} starts bid".format(currBidder+1))
        log = "bid log:\n"
        min_bids = [1,1,1,1,1]
                 # [C,D,H,S,NT]
        pass_count = 0
        bot.send_message(
            "{} (randomly chosen) starts bid\ncurrent bid: no bid".format(players[currBidder].name),
            chat_id,
            create_bidding_keyboard(min_bids)
        )

        while True:
            bid, message_id = listen_for_user(players[currBidder])

            if bid == "pass":
                pass_count += 1
            elif bid == "other":
                show_all_bid_options(chat_id,message_id,min_bids)
                print("showing all bid options")
                continue
            else:
                print("updating minimum bids")
                update_min_bids(min_bids,bid)
                pass_count = 0

            # update log
            log += "{}: {}\n".format(players[currBidder].name,bid)
            print("player {}'s turn ends".format(currBidder+1))
            currBidder = (currBidder+1)%4

            if min_bids[4] == 8: # bidder bid 7NT (no more possible bids)
                bid_winner = (currBidder+3)%4
                print("7NT - player {} wins bid".format(bid_winner+1))
                break
            elif pass_count > 2:
                if min_bids[0]==1: # >=3 passes with no bid
                    if pass_count > 3: # 4 passes with no bid
                        print("everybody passed without bidding (game ends)")
                        bot.edit_message(
                            "{}\neveryone passed; game ends.\n\nplay /again? or /exit".format(log),
                            chat_id,
                            message_id
                        )
                        skip_to_end = True
                        break
                else: # 3 passes with existing bid
                    bid_winner = currBidder
                    print("player {} wins bid".format(bid_winner+1))
                    break

            # continue with these if didnt terminate from above
            main_line = "{}, your turn to bid".format(players[currBidder].name)
            update_bid_message(main_line, log, chat_id, message_id, min_bids)
            # 7nt scenario

        if not skip_to_end:
            winning_bid = get_current_bid(min_bids)
            trump_suit = winning_bid[1:]
            bot.edit_message(
                "{}\n{} wins the bid ({})!".format(log,players[bid_winner].name,winning_bid),
                chat_id,
                message_id
            )
            bot.send_message(
                "{}, choose your partner".format(players[bid_winner].name),
                chat_id,
                create_partner_keyboard()
            )

            while True:
                partner_card_str, message_id = listen_for_user(players[bid_winner]) # new message_id
                if partner_card_str == "other":
                    show_all_partner_options(chat_id,message_id)
                    print("showing all possible cards")
                    continue
                else:
                    break
            bot.edit_message(
                "{} chose {} as his/her partner".format(players[bid_winner].name,partner_card_str),
                chat_id,
                message_id
            )

            partner_card = get_card_from_str(partner_card_str)
            print("partner:"+str(partner_card))
            partner = findPartner(partner_card,players)
            print("partner is player {}\n".format(partner+1))
            teams = createTeams(bid_winner,partner,int(winning_bid[0]))
            allocateTeams(players,teams)

            # to check
            for i in range(2):
                print("team {} needs:".format(i+1))
                print(str(teams[i].tricksNeeded))
                print("members:")
                for m in teams[i].members:
                    print(m+1)

            # determine who starts
            if(trump_suit==NOTRUMP):
                start = bid_winner
            else:
                start = (bid_winner+1)%4

            # for testing, to see all cards in terminal
            for i in range(4):
                print("player {}".format(i+1))
                bridge.printCardsFromList(players[i].hand)

            # actual gameplay
            info_string = "****** GAME INFO ******\nwinning bid: {} ({}-{})\n{}'s partner: {}".format(
                winning_bid,
                teams[players[bid_winner].team].tricksNeeded,
                14-teams[players[bid_winner].team].tricksNeeded,
                players[bid_winner].name,
                partner_card_str
            )
            trump_broken = False
            for i in range(13):
                log = "trick {}'s log:\n".format(i+1)
                suit = None
                print("player {} starts".format(start+1))
                bot.send_message(
                    "{}, play a card".format(players[start].name),
                    chat_id
                )
                for j in range(4):
                    curr_player_idx = (start+j)%4
                    next_player_idx = (start+j+1)%4
                    curr_player = players[curr_player_idx]
                    next_player = players[next_player_idx]
                    playable = curr_player.getPlayable(suit,trump_suit,trump_broken)
                    while True:
                        while True:
                            data = bot.listen()
                            if data["sender_id"]==curr_player.user_id:
                                played_card_str = data["text"]
                                break
                            else:
                                print("not that player's turn, listening again")
                        played_card = get_card_from_str(played_card_str)
                        if played_card in playable:
                            break
                        else:
                            bot.send_message(
                                "you cant play that card (wrong suit / trump not broken / dont have that card)",
                                chat_id
                            )
                    curr_player.play(played_card)
                    if(played_card.suit==trump_suit):
                        trump_broken = True

                    if(j==0):
                        suit = played_card.suit
                        winningCard = played_card
                        trick_winner = curr_player
                        trick_winner_idx = curr_player_idx
                    else:
                        if(isStrongerCard(played_card,winningCard,trump_suit)):
                            winningCard = played_card
                            trick_winner = curr_player
                            trick_winner_idx = curr_player_idx

                    log += "{}: {}\n".format(curr_player.name,played_card_str)

                    if j<3:
                        bot.send_message(
                            "updated @{}'s cards\n\n{}\n{}, your turn".format(curr_player.username,log,next_player.name),
                            chat_id,
                            hand_to_json_keyboard(curr_player)
                        )
                    else: # last player of the trick
                        bot.send_message(
                            "updated @{}'s cards\n\n{}".format(curr_player.username,log),
                            chat_id,
                            hand_to_json_keyboard(curr_player)
                        )
                trick_winner.tricksWon+=1
                teams[trick_winner.team].tricksWon+=1
                scores_str = "total tricks won:\n{}: {}\n{}: {}\n{}: {}\n{}: {}".format(
                    players[0].name, players[0].tricksWon,
                    players[1].name, players[1].tricksWon,
                    players[2].name, players[2].tricksWon,
                    players[3].name, players[3].tricksWon,
                )
                bot.send_message(
                    "{} wins this trick\n\n{}\n\n{}".format(trick_winner.name,scores_str,info_string),
                    chat_id
                )

                start = trick_winner_idx

                # check for winner
                if(teams[0].tricksWon==teams[0].tricksNeeded):
                    winningTeam = 0
                    losingTeam = 1
                    break
                elif(teams[1].tricksWon==teams[1].tricksNeeded):
                    winningTeam = 1
                    losingTeam = 0
                    break
                # else: pass

            if bid_winner == partner:
                partner_message = "{} called himself/herself. he/she ".format(players[bid_winner].name)
            else:
                partner_message = "{} was {}'s partner. they ".format(players[partner].name,players[bid_winner].name)

            other_team_message = get_team_members_str(teams[1],players)
            if winningTeam==0:
                team_message = "won!\n"
                other_team_message += " lost :/"
            else:
                team_message = "lost :/\n"
                other_team_message += " won!"

            print("{} won!".format(teams[winningTeam].name))
            print("winning members: {}".format(get_team_members_str(teams[winningTeam],players)))

            replay_message = "play /again? or /exit"

            bot.send_message(
                "{}{}{}\n\nplay /again? or /exit".format(partner_message,team_message,other_team_message),
                chat_id
            )

        while True:
            data = bot.listen()
            if data["text"]=="/again":
                print("game starting...")
                break
            elif data["text"]=="/exit":
                print("exiting ...")
                bot.send_message(
                    "alright, thanks for playing. goodbye!",
                    chat_id,
                    bot.create_remove_keyboard()
                )
                return
            else:
                print("invalid command, trying again")

        bot.send_message("great! are the same players playing again?",
            chat_id,
            bot.create_inline_keyboard([["same","diff"]])
        )
        while True:
            data = bot.listen_for_callback()
            if data["callback_data"] == "same":
                use_same_players = True
                bot.edit_message("same players are playing again; no need to re-register",chat_id,data["message_id"])
                break
            elif data["callback_data"] == "diff":
                use_same_players = False
                bot.edit_message("different players are playing; new players, please /register",chat_id,data["message_id"])
                break
            else:
                print("unrecognised input, listening again")


if __name__ == '__main__':
    main()

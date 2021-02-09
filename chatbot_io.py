import json
import requests
import time
import urllib # so that special characters can be parsed properly
import os

TOKEN = os.environ["TOKEN"]
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

# get content from url as string, in utf8
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# parse content from url as python dict (based on json object)
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

# if there are pre-existing updates, will return immediately
# if there are no updates, will keep connection open for min{timeout},~60 seconds
# during this time, if a new update comes in, will return immediately
# if not, returns the empty json object
def get_updates(timeout=100,offset=None):
    url = URL + "getUpdates?timeout={}".format(timeout)
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

# return type int
def get_last_update_id(updates):
    return updates["result"][-1]["update_id"]

# return type int
def get_first_update_id(updates):
    return updates["result"][0]["update_id"]

def clear_update(update_id):
    url = URL + "getUpdates?offset={}".format(update_id+1)
    get_url(url)
    print("Update {} (and any updates prior) cleared".format(update_id))

def clear_past_updates():
    print("clearing past updates...")
    updates = get_updates(timeout=0)
    if len(updates["result"]) > 0:
        last_update_id = get_last_update_id(updates)
        clear_update(last_update_id)
    else:
        print("nothing to clear!")

# keep listening for updates until at least one is received
# returns the data for the first of all updates
# ignores the rest of the updates (if any)
def listen():
    while True:
        print("listening for updates...")
        updates = get_updates()
        # bot will only register updates for bot commands or replies
        numUpdates = len(updates["result"])
        if numUpdates > 0:
            if numUpdates > 1:
                print("only reading first update, ignoring the rest")
            data = parse_update(updates["result"][0]) # parse only the first update
            last_update_id = get_last_update_id(updates)
            print("received update, stopped listening")
            clear_update(last_update_id) # clears ALL updates prior
            break
        else:
            print("no updates received, looping in 0.5 seconds...")
        time.sleep(0.5) # wait 0.5 seconds before looping
    return data

# get data from one update
def parse_update(update):
    sender_name = update["message"]["from"]["first_name"]
    sender_username = update["message"]["from"]["username"]
    sender_id = update["message"]["from"]["id"]
    chat_id = update["message"]["chat"]["id"]
    chat_type = update["message"]["chat"]["type"] # private or group
    text = update["message"]["text"]
    # name change / group creation counts as an update but with no text, so might have error
    data = {
        "sender_name":sender_name,
        "sender_username":sender_username,
        "sender_id":sender_id,
        "chat_id":chat_id,
        "chat_type":chat_type,
        "text":text
    }
    if chat_type == "group":
        data["group_name"] = update["message"]["chat"]["title"]
    return data

# work on this next
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    if(reply_markup!=None):
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)
    print("message '{}' sent to chat_id {} with keyboard:\n\t{}".format(text, chat_id, reply_markup))

# takes a list of elements (not a list of lists)
# creates simple keyboard with one element per line
def create_simple_keyboard(list):
    listOfList = []
    for x in list:
        listOfList.append([str(x)])
    reply_markup = {
        "keyboard": listOfList,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    js = json.dumps(reply_markup)
    return js

# takes a list of lists
# each sublist is one row
def create_keyboard(list,selective=False):
    reply_markup = {
        "keyboard": list,
        "resize_keyboard": True,
        "one_time_keyboard": False, # changing to False to test iOS
        "selective": selective # selective is bugged for tele for mac
    }
    js = json.dumps(reply_markup)
    return js

def create_remove_keyboard():
    reply_markup = {
        "remove_keyboard": True,
        "selective": False
    }
    js = json.dumps(reply_markup)
    return js

# takes list of list of string
def create_inline_keyboard(list):
    # convert list of list of string to list of list of buttons
    new_list = []
    for sublist in list:
        new_sublist = []
        for string in sublist:
            button = {
                "text":string,
                "callback_data":string
            }
            new_sublist.append(button)
        new_list.append(new_sublist)
    reply_markup = {
        "inline_keyboard": new_list
    }
    js = json.dumps(reply_markup)
    return js

def listen_for_callback():
    while True:
        print("listening for callback updates...")
        updates = get_updates()
        # bot will only register updates for bot commands or replies
        numUpdates = len(updates["result"])
        if numUpdates > 0:
            if numUpdates > 1:
                print("only reading first update, ignoring the rest")
            data = parse_callback_update(updates["result"][0]) # parse only the first update
            last_update_id = get_last_update_id(updates)
            print("received update, stopped listening")
            clear_update(last_update_id) # clears ALL updates prior
            break
        else:
            print("no updates received, looping in 0.5 seconds...")
        time.sleep(0.5) # wait 0.5 seconds before looping
    return data

# get data from one update
def parse_callback_update(update):
    sender_name = update["callback_query"]["from"]["first_name"]
    sender_username = update["callback_query"]["from"]["username"]
    sender_id = update["callback_query"]["from"]["id"]
    chat_id = update["callback_query"]["message"]["chat"]["id"]
    message_id = update["callback_query"]["message"]["message_id"]
    callback_data = update["callback_query"]["data"]

    data = {
        "sender_name":sender_name,
        "sender_username":sender_username,
        "sender_id":sender_id,
        "chat_id":chat_id,
        "message_id":message_id,
        "callback_data":callback_data
    }
    return data

def edit_message(new_text, chat_id, message_id, reply_markup=None):
    new_text = urllib.parse.quote_plus(new_text)
    url = URL + "editMessageText?text={}&chat_id={}&message_id={}".format(new_text, chat_id, message_id)
    if(reply_markup!=None):
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)
    print("edited message_id {} in chat_id {} to '{}' with keyboard:\n\t{}".format(message_id, chat_id, new_text, reply_markup))

def edit_message_markup(chat_id, message_id, reply_markup):
    url = URL + "editMessageReplyMarkup?chat_id={}&message_id={}&reply_markup={}".format(chat_id, message_id, reply_markup)
    get_url(url)
    print("changed markup of message_id {} in chat_id {} to:\n\t{}".format(message_id, chat_id, reply_markup))

def main():
    data = {
        "sender_name": "name",
        "sender_username": "asdfghjkl",
        "sender_id": 1234567,
        "chat_id": 1234567,
        "chat_type": "private",
        "text": "this is text"
    }
    chat_id = data["chat_id"]
    group_chat_id = -987654321
    username = data["sender_username"]
    send_message("play /again? or /exit", group_chat_id)

if __name__ == '__main__':
    main()

from telegram.ext import Updater, CommandHandler
import logging
import urllib.request
import json

url = 'https://api.chaos-darmstadt.de'
response = urllib.request.urlopen(url)
print(response.read())

#chats = {}
status_w17 = False


def autoupdate(bot, job):
    global status_w17
    curr_response = urllib.request.urlopen(url)
    curr_status = str(curr_response.read())
    if curr_status == "b'1'":
        status_new = True
    elif curr_status == "b'0'":
        status_new = False
    else:
        status_new = None
    print(status_w17, status_new)
    if status_new != status_w17:
        for i, chat in enumerate(chats.keys()):
            if chats[chat]:
                if curr_status == "b'1'":
                    bot.send_message(chat_id=chat, text='W17 besetzt')
                elif curr_status == "b'0'":
                    bot.send_message(chat_id=chat, text='W17 leer')
                else:
                    bot.send_message(chat_id=chat, text='sth changed')
        status_w17 = status_new


def status(bot, update):
    curr_response = urllib.request.urlopen(url)
    curr_status = str(curr_response.read())
    if curr_status == "b'1'":
        bot.send_message(chat_id=update.message.chat_id, text='W17 besetzt')
    elif curr_status == "b'0'":
        bot.send_message(chat_id=update.message.chat_id, text='W17 leer')
    else:
        bot.send_message(chat_id=update.message.chat_id, text='sth changed')


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text='/start zeigt diese Liste\n'
                          '/join setzt dich auf die Update-Liste\n'
                          '/leave nimmt dich von der Update-Liste\n'
                          '/status gibt den aktuellen Status')
    print(chats)


def join_updater(bot, update):
    global chats
    chats[update.message.chat_id] = True
    bot.send_message(chat_id=update.message.chat_id,
                     text='Du bekommst nun Updates, sobald sich etwas ändert')
    print(chats)
    data["chats"] = chats
    with open("chats.json", "w") as jsonFile:
        json.dump(data, jsonFile)


def leave_updater(bot, update):
    global chats
    chats[update.message.chat_id] = False
    bot.send_message(chat_id=update.message.chat_id,
                     text='Du bekommst nun keine Updates mehr')
    print(chats)
    data["chats"] = chats
    with open("chats.json", "w") as jsonFile:
        json.dump(data, jsonFile)



with open('conf.json') as f:
    config = json.load(f)
with open("chats.json", "r") as jsonFile:
    data = json.load(jsonFile)
chats = data["chats"]

#debug
chats[252269446] = True
data["chats"] = chats
with open("chats.json", "w") as jsonFile:
    json.dump(data, jsonFile)

updater = Updater(token=config["token"])
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
start_handler = CommandHandler('start', start)
status_handler = CommandHandler('status', status)
join_handler = CommandHandler('join', join_updater)
leave_handler = CommandHandler('leave', leave_updater)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(status_handler)
dispatcher.add_handler(join_handler)
dispatcher.add_handler(leave_handler)

updater.start_polling()
j = updater.job_queue
autoup = j.run_repeating(autoupdate, interval=60, first=0)

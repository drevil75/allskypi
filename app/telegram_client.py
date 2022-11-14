# install 
# pip3 install python-telegram-bot --upgrade

import telegram

def sendTxtMsg(token, to_list, msg):
	bot = telegram.Bot(token=token)
	for to in to_list:
		bot.send_message(chat_id=to, text=msg)
	print(bot)



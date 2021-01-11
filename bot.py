import logging
import os

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date

from credentials import TOKEN, URL
from claim import *

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

global chats
chats = {}

# Ordinary commands to appear in telegram
def start(update, context):
    global chats

    chat_id = update.message.chat.id
    logging.info(chat_id)
    chats[chat_id] = []

    general_message(update)

def add(update, context):
    global chats

    args = context.args
    chat_id = update.message.chat.id

    if len(args) < 2:
        send_reply(update, "Please create new claim in the form of <NAME> <AMT>")
    else:
        last_index = len(args)
        if(is_number(args[last_index - 1]) and float(args[last_index - 1]) > 0):
            claim_name = " ".join(args[:last_index - 1])
            claim_amt = float(args[last_index - 1])
            claim = Claim(claim_name, claim_amt, date.today())
            chats[chat_id].append(claim)
            send_reply(update, "Ok, claim amount of *$" + get_currency(claim_amt) + "* for *" + claim_name + "* has been created")
        else:
            send_reply(update, "Please enter a valid amount more than $0")

def get(update, context):
    chat_id = update.message.chat.id

    msg = ""
    index = 1

    for c in chats[chat_id]:
        msg += str(index) + ". " + c.name + " (" + c.date.strftime("%d/%m/%Y") + ") - $" + get_currency(c.amount) + "\n"
        index += 1 

    header_msg = "You have " + str(len(chats[chat_id])) + " open claim(s). \n\n"        
    send_reply(update, header_msg + msg)
    
def close(update, context):
    global chats
    chat_id = update.message.chat.id

    args = context.args
    if len(args) != 1:
        send_reply(update, "Please enter the index of the claim you wish to close")
    else:
        index = int(args[0])
        if valid_range(index, chats[chat_id]):
            c = chats[chat_id].pop(index - 1)
            send_reply(update, "You have closed a claim of *$" + get_currency(c.amount) + "*")
            get(update, context)
        else:
            send_reply(update, "Invalid claim index. Please check available claims using /list")

def restart(update, context):
    global chats
    chat_id = update.message.chat.id
    
    chats[chat_id] = []

    send_reply(update, "I have cleared all claims")


# Helper methods    
def send_reply(update, msg):
    update.message.reply_text(msg, parse_mode= 'Markdown')

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def valid_range(value, lst):
    length = len(lst)
    if value >= 1 and value <= length:
        return True
    else:
        return False

def get_currency(amt):
    return "{0:,.2f}".format(amt)

# Others
def general_message(update):
    send_reply(update, 'Hello, welcome to the Claims Tracker Bot! \nYou can use me to keep track of any claims you may have~ \n\nStart by making a new claim with /add')

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    command = 0

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add, pass_args=True))
    dp.add_handler(CommandHandler("list", get))
    dp.add_handler(CommandHandler("close", close, pass_args=True))
    dp.add_handler(CommandHandler("restart", restart))

    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, handle_commands))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot (HEROKU)
    # updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    # updater.bot.set_webhook(URL + TOKEN)
    # updater.idle()

    # Start the Bot (LOCALHOST)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main() 
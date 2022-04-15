from telegram.ext import *
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv('BOT_API_KEY')

# import Constans as keys
import Responses as Resp

print("Bot is starting...")

def start_command(update, context):
    update.message.reply_text("Welcome to the IA Project Bot!\n")


def help_command(update, context):
    update.message.reply_text("Ask Google!\n")

def handle_message(update, context):
    user_message = str(update.message.text).lower()
    response = Resp.sample_responses(user_message)
    update.message.reply_text(response)

def errors(update, context):
    """Log Errors caused by Updates.""" 
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
  updater = Updater(API_KEY, use_context=True)
  dp = updater.dispatcher

  dp.add_handler(CommandHandler("start", start_command))
  dp.add_handler(CommandHandler("help", help_command))

  dp.add_handler(MessageHandler(Filters.text, handle_message))
  dp.add_error_handler(errors)

  updater.start_polling()
  updater.idle()

main()
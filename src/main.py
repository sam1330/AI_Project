import Constans as keys
from telegram.ext import *
import Responses as R

print("Bot is starting...")

def start_command(update, context):
    update.message.reply_text("Welcome to the IA Project Bot!\n")


def help_command(update, context):
    update.message.reply_text("Ask Google!\n")

def handle_message(update, context):
    user_message = str(update.message.text).lower()
    response = R.sample_responses(user_message)
    update.message.reply_text(response)

def errors(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
  updater = Updater(keys.BOT_API_KEY, use_context=True)
  dp = updater.dispatcher

  dp.add_handler(CommandHandler("start", start_command))
  dp.add_handler(CommandHandler("help", help_command))

  dp.add_handler(MessageHandler(Filters.text, handle_message))
  dp.add_error_handler(errors)

  updater.start_polling()
  updater.idle()

main()
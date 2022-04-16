from telegram.ext import *
import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

import Constans as keys
import Responses as Resp

print("Bot is starting...")

def start_command(update, context):
    update.message.reply_text("Welcome to the IA Project Bot!\n")


def help_command(update, context):
    update.message.reply_text("Ask Google!\n")

def handle_message(update, context):
    user_message = str(update.message.text)
    user_message = tokenize(user_message)
    
    X = bag_of_words(user_message, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                # response = Resp.sample_responses(user_message)
                update.message.reply_text(random.choice(intent['responses']))

def errors(update, context):
    """Log Errors caused by Updates.""" 
    logger.warning('Update "%s" caused error "%s"', update, context.error)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

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
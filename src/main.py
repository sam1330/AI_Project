from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, Update,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, CallbackContext,
    ConversationHandler, MessageHandler,
    Filters, Updater, CallbackQueryHandler
)

# Define Options
CHOOSING, CLASS_STATE, PAY_STATE, CHECKOUT, \
    INVENTORY, ADD_PRODUCTS, SHOW_STOCKS, LOCATION, STATE_REQUEST = range(9)


from telegram.ext import *
import random
import json
import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

from DBRequests import *
import Constans as keys
import Responses as Resp
import handlers

print("Bot is starting...")

isInventory = False

def start_command(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    bot.send_message(chat_id=chat_id, text="Hola, soy un bot de prueba")
    return CHOOSING


def help_command(update, context):
    update.message.reply_text("Ask Google!\n")

#esta funcion es para manejar los mensajes del cliente. implementa NLP y tiene una serie de respuestas entrenadas dependiendo lo que pida el cliente
def handle_message(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    user_message = update.message.text
    user_message = tokenize(user_message)
        
    X = bag_of_words(user_message, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.65:
        #ideas para el futuro
        # ya se mas o menos lo que hare, pues implementare respuestas personalizadas para las preguntas abiertas y para preguntas relacionadas con el inventario voy a hacer procesos para responder de manera certera.
        for intent in intents['intents']:
            if tag == intent["tag"]:
                if tag == "inventory" or tag == "orders":
                    if tag == "orders":
                        bot.send_message(chat_id=chat_id, text=random.choice(intent['responses']))
                        return STATE_REQUEST
                    
                    bot.send_message(chat_id=chat_id, text="Para acceder a los productos escriba tu nombre, email y telefono en ese orden y separado por comas (,)")

                    return INVENTORY

                bot.send_message(chat_id=chat_id, text=random.choice(intent['responses']))
    else:
        for intent in intents['intents']:
            if intent["tag"] == "noanswer":
                bot.send_message(chat_id=chat_id, text=random.choice(intent['responses']))

    return CHOOSING

#esta funcion muestra errores en consola
def errors(update, context):
    """Log Errors caused by Updates.""" 
    print('Update "{}" caused error "{}"'.format(update, context.error))
    # logger.warning('Update "%s" caused error "%s"', update, context.error)


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

#Esta parte trae los datos resultantes de haber entrenado el bot con el Json de entrenamiento 
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

# Aqui estamos inicialdo el bot de telegram pasandole las credenciales
updater = Updater(keys.BOT_API_KEY, use_context=True)
dp = updater.dispatcher

#Esta funcion es la principal. el punto de entrada del bot. asi se setean los comandos y los mensajes y sus respectivos handlers
def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', handlers.start_command)],
        states={
            handlers.CHOOSING: [
                MessageHandler(
                    Filters.text, handle_message
                )
            ],
            handlers.INVENTORY: [
                MessageHandler(
                    Filters.all, handlers.handleMesages
                )
            ],
            handlers.CLASS_STATE: [
                CallbackQueryHandler(handlers.classer)
            ],
            handlers.SHOW_STOCKS: [
                CallbackQueryHandler(handlers.showProducts)
            ],
            handlers.ADD_PRODUCTS: [
                CallbackQueryHandler(handlers.addProductToCart)
            ],
            handlers.CHECKOUT: [
                CallbackQueryHandler(handlers.checkOut)
            ],
            handlers.PAY_STATE: [
                CallbackQueryHandler(handlers.pay)
            ],
            handlers.LOCATION: [
                MessageHandler(Filters.all, handlers.location)
            ],
            handlers.STATE_REQUEST: [
                MessageHandler(Filters.all, handlers.stateRequest)
            ],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
        allow_reentry=True
    )
    dp.add_handler(conv_handler)
    updater.start_polling(2)
    updater.idle()

if __name__ == '__main__':
    main()
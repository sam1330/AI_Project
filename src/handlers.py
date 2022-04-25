from numpy import product
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

from ProductRequests import *

CART = [] 

# Define Options
CHOOSING, CLASS_STATE, SME_DETAILS, CHOOSE_PREF, \
    SME_CAT, ADD_PRODUCTS, SHOW_STOCKS, POST_VIEW_PRODUCTS = range(8)

#este es el punto de entrada de la aplicación
def start_command(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    bot.send_message(chat_id=chat_id, text="Hola, para comenzar escribe tu nombre, email y telefono en ese orden y separado por comas (,)")
    return CHOOSING

# Esta funcion es para manejar los mensajes del cliente pero aun le falta pulirse
def handleMesages(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    data = update.message.text.split(',')
    if len(data) < 3 or len(data) > 3:
        bot.send_message(
            chat_id=chat_id,
            text="Invalid entry, please make sure to input the details "
            "as requested in the instructions"
        )
        bot.send_message(
            chat_id=chat_id,
            text="Cliente registrado, Escribe /start, Para reiniciar conversacion"
        )
        return ConversationHandler.END

    product = ProductRequests()
    newCustomer =  product.addClient(data[0], data[1], data[2])
    print(newCustomer[0][0])

    context.user_data["user-id"] = int(newCustomer[0][0])
    context.user_data["user-name"] = data[0]
    context.user_data['user-data'] = newCustomer

    reply_keyboard = [
        [
            InlineKeyboardButton(
                text="Comprar producto",
                callback_data="buy"
            ),
            InlineKeyboardButton(
                text="Ver estado de pedido",
                callback_data="state"
            )
        ]
    ]

    markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text="Perfecto, {} iniciemos.\n que desea hacer?".format(data[0]),
        reply_markup=markup
    )
    return CLASS_STATE

# Esta funcion es para ver las categorías disponibles para agregar productos
def classer(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    name = context.user_data["user-name"]

    categories = [  
        [
            InlineKeyboardButton(
                text="Alimentos",
                callback_data="alimentos"
            ),
            InlineKeyboardButton(
                text="Tecnología",
                callback_data="electronics"
            )
        ],
        [
            InlineKeyboardButton(
                text="Food/Kitchen Ware",
                callback_data="Food/Kitchen Ware"
            ),
            InlineKeyboardButton(
                text="ArtnDesign",
                callback_data="ArtnDesign"
            )
        ]
    ]
    bot.send_message(
        chat_id=chat_id,
        text="Aquí hay una lista de categorías, selecciona una para ver los productos",
        reply_markup=InlineKeyboardMarkup(categories)
    )
    return SHOW_STOCKS

# Esta funcion se explica sola. es para cancelar el proceso de compra
def cancel(update: Update, context: CallbackContext) -> int: 
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

#Esta funcion lo que hace es mostrar la lista de productos dependiendo de la categoria seleccionada, trae un botón de agregar al carrito y un botón de regresar al menu de categorías

def showProduct(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data
    productsClass = ProductRequests()
    products = productsClass.getProductsByCategory(data)

    if len(products) <= 0:
        bot.send_message(
              chat_id=chat_id,
              text="'No hay productos de esta categoria aun"
        )
        button = [  
            [
                InlineKeyboardButton(
                    text="Volver",
                    callback_data="back"
                ),
            ],
        ]
        bot.send_message(
            chat_id=chat_id,
            text="Ir atrás?",
            reply_markup=InlineKeyboardMarkup(button)
        )
        return CLASS_STATE

    for product in products:
        button = [
              [
                
                  InlineKeyboardButton(
                      text="Agregar al carrito",
                      callback_data=product[0]
                  )
              ],
        ]
        bot.send_photo(
          chat_id=chat_id,
          photo=product[5],
          caption=f"{str(product[1])} \nDescription: {str(product[2])}\nPrice:{str(product[4])}",
          reply_markup=InlineKeyboardMarkup(button)
        )
    button = [
          [
            
              InlineKeyboardButton(
                  text="Volver",
                  callback_data="back"
              )
          ],
    ]
    bot.send_message(
      chat_id=chat_id,
      text="Ir atrás?",
      reply_markup=InlineKeyboardMarkup(button)
    )
    return ADD_PRODUCTS
    

def customerPref(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data
    print(data)

def postViewProduct(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data

# Esta funcion es para agregar productos al carrito
# Lo que hace es en un array temporal, almacena los productos que se van agregando para al final consultar la base de datos y hacer los calculos pertinentes para completar la compra
def addProductToCart(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data
    print(data)
    if data == "back":
        return CLASS_STATE
    CART.append(data)
    bot.send_message(
        chat_id=chat_id,
        text="Producto agregado al carrito"
    )
    return ADD_PRODUCTS
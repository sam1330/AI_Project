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
from geopy import distance

from DBRequests import *

# Variables de estado
CART = [] 
TOTAL = 0
CLIENT_LOCATION = ()
COMMERCE_LOCATION = (19.4904660, -70.7179249)

# Define Options
CHOOSING, CLASS_STATE, PAY_STATE, CHECKOUT, \
    INVENTORY, ADD_PRODUCTS, SHOW_STOCKS, LOCATION = range(8)

#este es el punto de entrada de la aplicación
def start_command(update, context: CallbackContext) -> int:
    bot = context.bot
    chat_id = update.message.chat.id
    # bot.send_message(chat_id=chat_id, text="Hola, para comenzar escribe tu nombre, email y telefono en ese orden y separado por comas (,)")
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
        # bot.send_message(
        #     chat_id=chat_id,
        #     text="Cliente registrado, Escribe /start, Para reiniciar conversacion"
        # )
        return ConversationHandler.END

    product = DBRequests()
    newCustomer =  product.addClient(data[0], data[1], data[2])

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

    if len(CART) > 0:
        categories.append([
            InlineKeyboardButton(
                text="Check Out",
                callback_data="checkout"
            )
        ])

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
    
    if data == "checkout":
        # checkOut(update, context)
        return CHECKOUT
    else:
        productsClass = DBRequests()
        products = productsClass.getProductsByCategory(data)

        if len(products) <= 0:
            bot.send_message(
                chat_id=chat_id,
                text="No hay productos de esta categoria aun"
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
        text="Volver (Presione dos veces)",
        reply_markup=InlineKeyboardMarkup(button)
        )
        return ADD_PRODUCTS
    

def customerPref(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data

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

    if data == "back":
        return classer(update, context)
    CART.append(data)
    bot.send_message(
        chat_id=chat_id,
        text="Producto agregado al carrito"
    )
    return ADD_PRODUCTS

def checkOut(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id

    productClass = DBRequests()
    productsInCart = []
    global TOTAL
    TOTAL = 0

    for product in CART:
        currentProduct = productClass.getProductById(product)
        productsInCart.append(currentProduct[0])

        TOTAL += currentProduct[0][4]
        bot.send_message(
            chat_id=chat_id,
            text=f"{currentProduct[0][1]} \nDescription: {currentProduct[0][2]}\nPrice:{currentProduct[0][4]}"
        )

    buttons = [
        [
            InlineKeyboardButton(
                text="Pagar",
                callback_data="pay"
            )
        ],
        [
            InlineKeyboardButton(
                text="Volver (Pulse 2 veces)",
                callback_data="back"
            )
        ],
    ]
    bot.send_message(
        chat_id=chat_id,
        text=f"Total: {TOTAL}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PAY_STATE


def pay(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data

    global TOTAL

    if data == "pay":
        shippingPref(update, context)
        return LOCATION
    elif data == "back":
        return CLASS_STATE

    elif data == "effective":
        TOTAL = TOTAL - (TOTAL * 0.1)
        bot.send_message(
            chat_id=chat_id,
            text=f"Por pagar en efectivo, el TOTAL es: {TOTAL} \nGracias por su compra!"
        )
        return ConversationHandler.END
    
    # return LOCATION


def shippingPref(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id

    buttons = [
        [
            InlineKeyboardButton(
                text="Para Recoger",
                callback_data="take"
            )
        ],
        [
            InlineKeyboardButton(
                text="A Domicilio",
                callback_data="shipping"
            )
        ],
    ]
    bot.send_message(
        chat_id=chat_id,
        text="Por favor selecciona la opción de tu preferencia",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return LOCATION

def location(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    # data = update.callback_query.data

    if update.callback_query is not None:
        data = update.callback_query.data
        bot.send_message(
            chat_id=chat_id,
            text="Por favor envié su ubicación"
        )
    else:
        data = update.message.text

    if data == "take":
        bot.send_message(
            chat_id=chat_id,
            text="Gracias por su compra!"
        )
        return ConversationHandler.END
    elif data == "shipping":
        bot.send_message(
            chat_id=chat_id,
            text="Por favor envié su ubicación"
        )
        return LOCATION
    if update.message.location is None:
        bot.send_message(
            chat_id=chat_id,
            text="No has enviado tu ubicación, por favor enviala para seguir"
        )
        return LOCATION

    global CLIENT_LOCATION
    CLIENT_LOCATION = (update.message.location.latitude, update.message.location.longitude)

    print("Client: {}".format(CLIENT_LOCATION))
    print("Commerce: {}".format(COMMERCE_LOCATION))

    print("Distance: {}".format(distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km))

    if distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km >= 5 and distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km <= 10:
        bot.send_message(
            chat_id=chat_id,
            text="Se le asignara El costo de envió son 200 pesos."
        )
    
    elif distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km >= 10:
        bot.send_message(
            chat_id=chat_id,
            text="Lo siento pero no realizamos envió a mas de 10km, en cambio puede pasar a recoger su pedido en el local"
        )
        return CHECKOUT

    buttons = [
        [
            InlineKeyboardButton(
                text="Efectivo",
                callback_data="effective",
            )
        ],
        [
            InlineKeyboardButton(
                text="Tarjeta",
                callback_data="card",
            )
        ],
    ]
    bot.send_message(
        chat_id=chat_id,
        text="Como desea pagar?",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return PAY_STATE

    
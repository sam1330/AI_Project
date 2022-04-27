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
    INVENTORY, ADD_PRODUCTS, SHOW_STOCKS, LOCATION, STATE_REQUEST = range(9)

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
        ]
    ]

    markup = InlineKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text="Perfecto {}, continuemos.\n\n que desea hacer?".format(data[0]),
        reply_markup=markup
    )
    return CLASS_STATE

# Esta funcion es para ver las categorías disponibles para agregar productos
def classer(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data
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
        'Bye! I hope we can talk again some day.\n\nsi desea algo mas escriba /start',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

#Esta funcion lo que hace es mostrar la lista de productos dependiendo de la categoria seleccionada, trae un botón de agregar al carrito y un botón de regresar al menu de categorías

def showProducts(update, context):
    bot = context.bot
    chat_id = update.callback_query.message.chat.id
    data = update.callback_query.data
    
    if data == "checkout":
        checkOut(update, context)
        return PAY_STATE
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
            caption=f"{str(product[1])} \n\nDescripcion:\n{str(product[2])}\n\nPrecio:\n{str(product[4])}",
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
        text="Volver",
        reply_markup=InlineKeyboardMarkup(button)
        )
        return ADD_PRODUCTS
    
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

    print(context.user_data)
    # return LOCATION

    global CLIENT_LOCATION
    global TOTAL
    global CART
    #Aquí se obtiene el numero de la ultima factura y se le suma 1 para que sea la nueva factura 
    db = DBRequests()
    purchase_num = db.getLastPurchaseNumber() + 1

    if data == "pay":
        shippingPref(update, context)
        return LOCATION
    elif data == "back":
        return CLASS_STATE

    elif data == "cash":
        TOTAL = TOTAL - (TOTAL * 0.1)
        bot.send_message(
            chat_id=chat_id,
            text=f"Por pagar en efectivo se le aplica un 10% de descuento.\nEl TOTAL a pagar es: {TOTAL} \nGracias por su compra!\n\nSi desea algo mas escriba /start"
        )

        for product in CART:
            db.completePurchase(purchase_num, product, context.user_data["user-id"], TOTAL, "cash", 'procesado')

        CART = [] 
        TOTAL = 0
        CLIENT_LOCATION = ()
        return ConversationHandler.END
    elif data == "card":

        bot.send_message(
            chat_id=chat_id,
            text=f"El total a pagar es: {TOTAL} \n\nComo no podemos manejar Info sensible como tarjetas, hasta aquí llegamos \nSe le enviaran los detalles de la factura por el email dado. \n\nGracias por su compra!!\n\n si desea algo mas escriba /start"
        )

        for product in CART:
            db.completePurchase(purchase_num, product, context.user_data["user-id"], TOTAL, "card", 'procesado')

        CART = [] 
        TOTAL = 0
        CLIENT_LOCATION = ()
        return ConversationHandler.END
    
    return PAY_STATE


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

    global CLIENT_LOCATION
    global TOTAL
    global CART

    bot = context.bot
    chat_id = update.message.chat.id

    print("callbak: {}".format(type(update.callback_query)))
    print("message: {}".format(type(update.message)))
    # return LOCATION
    if update.callback_query is None:
        data = update.message.text

    else:
        data = update.callback_query.data
        bot.send_message(
            chat_id=chat_id,
            text="Por favor envié su ubicación"
        )        

    print(data)
    if data == "take":
        CART = [] 
        TOTAL = 0
        CLIENT_LOCATION = ()
        bot.send_message(
            chat_id=chat_id,
            text="Gracias por su compra!"
        )
        return ConversationHandler.END
    elif data == "shipping":
        bot.send_message(
            chat_id=chat_id,
            text="Por favor envíe su ubicación"
        )
        return LOCATION
    if update.message.location is None:
        bot.send_message(
            chat_id=chat_id,
            text="No has enviado tu ubicación, por favor enviala para seguir"
        )
        return LOCATION

    CLIENT_LOCATION = (update.message.location.latitude, update.message.location.longitude)

    print("Client: {}".format(CLIENT_LOCATION))
    print("Commerce: {}".format(COMMERCE_LOCATION))

    print("Distance: {}".format(distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km))

    if distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km >= 5 and distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km <= 10:
        bot.send_message(
            chat_id=chat_id,
            text="Usted se encuentra a mas de 5 KM de distancia \nSe le agregara el costo de envió son 200 pesos."
        )
        TOTAL += 200
    
    elif distance.distance(COMMERCE_LOCATION, CLIENT_LOCATION).km >= 10:
        bot.send_message(
            chat_id=chat_id,
            text="Lo siento pero no realizamos envió a mas de 10km.\nEn cambio puede pasar a recoger su pedido en la tienda"
        )
        return CHECKOUT

    buttons = [
        [
            InlineKeyboardButton(
                text="Efectivo",
                callback_data="cash",
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


def stateRequest(update, context):
    bot = context.bot
    chat_id = update.message.chat.id
    data = update.message.text

    print(data)

    if data.isdigit():
        db = DBRequests()
        state = db.getOrderState(data)
        if state == "procesado":
            bot.send_message(
                chat_id=chat_id,
                text="La orden ya fue procesada, si fue seleccionada para envío, para mañana deberia estar en su domicilio"
            )
            return CHOOSING
        elif state == "pendiente":
            bot.send_message(
                chat_id=chat_id,
                text="La orden esta pendiente de entrega \nA mas tardar mañana se entrega su orden"
            )
            return CHOOSING
        elif state == "cancelado":
            bot.send_message(
                chat_id=chat_id,
                text="La orden fue cancelada"
            )
            return CHOOSING
        else:
            bot.send_message(
                chat_id=chat_id,
                text="La orden dada no existe"
            )
            return CHOOSING
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Escribe un numero de orden valido (solo el numero)"
        )
        return STATE_REQUEST

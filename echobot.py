# import logging
import os
from functools import partial
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

from elasticpath import (get_client_credentials_token, get_product_by_id,
                         get_products)

_database = None


def start(update, context, client_id, client_secret):
    access_token = get_client_credentials_token(client_id, client_secret)
    products = get_products(access_token)

    keyboard = [
        [button]
        for button in [
            InlineKeyboardButton(p["attributes"]["name"], callback_data=p["id"]) for p in products
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Please choose your fish:", reply_markup=reply_markup)

    # return "HANDLE_DESCRIPTION"
    # return "ECHO"
    return "HANDLE_MENU"


def handle_menu(update, context, client_id, client_secret):
    query = update.callback_query
    query.answer()

    # Get the callback data from the button
    product_id = query.data

    access_token = get_client_credentials_token(client_id, client_secret)
    product = get_product_by_id(access_token, product_id)

    message_text = f"""\
    {product["attributes"]["name"]}

    {product["attributes"]["description"]}
    """

    query.edit_message_text(text=dedent(message_text))

    # access_token = get_client_credentials_token(client_id, client_secret)
    # products = get_products(access_token)

    # keyboard = [
    #     [
    #         InlineKeyboardButton(product["attributes"]["name"], callback_data=product["id"])
    #         for product in products
    #     ],
    #     [InlineKeyboardButton("Корзина", callback_data="Корзина")],
    # ]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    # update.callback_query.message.reply_text(
    #     "Товары магазина:",
    #     reply_markup=reply_markup,
    # )

    # bot.delete_message(
    #     chat_id=update.callback_query.message.chat.id,
    #     message_id=update.callback_query.message.message_id,
    # )

    return "HANDLE_MENU"


def echo(update, context):
    # users_reply = update.message.text
    if update.callback_query:
        # Handle the case of a callback query (button click)
        users_reply = update.callback_query.data
        update.callback_query.message.reply_text(users_reply)
    else:
        # Handle the case of a regular message
        users_reply = update.message.text
        update.message.reply_text(users_reply)

    return "ECHO"


def handle_users_reply(update, context, client_id, client_secret):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == "/start":
        user_state = "START"
    elif not db.get(chat_id):
        update.message.reply_text("Please, start bot with '/start' command.")
        return
    else:
        user_state = db.get(chat_id).decode("utf-8")

    states_functions = {
        "START": partial(start, client_id=client_id, client_secret=client_secret),
        "ECHO": echo,
        "HANDLE_MENU": partial(handle_menu, client_id=client_id, client_secret=client_secret),
        # "HANDLE_DESCRIPTION": partial(
        #     handle_description, client_id=client_id, client_secret=client_secret
        # ),
        # "HANDLE_CART": partial(handle_cart, client_id=client_id, client_secret=client_secret),
        # "WAITING_EMAIL": partial(handle_email, client_id=client_id, client_secret=client_secret),
    }
    state_handler = states_functions[user_state]
    # Если вы вдруг не заметите, что python-telegram-bot перехватывает ошибки.
    # Оставляю этот try...except, чтобы код не падал молча.
    # Этот фрагмент можно переписать.
    try:
        next_state = state_handler(update, context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)


def get_database_connection():
    global _database
    if _database is None:
        _database = redis.Redis(host="localhost", port=6379, db=0)
    return _database


if __name__ == "__main__":
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")

    elasticpath_client_id = os.getenv("ELASTICPATH_CLIENT_ID")
    elasticpath_client_secret = os.getenv("ELASTICPATH_CLIENT_SECRET")

    # customer_elasticpath_id = os.getenv("CUSTOMER_ELASTICPATH_ID")

    updater = Updater(telegram_token)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(
        CallbackQueryHandler(
            partial(
                handle_users_reply,
                client_id=elasticpath_client_id,
                client_secret=elasticpath_client_secret,
            )
        )
    )
    dispatcher.add_handler(
        MessageHandler(
            Filters.text,
            partial(
                handle_users_reply,
                client_id=elasticpath_client_id,
                client_secret=elasticpath_client_secret,
            ),
        )
    )
    dispatcher.add_handler(
        CommandHandler(
            "start",
            partial(
                handle_users_reply,
                client_id=elasticpath_client_id,
                client_secret=elasticpath_client_secret,
            ),
        )
    )

    updater.start_polling()
    updater.idle()

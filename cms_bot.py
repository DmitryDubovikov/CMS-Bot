# import logging
import os
from functools import partial
from textwrap import dedent

import redis
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

from elasticpath import (
    add_product_to_customer_cart,
    get_client_credentials_token,
    get_customer_cart_items,
    get_image_link_by_id,
    get_product_by_id,
    get_products,
    delete_customer_cart_item,
)

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

    update.message.reply_text("Let's start. Please choose your fish:", reply_markup=reply_markup)

    return "HANDLE_DESCRIPTION"


def handle_menu(update, context, client_id, client_secret):
    query = update.callback_query

    access_token = get_client_credentials_token(client_id, client_secret)
    products = get_products(access_token)

    keyboard = [
        [button]
        for button in [
            InlineKeyboardButton(p["attributes"]["name"], callback_data=p["id"]) for p in products
        ]
    ]
    keyboard.append([InlineKeyboardButton("My cart", callback_data="My cart")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text(
        "This is our menu. Please choose your fish:", reply_markup=reply_markup
    )

    query.delete_message(query.message.message_id)

    return "HANDLE_DESCRIPTION"


def handle_description(update, context, client_id, client_secret):
    query = update.callback_query
    chat_id = query.message.chat.id

    if query.data == "Back":
        handle_menu(update, context, client_id, client_secret)
        return "HANDLE_DESCRIPTION"

    if query.data == "My cart":
        handle_cart(update, context, client_id, client_secret)
        return "HANDLE_CART"

    product_id = query.data
    access_token = get_client_credentials_token(client_id, client_secret)

    if "unit" in query.data:
        amount, _, product_id = query.data.split()
        response = add_product_to_customer_cart(access_token, product_id, int(amount), chat_id)
        handle_cart(update, context, client_id, client_secret)
        return "HANDLE_CART"

    product = get_product_by_id(access_token, product_id)
    main_image_link = get_image_link_by_id(
        access_token, product["relationships"]["main_image"]["data"]["id"]
    )

    message_text = f"""\
    {product["attributes"]["name"]}

    {product["attributes"]["description"]}
    """

    keyboard = [
        [
            InlineKeyboardButton("1 unit", callback_data=f"1 unit {product_id}"),
            InlineKeyboardButton("5 unit", callback_data=f"5 unit {product_id}"),
            InlineKeyboardButton("10 unit", callback_data=f"10 unit {product_id}"),
        ],
        [InlineKeyboardButton("Back", callback_data="Back")],
        [InlineKeyboardButton("My cart", callback_data="My cart")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_photo(
        photo=main_image_link,
        caption=dedent(message_text),
        reply_markup=reply_markup,
    )

    query.delete_message(query.message.message_id)

    return "HANDLE_DESCRIPTION"


def handle_cart(update, context, client_id, client_secret):
    query = update.callback_query

    if query.data == "To menu":
        handle_menu(update, context, client_id, client_secret)
        return "HANDLE_DESCRIPTION"

    access_token = get_client_credentials_token(client_id, client_secret)
    chat_id = query.message.chat.id

    if "Remove" in query.data:
        _, item_id = query.data.split()
        response = delete_customer_cart_item(access_token, chat_id, item_id)

    cart_items = get_customer_cart_items(access_token, chat_id)

    keyboard = []
    message_text = """\
                Your cart:
                """

    if cart_items:
        for item in cart_items["data"]:
            message_text += f"""\

                {item["name"]}
                price: {item["unit_price"]["amount"]/100} {item["unit_price"]["currency"]}
                quantity: {item["quantity"]}
                value: {item["value"]["amount"]/100} {item["value"]["currency"]}

                """
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"Remove {item['name']}", callback_data=f"Remove {item['id']}"
                    )
                ]
            )
        keyboard.append([InlineKeyboardButton("To payment", callback_data="To payment")])

        total_sum_data = cart_items["meta"]["display_price"]["with_tax"]
        message_text += f"""Total: {total_sum_data["amount"]/100} {total_sum_data["currency"]}"""

    else:
        pass

    keyboard.append([InlineKeyboardButton("To menu", callback_data="To menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text(dedent(message_text), reply_markup=reply_markup)

    query.delete_message(query.message.message_id)

    return "HANDLE_CART"


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
        "HANDLE_MENU": partial(handle_menu, client_id=client_id, client_secret=client_secret),
        "HANDLE_DESCRIPTION": partial(
            handle_description, client_id=client_id, client_secret=client_secret
        ),
        "HANDLE_CART": partial(handle_cart, client_id=client_id, client_secret=client_secret),
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

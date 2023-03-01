import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

TOKEN = '6295400906:AAHdXGiKrIbEAiW4a5udRS6VJKaK-xuE7-k'


# Define the handler for the /start command
def start(update):
    # Create the keyboard and add the buttons
    keyboard = [[InlineKeyboardButton("Buy", callback_data='buy'),
                 InlineKeyboardButton("Send", callback_data='send')],
                [InlineKeyboardButton("Main menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the keyboard
    update.message.reply_text('Please choose an option:', reply_markup=reply_markup)


# Define the handler for the callback data from the buttons
def button(update, context):
    query = update.callback_query
    query.answer()

    # Determine which button was pressed and handle accordingly
    if query.data == 'buy':
        query.edit_message_text(text="You selected 'Buy'.")
    elif query.data == 'send':
        query.edit_message_text(text="You selected 'Send'.")
    elif query.data == 'main_menu':
        start(update, context)


# Define the handler for the 'back' command
def back(update, context):
    start(update, context)


# Create the Updater and add the handlers
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler('back', back))

# Start the bot
updater.start_polling()
updater.idle()
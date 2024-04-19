import logging
import dill as pkl
import os

from ollama import Client
ollama_client = Client(host='http://192.168.0.9:11434', timeout=5)

from helperfunctions import *
from pointsystem import *
# from instagramScraper import getFollowerHistory

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
hot = u'\U0001F525'
beer = u'\U0001F37A'
geld_smiley = u'\U0001F911'
smiley = u'\U0001F60A'
sad_smiley = u'\U0001F641'

SYSTEM_PROMPT = "You are Nico Haidinger and will provide an answer or follow-up to any questions provided. Try sounding like a Bank salesman who works for Sparkasse and wants to sell you financial products."

# Enable points
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def instagram_command(update, context):
    update.message.reply_text(f'Deprecated!')
    return


def zeawas(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Zeawas Buaschn!')


def register_command(update, context):
    user = update.message.from_user
    if user.username != "None":
        username = user.username
    else:
        username = user.name
    add_user(username, update.message.chat_id)
    PS = Point_System()
    PS.set(username, 100)
    update.message.reply_text('User added!')


def get_name_command(update, context):
    user = update.message.from_user
    if user.username != "None":
        username = user.username
    else:
        username = user.name
    update.message.reply_text("Du heißt: " + str(username))


def money_status(update, context):
    user = update.message.from_user
    if user.username != "None":
        username = user.username
    else:
        username = user.name
    PS = Point_System()
    update.message.reply_text("Du hast " + str(truncate(PS.get(username), 2)) + "€!")


def winter_cash_command(update, context):
    if len(context.args) != 0:
        games = context.args[0]
    else:
        games = 1
    user = update.message.from_user
    if user.username != "None":
        username = user.username
    else:
        username = user.name
    PS = Point_System()
    [money, order] = wintercash(PS.get(username), games, username)
    PS.set(username, money)
    update.message.reply_text("Du spielst " + str(games) + "-mal!\n\nSpielverlauf: " + order + "\nDu hast jetzt " + str(truncate(PS.get(username), 2)) + "€!")


def zukunft_command(update, context):
    update.message.reply_text('Beim Zukunftsfond der Sparkasse Oberösterreich hast du alles dabei!\n'
                              'Bitcoin, Blockchain, erneuerbare Energien und Wirecard Aktien!\n' + hot + hot + hot)


def bausparen_command(update, context):
    update.message.reply_text('Bausparen ab 30€, ist doch kein Problem oder?')


def reich_command(update, context):
    update.message.reply_text('Ich bin reich!')


def rolex_command(update, context):
    update.message.reply_text('Ich bin reich!')


def help_command(update, context):
    update.message.reply_text('I bims da Nico!')


def alkohol_command(update, context):
    update.message.reply_text('Ich bin alkoholiker!\n' + beer + beer + beer)


def wein_command(update, context):
    update.message.reply_text('Guada tropfn!!!!')


def deppad_command(update, context):
    update.message.reply_text('Hoit dei fressn!')


def floda_command(update, context):
    update.message.reply_text('''Test''')
    
    
def weron_command(update, context):
    context.bot.send_poll(update.effective_chat.id, "Heid wer on?", ["Yo", "Na", "Martin"], is_anonymous=False)


def aktien_command(update, context):
    update.message.reply_text('Komm in die gruppe und verdiene mehr als 50.000€ im monat' + geld_smiley +'\nPorschen,aktien,uhren,häusern\n050 688 699 20')

def ask_llama_command(update, context):
    if len(context.args) != 0:
      try:
        prompt = ' '.join(context.args)
        response = ollama_client.generate(model='llama3', 
                system=SYSTEM_PROMPT,
                prompt=prompt)
        update.message.reply_text(response["response"])
      except:
        update.message.reply_text("Bin ned online. " + sad_smiley)
    else:
        update.message.reply_text('Du musst mir a Frage stellen! ' + smiley)
      
def set_llama_command(update, context):
    if len(context.args) != 0:
        SYSTEM_PROMPT = ' '.join(context.args)
        update.message.reply_text("System prompt was set to: " + SYSTEM_PROMPT)
    else:
        update.message.reply_text('Give a system prompt!')

def logging(update, context):
    """Echo the user message."""
    #user = update.message.from_user
    if user.username != "None":
        username = user.username
    else:
        username = user.name
    message = update.message.text
    add_message(username, message, update.message.chat_id)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    token = os.getenv('BOT_TOKEN')
    if token is None:
        with open("token", 'r') as file:
            token = file.read()
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Llama handler
    dp.add_handler(CommandHandler("ask", ask_llama_command))
    dp.add_handler(CommandHandler("set_llama_system", set_llama_command))
    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("zeawas", zeawas))
    dp.add_handler(CommandHandler("instafollowers", instagram_command))
    dp.add_handler(CommandHandler("Floda", floda_command))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("reich", reich_command))
    dp.add_handler(CommandHandler("rolex", rolex_command))
    dp.add_handler(CommandHandler("bausparen", bausparen_command))
    dp.add_handler(CommandHandler("zukunft", zukunft_command))
    dp.add_handler(CommandHandler("weron", weron_command))
    #dp.add_handler(CommandHandler("wordcloud", wordcloud_command, pass_args=True))

    dp.add_handler(CommandHandler("alkohol", alkohol_command))
    dp.add_handler(CommandHandler("deppad", deppad_command))
    dp.add_handler(CommandHandler("aktien", aktien_command))
    dp.add_handler(CommandHandler("wein", wein_command))

    dp.add_handler(CommandHandler("register", register_command))
    dp.add_handler(CommandHandler("cash", money_status))
    dp.add_handler(CommandHandler("name", get_name_command))
    dp.add_handler(CommandHandler("wintercash", winter_cash_command))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, logging))

    print("Bot starting!")
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

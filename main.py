import os
import sys
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai
import logging
import requests

# Initialize the Telegram Bot
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Initialize the OpenAI API
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Set up the logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Handler for the /start command
def start(update, context):
    logger.info('Received /start command')
    update.message.reply_text("""
Hi!👋 I am Saif Chatbot.

Send me any text, and I will respond 🙂.

Use command /help 🔏 for more details.
    """)

# Handler for the /help command
def help(update, context):
    logger.info('Received /help command')
    help_message = """
    Here are the available commands.

    /talk - Use this command to have a chat with the bot.
    
    /quote - Generates and shares an inspirational or motivational quote.
    
    /fact - Shares an interesting fact on various topics.
    
    /joke - Responds with a random joke or a humorous message.
    """
    update.message.reply_text(help_message)

# Handler for the /talk command
def talk(update, context):
    logger.info('Received /talk command')
    user_message = update.message.text
    # Remove the /talk command from the message
    user_message = user_message.replace("/talk", "").strip()

    # Check if there's any user message left after removing the /talk command
    if not user_message:
        update.message.reply_text("""Hey there! 🤖 I'm your friendly Saif Chatbot, ready to chat with you! 😃

Just type '/talk' followed by your message.
example : /talk Hello!
and let's dive into an exciting conversation together! 🚀 Ask me anything, share your ideas, or tell me a joke – I'm all ears and eager to respond! 🎉""")
        return

    # If there's a user message, send it to OpenAI for generating the response
    response = get_openai_response(user_message)
    logger.info(f'Response from OpenAI: {response}')
    update.message.reply_text(response)

# Handler for the /quote command
def quote(update, context):
    logger.info('Received /quote command')
    quote = get_random_quote()
    update.message.reply_text(quote)

# Handler for the /fact command
def fact(update, context):
    logger.info('Received /fact command')
    fact = get_random_fact()
    update.message.reply_text(fact)

# Handler for the /joke command
def joke(update, context):
    logger.info('Received /joke command')
    joke = get_random_joke()
    update.message.reply_text(joke)

# Function to interact with ChatGPT-3.5 turbo using OpenAI API
def get_openai_response(user_message):
    try:
        prompt = "User: " + user_message + "\nChatGPT: "
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=250
        )
        return response['choices'][0]['text'].strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Apologies, there was an issue processing your request. Please try again later."

# Function to get a random inspirational or motivational quote from an API
def get_random_quote():
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            quote = response.json()
            return f"{quote['content']} - {quote['author']}"
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")
    return "Sorry, I couldn't fetch a quote at the moment."

# Function to get a random interesting fact from an API
def get_random_fact():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if response.status_code == 200:
            fact = response.json()
            return fact['text']
    except Exception as e:
        logger.error(f"Error fetching fact: {e}")
    return "Sorry, I couldn't fetch a fact at the moment."

# Function to get a random joke from an API
def get_random_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        if response.status_code == 200:
            joke = response.json()
            return f"{joke['setup']} {joke['punchline']}"
    except Exception as e:
        logger.error(f"Error fetching joke: {e}")
    return "Why did the chicken cross the road? To get to the other side!"

# Handler for processing incoming messages
def reply_message(update, context):
    user_message = update.message.text
    logger.info(f'Received message from user: {user_message}')

    # Check if the bot is mentioned with the /talk command
    if user_message.lower().startswith("/talk"):
        # Call the talk function to respond to the /talk command
        talk(update, context)
        return

    # Check if the user asks for the bot's name
    if user_message.lower() == "what's your name?" or user_message.lower() == "your name?":
        response = "Saif Chatbot"
    else:
        # Send the user message to OpenAI for generating the response
        response = get_openai_response(user_message)

    logger.info(f'Response from OpenAI: {response}')
    update.message.reply_text(response)

def main():
    port = int(os.environ.get("PORT", 5000))
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("talk", talk))
    dp.add_handler(CommandHandler("quote", quote))
    dp.add_handler(CommandHandler("fact", fact))
    dp.add_handler(CommandHandler("joke", joke))

    # Add message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command & Filters.group, reply_message))

    updater.start_webhook(listen="0.0.0.0", port=port, url_path=TELEGRAM_TOKEN)
    updater.bot.setWebhook(f"https://your-app-name.onrender.com/{TELEGRAM_TOKEN}")

    logger.info('Bot started polling')
    updater.idle()

if __name__ == "__main__":
    main()

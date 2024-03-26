import os
import json
import datetime
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, ContextTypes

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# File to store the counter data
COUNTER_FILE = 'joke_counter.json'

# Load the counter data from the file
def load_counter():
    try:
        with open(COUNTER_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save the counter data to the file
def save_counter(counter_data):
    try:
        with open(COUNTER_FILE, 'w') as file:
            json.dump(counter_data, file)
    except Exception as e:
        print(f"Error saving counter data: {e}")

# Increment the counter for the current date and chat
def increment_counter(counter_data, chat_id):
    today = datetime.date.today().isoformat()
    if chat_id not in counter_data:
        counter_data[chat_id] = {}
    counter_data[chat_id][today] = counter_data[chat_id].get(today, 0) + 1
    save_counter(counter_data)

# Handler for the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! I will count jokes per chat. Available commands:",
        reply_markup=ForceReply(selective=True),
    )
    await update.message.reply_text("/joke - Increment the joke counter for the current chat")
    await update.message.reply_text("/status - Get the current joke count for the current chat")

# Handler for the /joke command
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    counter_data = load_counter()
    increment_counter(counter_data, chat_id)
    today = datetime.date.today().isoformat()
    count = counter_data.get(chat_id, {}).get(today, 0)
    await update.message.reply_text(f"Joke received! Total for today in this chat is {count}")

# Handler for the /status command
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)
    counter_data = load_counter()
    today = datetime.date.today().isoformat()
    count = counter_data.get(chat_id, {}).get(today, 0)
    await update.message.reply_text(f"Joke count for today in this chat: {count}")

# Main function to set up the bot
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("joke", joke))
    application.add_handler(CommandHandler("status", status))

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    application.run_polling()

if __name__ == '__main__':
    main()
import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from qa import qa
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
def start(update, context):
    update.message.reply_text("سلام")
def handle_message(update, context):
    text = update.message.text.strip()
    answer = qa.get(text, "جوابی برای این سوال موجود نیست.")
    update.message.reply_text(answer)
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()
if __name__ == '__main__':
    main()

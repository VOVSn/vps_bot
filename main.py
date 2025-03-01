import logging
import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from logging_config import configure_logging
from message_handler import handle_message
from start_handler import start
from stop_handler import stop


load_dotenv()


def main():
    """Initialize and run the Telegram bot application."""
    configure_logging()
    logging.info('Starting the Telegram bot application')
    token = os.getenv('TELEGRAM_BOT_TOKEN', 'your-telegram-bot-token')
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message
    ))
    app.run_polling()


if __name__ == '__main__':
    main()

import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from constants import TELEGRAM_BOT_TOKEN
from utils.logging_config import configure_logging
from handlers.message_handler import handle_message
from handlers.start_handler import start
from handlers.stop_handler import stop
from handlers.delete_handler import delete
from handlers.model_handler import model


def main():
    """Initialize and run the Telegram bot application."""
    configure_logging()
    logging.info('Starting the Telegram bot application')
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('stop', stop))
    app.add_handler(CommandHandler('delete', delete))
    app.add_handler(CommandHandler('model', model))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message
    ))
    app.run_polling()


if __name__ == '__main__':
    main()

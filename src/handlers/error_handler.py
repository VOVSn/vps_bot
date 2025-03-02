import logging
from telegram import Update
from telegram.ext import ContextTypes


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors that occur during update processing."""
    # Log the error for debugging
    logging.error(f'Update "{update}" caused error "{context.error}"', exc_info=True)

    # If there's an update and a message, notify the user
    if update is not None and update.effective_message:
        try:
            await update.effective_message.reply_text(
                'Oops, something went wrong! Please try again later.'
            )
        except Exception as e:
            logging.error(f'Failed to send error message to user: {e}')
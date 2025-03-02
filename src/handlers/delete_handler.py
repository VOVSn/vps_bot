import os

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /delete command to remove user's chat history."""
    user_id = update.message.from_user.id
    chat_file = f'../chats/{user_id}.json'

    if os.path.exists(chat_file):
        try:
            os.remove(chat_file)
            await update.message.reply_text('Your chat history has been deleted.')
        except Exception as e:
            await update.message.reply_text(
                f'Failed to delete chat history: {str(e)}'
            )
    else:
        await update.message.reply_text('No chat history found to delete.')

delete_handler = CommandHandler('delete', delete)
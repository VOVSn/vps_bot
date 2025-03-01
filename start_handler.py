from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        'Hey! I can manage your VPS. Ask me anything (e.g., "give me contents '
        'of history.txt"). Use /stop to cancel a task.'
    )

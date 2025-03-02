from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command with a welcome message."""
    welcome_message = (
        'Hey! I’m VPSBuddy, your assistant for VPS management and chats.\n\n'
        'What I can do:\n'
        '- Chat with you (e.g., "What’s the weather like?")\n'
        '- Manage your VPS (e.g., "ping google" or "show contents of history.txt")\n\n'
        'Available commands:\n'
        '/start - Show this message\n'
        '/stop - Cancel a running task\n'
        '/delete - Clear your local chat history\n'
        '/model - Check the current Ollama model\n\n'
        'Just ask me anything to get started!'
    )
    await update.message.reply_text(welcome_message)

start_handler = CommandHandler('start', start)
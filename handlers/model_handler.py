import os

from telegram import Update
from telegram.ext import ContextTypes


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /model command to show the current Ollama model."""
    ollama_model = os.getenv('OLLAMA_MODEL', 'Not specified')
    try:
        if ollama_model == 'Not specified':
            await update.message.reply_text(
                'No Ollama model specified in the environment.'
            )
        else:
            await update.message.reply_text(
                f'The current Ollama model is: {ollama_model}'
            )
    except Exception as e:
        await update.message.reply_text(
            f'Error retrieving model information: {str(e)}'
        )
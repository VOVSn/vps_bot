import logging

from telegram import Update
from telegram.ext import ContextTypes

from task_handler import analyze_prompt, execute_vps_task, ollama_generate


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users."""
    user_input = update.message.text
    category = analyze_prompt(user_input)

    if category == 1:
        try:
            response = ollama_generate(user_input)
            await update.message.reply_text(
                response.get('response', 'No response').strip()
            )
        except Exception as e:
            logging.error(f'Failed to process user input with Ollama: {str(e)}')
            await update.message.reply_text(
                'Sorry, I couldn’t process that request due to an error.'
            )
    elif category == 2:
        await execute_vps_task(update, context, user_input)
    else:
        await update.message.reply_text('Sorry, I don’t understand that request.')
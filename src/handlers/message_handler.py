import json
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from handlers.task_handler import analyze_prompt, execute_vps_task, ollama_generate
from constants import MAX_HISTORY, AGENT_PRECONTEXT, CHAT_DIR


# def escape_markdown_v2(text):
#     """Escape special characters for MarkdownV2."""
#     reserved_chars = r'_*[]()~`>#+-|=}{.!'
#     escaped = ''
#     for char in text:
#         if char in reserved_chars:
#             escaped += f'\\{char}'
#         else:
#             escaped += char
#     return escaped


def save_conversation(conversation, chat_file, max_history=MAX_HISTORY):
    """Save conversation to JSON file, truncating if over max_history."""
    if len(conversation) > max_history:
        conversation = conversation[-max_history:]
    with open(chat_file, 'w') as f:
        json.dump(conversation, f, indent=2)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users."""
    user_id = update.message.from_user.id
    chat_file = os.path.join(CHAT_DIR, f'{user_id}.json')

    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            conversation = json.load(f)
    else:
        conversation = []

    user_message = update.message.text
    category = analyze_prompt(user_message)

    async def reply_and_log(message, **kwargs):
        # Escape special characters
        # escaped_message = escape_markdown_v2(message)
        # kwargs.setdefault('parse_mode')
        await update.message.reply_text(message, **kwargs)
        conversation.append(f'agent: {message}')
        save_conversation(conversation, chat_file)

    if category == 1:
        conversation.append(f'user: {user_message}')
        save_conversation(conversation, chat_file)
        try:
            history_str = '\n'.join(conversation)
            prompt = f'{AGENT_PRECONTEXT}\n{history_str}\nagent:'
            response = ollama_generate(prompt)
            agent_response = response.get('response', '').strip()
            await reply_and_log(agent_response)
        except Exception as e:
            logging.error(f'Failed to process with Ollama: {str(e)}')
            error_msg = 'Sorry, I couldn’t process that due to an error.'
            await reply_and_log(error_msg)
    elif category == 2:
        await execute_vps_task(update, context, user_message,
                               reply_func=reply_and_log)
    else:
        conversation.append(f'user: {user_message}')
        save_conversation(conversation, chat_file)
        await reply_and_log('Sorry, I don’t understand that request.')


message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
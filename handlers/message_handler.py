import json
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes

from handlers.task_handler import analyze_prompt, execute_vps_task, ollama_generate


MAX_HISTORY = 20


def save_conversation(conversation, chat_file, max_history=MAX_HISTORY):
    """Save conversation to JSON file, truncating if over max_history."""
    if len(conversation) > max_history:
        conversation = conversation[-max_history:]
    with open(chat_file, 'w') as f:
        json.dump(conversation, f, indent=2)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages from users."""
    user_id = update.message.from_user.id
    chat_file = f'chats/{user_id}.json'

    # Load existing conversation or start new
    if os.path.exists(chat_file):
        with open(chat_file, 'r') as f:
            conversation = json.load(f)
    else:
        conversation = []

    user_message = update.message.text
    category = analyze_prompt(user_message)

    # Define reply function to send and log agent messages
    async def reply_and_log(message):
        await update.message.reply_text(message)
        conversation.append(f'agent: {message}')
        save_conversation(conversation, chat_file)

    if category == 1:
        # For AI responses, store user message and process with history
        conversation.append(f'user: {user_message}')
        save_conversation(conversation, chat_file)
        try:
            history_str = '\n'.join(conversation)
            prompt = f'{history_str}\nagent:'
            response = ollama_generate(prompt)
            agent_response = response.get('response', '').strip()
            await reply_and_log(agent_response)
        except Exception as e:
            logging.error(f'Failed to process with Ollama: {str(e)}')
            error_msg = 'Sorry, I couldn’t process that due to an error.'
            await reply_and_log(error_msg)
    elif category == 2:
        # For tasks, do not store user message in conversation history
        # Execute task and let it handle replies
        await execute_vps_task(update, context, user_message,
                               reply_func=reply_and_log)
    else:
        # For unrecognized messages, store and respond
        conversation.append(f'user: {user_message}')
        save_conversation(conversation, chat_file)
        await reply_and_log('Sorry, I don’t understand that request.')
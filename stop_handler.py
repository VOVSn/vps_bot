from telegram import Update
from telegram.ext import ContextTypes

from task_handler import archive_completed_task, load_task_state, save_task_state


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /stop command to cancel a running task."""
    current_state = load_task_state()
    if not current_state:
        await update.message.reply_text('No task is currently running.')
        return
    if current_state.get('needed_command') == 'complete' or current_state.get(
        'task_complete'
    ):
        await update.message.reply_text(
            'No active task to stop; last task is already complete.'
        )
        return
    # Mark as stopped and archive
    current_state['task_complete'] = True
    save_task_state(current_state)
    archive_completed_task()
    await update.message.reply_text(
        f"Task (ID: {current_state['task_id']}) stopped and archived."
    )
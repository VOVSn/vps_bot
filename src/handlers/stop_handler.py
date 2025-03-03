from telegram.ext import CommandHandler
from utils.state_utils import load_task_state, save_task_state, archive_completed_task


async def stop(update, context):
    """Handle the /stop command to terminate the current task."""
    current_state = load_task_state()
    if not current_state:
        await update.message.reply_text('No task is currently running.')
        return

    if current_state.get('task_complete', False):
        await update.message.reply_text('No task is currently running.')
        return

    # Set stop flag
    current_state['stop_requested'] = True
    current_state['task_complete'] = True
    save_task_state(current_state)

    # Cancel the running task if it exists
    task_id = context.user_data.get('current_task_id')
    if task_id and task_id == current_state.get('task_id'):
        current_task = context.user_data.get('current_task')
        if current_task and not current_task.done():
            current_task.cancel()

    archive_completed_task()
    await update.message.reply_text('Task stopped successfully.')


stop_handler = CommandHandler('stop', stop)
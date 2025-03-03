import json
import logging
import re
import requests
import uuid
import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from constants import (
    VPS_PASSWORD, OLLAMA_API_URL, OLLAMA_MODEL, UNSAFE_COMMANDS,
    INTERACTIVE_COMMANDS, INTERACTIVE_COMMAND_MESSAGE,
    ANALYZE_PROMPT_TEMPLATE, EXPAND_USER_TASK_PROMPT_TEMPLATE,
    SUMMARIZE_TASK_PROMPT_TEMPLATE, INFER_NEXT_COMMAND_PROMPT_TEMPLATE,
    DEFAULT_SUMMARY_RESPONSE, TELEGRAM_MAX_MESSAGE_LENGTH
)
from utils.ssh_utils import ssh_connect, ssh_execute
from utils.state_utils import load_task_state, save_task_state, archive_completed_task


def ollama_generate(prompt):
    """Generate a response using the Ollama API."""
    logging.info(f'Ollama Prompt: {prompt}')
    payload = {
        'model': OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False,
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        logging.info(f'Ollama Response: {result}')
        return result
    except requests.RequestException as e:
        logging.error(f'Ollama API error: {str(e)}')
        raise


def expand_user_task(user_input):
    """Expand the user's task description using Ollama for clarity."""
    prompt = EXPAND_USER_TASK_PROMPT_TEMPLATE.format(user_input=user_input)
    response = ollama_generate(prompt)
    expanded_task = response.get('response', user_input).strip()
    return expanded_task


def summarize_task(task_state):
    """Summarize the completed task using Ollama."""
    task_state_json = json.dumps(task_state, indent=2)
    prompt = SUMMARIZE_TASK_PROMPT_TEMPLATE.format(task_state_json=task_state_json)
    response = ollama_generate(prompt)
    summary = response.get('response', DEFAULT_SUMMARY_RESPONSE).strip()
    return summary


def analyze_prompt(prompt):
    """Analyze the user's prompt to determine its category."""
    stripped_prompt = prompt.strip()
    if stripped_prompt.startswith('>'):
        if len(stripped_prompt) <= 1 or stripped_prompt[1:].strip() == '':
            return 3  # Treat empty > as invalid
        return 2

    analysis_prompt = ANALYZE_PROMPT_TEMPLATE.format(prompt=prompt)
    response = ollama_generate(analysis_prompt)
    response_text = response.get('response', '3').strip()
    if response_text and response_text[0].isdigit():
        return int(response_text[0])
    else:
        logging.error(f'Unexpected response format: {response_text}')
        return 3


def infer_next_command(task_state):
    """Infer the next SSH command based on the task state."""
    task_state_json = json.dumps(task_state, indent=2)
    prompt = INFER_NEXT_COMMAND_PROMPT_TEMPLATE.format(
        task_state_json=task_state_json, sudo_password=VPS_PASSWORD
    )
    response = ollama_generate(prompt)
    response_text = response.get('response', '').strip()

    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        try:
            update_dict = json.loads(json_str)
            logging.info(f'Next command: {update_dict}')
            return update_dict
        except json.JSONDecodeError as e:
            logging.error(f'JSON parse error: {str(e)}')
    else:
        logging.error('No JSON found in response')

    return {'needed_command': 'complete'}


async def validate_command(next_command, task_state, reply_func):
    """Validate the command for safety, interactivity, and repetitions."""
    task_state['command_repetitions'].setdefault(next_command, 0)
    task_state['command_repetitions'][next_command] += 1
    if task_state['command_repetitions'][next_command] > 2:
        await reply_func(
            f'Command `{next_command}` repeated more than twice. '
            'Terminating task to avoid potential loop.'
        )
        return False

    if any(unsafe in next_command for unsafe in UNSAFE_COMMANDS):
        await reply_func(f'Blocked unsafe command: {next_command}')
        return False

    command_base = next_command.split()[0] if next_command else ''
    if command_base in INTERACTIVE_COMMANDS:
        await reply_func(
            INTERACTIVE_COMMAND_MESSAGE.format(command=next_command)
        )
        return False
    return True


async def rewrite_sudo_command(next_command, output, reply_func):
    """Rewrite command to handle sudo issues."""
    if 'sudo: a terminal is required' in output or 'sudo: a password is required' in output:
        await reply_func(f'Command `{next_command}` failed due to sudo issues. Rewriting...')
        next_command = f'echo {VPS_PASSWORD} | sudo -S bash -c "{next_command}"'
        await reply_func(f'Retrying: `{next_command}`')
    return next_command


async def handle_interactive_prompt(next_command, output, task_state, reply_func):
    """Handle interactive prompt failures and update failed_attempts."""
    if 'Do you want to continue? [Y/n]' in output:
        task_state['failed_attempts'][next_command] = (
            task_state['failed_attempts'].get(next_command, 0) + 1
        )
        if task_state['failed_attempts'][next_command] >= 3:
            await reply_func(
                f'Command `{next_command}` repeatedly failed due to '
                'an interactive prompt. Terminating task.'
            )
            return False
    return True


async def send_output_in_chunks(reply_func, output: str, prefix: str = ''):
    """Send long output in chunks smaller than 4096 characters."""
    if not output:
        await reply_func(f'{prefix}No output.')
        return

    lines = output.splitlines()
    current_chunk = prefix
    for line in lines:
        line_with_newline = line + '\n'
        if len(current_chunk) + len(line_with_newline) > TELEGRAM_MAX_MESSAGE_LENGTH:
            if current_chunk != prefix:
                await reply_func(current_chunk.rstrip())
            current_chunk = prefix + line_with_newline
        else:
            current_chunk += line_with_newline

    if current_chunk != prefix:
        await reply_func(current_chunk.rstrip())


async def execute_vps_task(update: Update, context: ContextTypes.DEFAULT_TYPE,
                           user_input, reply_func=None):
    """Execute a task on the VPS based on user input."""
    if reply_func is None:
        reply_func = update.message.reply_text

    # Check for existing task
    current_state = load_task_state()
    if current_state and (
        current_state.get('needed_command') != 'complete' and
        not current_state.get('task_complete')
    ):
        await reply_func('Another task is in progress. Use /stop to cancel it.')
        return

    # Clear completed task state if it exists
    if current_state and (
        current_state.get('needed_command') == 'complete' or
        current_state.get('task_complete')
    ):
        archive_completed_task()

    expanded_task = expand_user_task(user_input)
    await reply_func(f'Expanded task: \n{expanded_task}')

    task_id = str(uuid.uuid4())
    task_state = {
        'task_id': task_id,
        'current_user_task': expanded_task,
        'original_user_task': user_input,
        'task_complete': False,
        'stop_requested': False,
        'history': [],
        'current_ssh_output': '',
        'needed_command': '',
        'failed_attempts': {},
        'command_repetitions': {},
    }
    save_task_state(task_state)
    ssh = ssh_connect()

    try:
        await reply_func(f'Starting task (ID: {task_id})...')
        # Store the task ID in context for cancellation
        context.user_data['current_task_id'] = task_id

        while True:
            # Check for stop request at the start of each iteration
            current_state = load_task_state()
            if current_state.get('stop_requested', False):
                await reply_func('Task stopped by user.')
                task_state['task_complete'] = True
                save_task_state(task_state)
                archive_completed_task()
                break

            # Yield control to allow cancellation
            await asyncio.sleep(0)

            ollama_response = infer_next_command(task_state)
            if 'needed_command' in ollama_response:
                task_state['needed_command'] = ollama_response['needed_command']
            save_task_state(task_state)

            # Check stop again after Ollama call
            current_state = load_task_state()
            if current_state.get('stop_requested', False):
                await reply_func('Task stopped by user.')
                task_state['task_complete'] = True
                save_task_state(task_state)
                archive_completed_task()
                break

            if task_state.get('needed_command') == 'complete':
                task_state['task_complete'] = True
                save_task_state(task_state)
                summary_msg = 'Task completed successfully!'
                if task_state['current_ssh_output']:
                    summary_msg += ' See output below:'
                await reply_func(summary_msg)
                await send_output_in_chunks(reply_func, task_state['current_ssh_output'])
                summary = summarize_task(task_state)
                await reply_func(f'Summary:\n{summary}')
                archive_completed_task()
                break

            next_command = task_state['needed_command']
            if not await validate_command(next_command, task_state, reply_func):
                task_state['task_complete'] = True
                save_task_state(task_state)
                summary = summarize_task(task_state)
                await reply_func(f'Summary:\n{summary}')
                archive_completed_task()
                break

            if 'apt-get' in next_command and '-y' not in next_command:
                parts = next_command.split('apt-get')
                if len(parts) > 1:
                    next_command = parts[0] + 'apt-get -y ' + ' '.join(parts[1].split()[1:])
                else:
                    next_command = next_command + ' -y'

            await reply_func(f'Running: `{next_command}`')
            output = ssh_execute(ssh, next_command)
            next_command = await rewrite_sudo_command(next_command, output, reply_func)
            await send_output_in_chunks(reply_func, output, prefix='Output:\n')
            task_state['history'].append({
                'command': next_command,
                'output': output
            })
            task_state['current_ssh_output'] = output

            # Check stop again after SSH execution
            current_state = load_task_state()
            if current_state.get('stop_requested', False):
                await reply_func('Task stopped by user.')
                task_state['task_complete'] = True
                save_task_state(task_state)
                archive_completed_task()
                break

            if not await handle_interactive_prompt(next_command, output, task_state, reply_func):
                task_state['task_complete'] = True
                save_task_state(task_state)
                summary = summarize_task(task_state)
                await reply_func(f'Summary:\n{summary}')
                archive_completed_task()
                break

            task_state['needed_command'] = ''
            save_task_state(task_state)

    except asyncio.CancelledError:
        await reply_func('Task cancelled by user.')
        task_state['task_complete'] = True
        save_task_state(task_state)
        archive_completed_task()
        raise

    except Exception as e:
        await reply_func(f'Error: {str(e)}')
        summary = summarize_task(task_state)
        await reply_func(f'Summary:\n{summary}', parse_mode='MarkdownV2')
        archive_completed_task()

    finally:
        ssh.close()
        if 'current_task_id' in context.user_data:
            del context.user_data['current_task_id']
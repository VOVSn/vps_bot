import os

from dotenv import load_dotenv


load_dotenv()


# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'your-telegram-bot-token')
VPS_IP = os.getenv('VPS_IP', '127.0.0.1')
VPS_USER = os.getenv('VPS_USER', 'your-vps-username')
VPS_PASSWORD = os.getenv('VPS_PASSWORD', 'your-vps-password')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'granite3.2:2b')
OLLAMA_API_URL = f'{OLLAMA_HOST}/api/generate'
JSON_FILE = os.getenv('JSON_FILE', '../tasks/task_state.json')

# Define BASE_DIR to ensure correct paths regardless of working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHAT_DIR = os.path.join(BASE_DIR, 'chats')
TASK_DIR = os.path.join(BASE_DIR, 'tasks')

MAX_HISTORY = 20

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

DEFAULT_SUMMARY_RESPONSE = 'No summary available.'


AGENT_PRECONTEXT = (
    'You are AI agent VPS_buddy, an intelligent agent that can answer technical '
    'questions and also connect to a VPS through SSH to perform operations there.'
)

# Other Constants
UNSAFE_COMMANDS = [
    #'rm -rf /',
    'halt',
    'shutdown -h now',
    'dd if=/dev/zero',
    ':(){ :|: & };:',
]

INTERACTIVE_COMMANDS = [
    'htop',
    'top',  # Without -b flag, top is interactive
    'nano',
    'vim',
    'vi',
    'less',
    'more',
    'watch',
]

INTERACTIVE_COMMAND_MESSAGE = (
    'The command `{command}` is interactive and cannot be run in this context. '
    'Consider using a non-interactive alternative (e.g., `ps aux` or `top -b -n 1` '
    'for system monitoring).'
)

ANALYZE_PROMPT_TEMPLATE = (
    'Analyze the user\'s prompt:\n"{prompt}"\n'
    '1. Answerable by AI immediately or small talk\n'
    '2. Requires VPS connection and actions, like shell commands\n'
    '3. None of the above\n'
    'Return only a single digit, no explanation, choose: (1 or 2 or 3)'
)

EXPAND_USER_TASK_PROMPT_TEMPLATE = (
    'Analyze and expand the user\'s input to a clear task plan with steps:\n'
    '"{user_input}"\n'
    'Provide a detailed description of the task in English, focusing on '
    'actions to be performed on a VPS. For example, if the user says '
    '"пингани гугл", expand it to "the user asks the agent to ping '
    'google.com from the VPS". Return only steps needed to accomplish task.'
    'If you are to check if something is installed, that means just check,'
    'advice to install only if explicitly said to install!'
    'Example of finding files: '
    'find / -name filename.txt 2>/dev/null || echo "No file or access denied."'
    'Be concise. 3-5 sentences for each step of the plan'
)

SUMMARIZE_TASK_PROMPT_TEMPLATE = (
    'Summarize the following completed task state in about 100 words:\n'
    '{task_state_json}\n'
    'Include what the task was (current_user_task), what commands were '
    'executed (history), and the final result (current_ssh_output or '
    'task_complete status). Be concise and focus on key details.'
)

INFER_NEXT_COMMAND_PROMPT_TEMPLATE = (
    'Based on the current task state:\n{task_state_json}\n'
    'Determine the next SSH command to execute for the task.'
    'CHECK:If the task is COMPLETE and no more commands are needed,'
    'set "needed_command" to "complete". Otherwise, provide the next command to run.'
    'For commands that require sudo,'
    'prepend echo {sudo_password} | sudo -S  to handle password input.'
    'For commands that may prompt for user input (e.g., Y/n), '
    'include non-interactive flags like "-y" for apt-get or equivalent. If a '
    'previous command failed due to an interactive prompt, adjust the command '
    'to include the appropriate flag or method to bypass the prompt. '
    'Return only JSON with "needed_command". NO EXPLANATION.'
    'Do not install anything unless it is requested to install'
    'for ping commands always add "-c 4"'
    'AVOID interactive commands like htop, vim, nano, watch and others'
)

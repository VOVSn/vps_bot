# constants.py
UNSAFE_COMMANDS = [
    'rm -rf /',
    'halt',
    'shutdown -h now',
    'dd if=/dev/zero',
    ':(){ :|: & };:',
]

# Prompt for analyzing the user's input to determine its category
ANALYZE_PROMPT_TEMPLATE = (
    'Analyze the user\'s prompt:\n"{prompt}"\n'
    '1. Answerable by AI immediately or small talk\n'
    '2. Requires VPS connection and actions, like shell commands, ping, install, check and other requests\n'
    '3. None of the above\n'
    'Return only a single digit, no explanation'
)

# Prompt for expanding the user's task description
EXPAND_USER_TASK_PROMPT_TEMPLATE = (
    'Analyze and expand the user\'s input to a clear task description:\n'
    '"{user_input}"\n'
    'Provide a detailed description of the task in English, focusing on '
    'actions to be performed on a VPS. For example, if the user says '
    '"пингани гугл", expand it to "the user asks the agent to ping '
    'google.com from the VPS". Return only the expanded description.'
)

# Prompt for summarizing a completed task
SUMMARIZE_TASK_PROMPT_TEMPLATE = (
    'Summarize the following completed task state in about 100 words:\n'
    '{task_state_json}\n'
    'Include what the task was (current_user_task), what commands were '
    'executed (history), and the final result (current_ssh_output or '
    'task_complete status). Be concise and focus on key details.'
)

# Prompt for inferring the next SSH command
INFER_NEXT_COMMAND_PROMPT_TEMPLATE = (
    'Based on the current task state:\n{task_state_json}\n'
    'Determine the next SSH command to execute for the task. If the task is '
    'complete and no more commands are needed, set "needed_command" to '
    '"complete". Otherwise, provide the next command to run. For commands '
    'that require sudo, prepend "echo {sudo_password} | sudo -S " to handle '
    'password input. For commands that may prompt for user input (e.g., Y/n), '
    'include non-interactive flags like "-y" for apt-get or equivalent. If a '
    'previous command failed due to an interactive prompt, adjust the command '
    'to include the appropriate flag or method to bypass the prompt. '
    'Return only JSON with "needed_command". NO EXPLANATION.'
    'Do not install anything unless it is requested to install'
    'for ping commands always add "-c 4"'
)

# Default response when no summary is available
DEFAULT_SUMMARY_RESPONSE = 'No summary available.'

# Telegram message length limit
TELEGRAM_MAX_MESSAGE_LENGTH = 4096
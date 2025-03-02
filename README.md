# Telegram VPS Task Automation Bot

## Overview
This project is a Telegram bot that automates task execution on a Virtual Private Server (VPS). The bot processes user messages, categorizes them, and executes appropriate tasks via SSH. It can also generate responses using the Ollama AI model, handle VPS commands securely, and maintain task history.

## Features
- **Task Automation**: Executes commands on a VPS through SSH based on user inputs.
- **AI-powered Prompt Analysis**: Uses the Ollama AI model to categorize user messages.
- **Task State Management**: Saves, loads, and archives task states for continuity.
- **Secure Command Execution**: Filters out unsafe commands and prevents execution of interactive commands.
- **Telegram Bot Integration**: Communicates with users through Telegram commands and messages.
- **Automatic Task Expansion and Summarization**: Enhances user input and provides a summary upon task completion.

## Tech Stack
- **Python**: Core programming language.
- **python-telegram-bot**: Telegram bot framework for handling user interactions.
- **Paramiko**: For executing SSH commands securely.
- **Ollama AI Model**: AI model used for analyzing and expanding user input.
- **dotenv**: For managing environment variables.
- **Logging**: Built-in Python logging for monitoring and debugging.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- A VPS with SSH access
- A Telegram bot token (from @BotFather on Telegram)

### Setup

1. **Clone the Repository**
   ```sh
   git clone https://github.com/VOVSn/vps-bot.git
   ```
2. **Create a Virtual Environment and Install Dependencies**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Set Up Environment Variables**
   Create a `.env` file and populate it with:
   ```env
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token
   VPS_IP=your-vps-ip
   VPS_USER=your-vps-username
   VPS_PASSWORD=your-vps-password
   OLLAMA_HOST=http://127.0.0.1:11434
   OLLAMA_MODEL=your-model
   ```

## Running the Bot
To start the bot, run:
```sh
python main.py
```
The bot will listen for messages and execute tasks accordingly.

## Usage
- **Start the Bot**: `/start`
- **Stop a Running Task**: `/stop`
- **Show current LLM model**: `/model`
- **Delete local chat history**: `/delete`
- **Send Commands**: Simply type a message, and the bot will categorize and process it.


## Security Considerations
- **Prevents Unsafe Commands**: Blocks potentially harmful SSH commands.
- **Limits Interactive Commands**: Detects and stops commands requiring user interaction.
- **Environment Variables**: Uses `.env` for sensitive configurations.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License.
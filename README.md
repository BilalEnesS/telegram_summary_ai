# AI Daily Literature & News Summary Bot

This project is a Python application that automatically tracks, summarizes, and sends daily reports of the latest academic papers, news, and blog posts in the field of artificial intelligence via Telegram.

## Features
- Collects up-to-date content from sources like ArXiv, AI News, OpenAI Blog, and more.
- Summarizes academic papers and news in Turkish using OpenAI LLM (GPT).
- Sends a detailed report to Telegram every day at a specified time (default: 10:00).
- Automatically splits long reports into multiple messages.
- Can automatically test bot connection and detect chat ID.
- Uses a `.env` file for secure management of API keys and credentials.

## Installation

1. **Clone or Download the Project Files**

2. **Install Required Python Packages**

```bash
pip install -r requirements.txt
```

3. **Create a Telegram Bot**
- Use [@BotFather](https://t.me/BotFather) to create a new bot.
- Obtain your bot token.

4. **Get Your OpenAI API Key**
- Obtain your API key from [OpenAI](https://platform.openai.com/api-keys).

5. **Create a .env File**
Create a file named `.env` in the project root directory and fill it as follows:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
OPENAI_API_KEY=your_openai_api_key_here
```

> **If you don't know your Chat ID:**
> - Send /start to your bot on Telegram.
> - Set `TELEGRAM_CHAT_ID` to `AUTO_DETECT` in your `.env` file.
> - When you run the program, your chat ID will be detected and printed to the console.

## Usage

```bash
python main.py
```

- The program will first test the Telegram connection.
- Then it will generate the daily report and send it to Telegram.
- The scheduler is set to run automatically every day at 10:00.

## Sources
- **Academic:** ArXiv (cs.AI, cs.CL, cs.CV, cs.LG, cs.NE)
- **News:** AI News, VentureBeat AI, The Batch
- **Blog:** OpenAI Blog, Google AI Blog, DeepMind Blog, Anthropic Blog

## Customization
- You can update the source lists in `main.py` as you wish.
- Report format and summary lengths can be changed in the relevant functions.

## Frequently Asked Questions
- **No message received:** Check your bot token and chat ID. Make sure you have sent /start to your bot.
- **API limit:** Your OpenAI API key quota may be exhausted.
- **Message too long:** Messages are automatically split to comply with Telegram's 4096 character limit.

## Contribution & License
- This project is licensed under the MIT License.
- You are welcome to contribute via pull requests.

---

Feel free to reach out for any questions or suggestions! 
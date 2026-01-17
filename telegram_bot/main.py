
import os
import sqlite3
import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME")
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 10))
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-7b-it")
YOUR_NAME = os.getenv("YOUR_NAME", "User")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

# Database path
DB_PATH = "/app/data/messages.db"

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def init_db():
    """Initializes the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

def add_message(update: Update):
    """Adds a message to the database."""
    if update.message.chat_id != ALLOWED_CHAT_ID:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, message_id, user_id, username, text) VALUES (?, ?, ?, ?, ?)",
        (
            update.message.chat_id,
            update.message.message_id,
            update.message.from_user.id,
            update.message.from_user.username,
            update.message.text,
        ),
    )
    conn.commit()
    conn.close()

async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles mentions and triggers OpenRouter."""
    if update.message.chat_id != ALLOWED_CHAT_ID:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, text FROM messages WHERE chat_id = ? ORDER BY timestamp DESC LIMIT ?",
        (ALLOWED_CHAT_ID, HISTORY_LIMIT),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("Not enough message history to generate a response.")
        return

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for username, text in reversed(rows):
        role = "assistant" if username == BOT_USERNAME else "user"
        if role == "user" and YOUR_NAME:
            name = YOUR_NAME
        else:
            name = username
        messages.append({"role": role, "content": f"{name}: {text}"})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": MODEL_NAME,
                "messages": messages,
            },
        )
        response.raise_for_status()
        reply = response.json()["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        await update.message.reply_text("Sorry, I couldn't generate a response.")

def main():
    """Starts the bot."""
    init_db()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handler for all messages to save them
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_message)
    )

    # Handler for mentions
    application.add_handler(
        MessageHandler(
            filters.Entity("mention") & filters.Regex(f"@{BOT_USERNAME}"),
            handle_mention,
        )
    )

    logger.info("Bot started")
    application.run_polling()

if __name__ == "__main__":
    main()

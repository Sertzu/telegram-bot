import os
import re
import sqlite3
import asyncio
import requests
import logging
from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Env
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.getenv("ALLOWED_CHAT_ID"))
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# BOT_USERNAME can be "MyBot" or "@MyBot"
BOT_USERNAME_RAW = os.getenv("BOT_USERNAME", "")
BOT_USERNAME = BOT_USERNAME_RAW.lstrip("@")
BOT_MENTION = f"@{BOT_USERNAME}"

HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", 10))
MODEL_NAME = os.getenv("MODEL_NAME", "google/gemma-7b-it")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant.")

DB_PATH = "/app/data/messages.db"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT,
            full_name TEXT,
            is_bot INTEGER NOT NULL DEFAULT 0,
            text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Migration for older DBs (adds missing columns if table already exists)
    cur.execute("PRAGMA table_info(messages)")
    cols = {row[1] for row in cur.fetchall()}
    if "full_name" not in cols:
        cur.execute("ALTER TABLE messages ADD COLUMN full_name TEXT")
    if "is_bot" not in cols:
        cur.execute("ALTER TABLE messages ADD COLUMN is_bot INTEGER NOT NULL DEFAULT 0")

    conn.commit()
    conn.close()


def _insert_message(chat_id: int, message_id: int, user_id: int, username: str, full_name: str, is_bot: int, text: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO messages (chat_id, message_id, user_id, username, full_name, is_bot, text)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (chat_id, message_id, user_id, username, full_name, is_bot, text),
    )
    conn.commit()
    conn.close()


async def store_message(msg: Message):
    if not msg or not msg.text:
        return
    if msg.chat_id != ALLOWED_CHAT_ID:
        return

    u = msg.from_user
    username = (u.username or "").strip()
    full_name = (u.full_name or "").strip()
    is_bot = 1 if (u and u.is_bot) else 0

    await asyncio.to_thread(
        _insert_message,
        msg.chat_id,
        msg.message_id,
        u.id if u else 0,
        username,
        full_name,
        is_bot,
        msg.text,
    )


def _fetch_history(chat_id: int, limit: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT user_id, username, full_name, is_bot, text
        FROM messages
        WHERE chat_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (chat_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


async def fetch_history(chat_id: int, limit: int):
    return await asyncio.to_thread(_fetch_history, chat_id, limit)


def build_openrouter_messages(rows):
    """
    rows: [(user_id, username, full_name, is_bot, text), ...] newest->oldest
    Output: OpenRouter chat messages oldest->newest with per-speaker labeling in content.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user_id, username, full_name, is_bot, text in reversed(rows):
        role = "assistant" if is_bot else "user"

        if is_bot:
            speaker = BOT_MENTION
        else:
            if username:
                speaker = f"@{username}"
            elif full_name:
                speaker = full_name
            else:
                speaker = f"user_{user_id}"
            # Stable disambiguator for group chats
            speaker = f"{speaker}#{user_id}"

        messages.append({"role": role, "content": f"{speaker}: {text}"})

    return messages


async def add_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.chat_id == ALLOWED_CHAT_ID:
        # Ignore storing bot's own incoming updates (rare, but possible)
        if update.message.from_user and update.message.from_user.is_bot:
            return
        await store_message(update.message)


async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.message.chat_id != ALLOWED_CHAT_ID:
        return
    if update.message.from_user and update.message.from_user.is_bot:
        return

    rows = await fetch_history(ALLOWED_CHAT_ID, HISTORY_LIMIT)
    if not rows:
        await update.message.reply_text("Not enough message history to generate a response.")
        return

    messages = build_openrouter_messages(rows)

    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                # Optional but useful with OpenRouter
                "HTTP-Referer": os.getenv("OPENROUTER_HTTP_REFERER", "http://localhost"),
                "X-Title": os.getenv("OPENROUTER_X_TITLE", "telegram-bot"),
            },
            json={
                "model": MODEL_NAME,
                "messages": messages,
                "temperature": 0.2,
                "reasoning": {"enabled": False},
            },
            timeout=30,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]

        sent = await update.message.reply_text(reply)
        await store_message(sent)  # store bot reply so the model sees it next time

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        await update.message.reply_text("Irgendwas funzt ned...")


def main():
    init_db()

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Save all text messages (group 0)
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_message),
        group=0,
    )

    # Trigger on mentions of this bot (group 1, runs after saving)
    mention_regex = rf"{re.escape(BOT_MENTION)}\b"
    application.add_handler(
        MessageHandler(
            filters.Entity("mention") & filters.Regex(mention_regex),
            handle_mention,
        ),
        group=1,
    )

    logger.info("Bot started")
    application.run_polling()


if __name__ == "__main__":
    main()

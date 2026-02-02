import os
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ========================
# Environment Variables
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Your Telegram bot token
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Gemini 2.0 Flash API key
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")    # PM system prompt

if not TELEGRAM_TOKEN or not GEMINI_API_KEY or not SYSTEM_PROMPT:
    raise ValueError("TELEGRAM_TOKEN, GEMINI_API_KEY or SYSTEM_PROMPT not set")

# ========================
# Conversation Memory
# ========================
# Keep per-user conversation history in memory (for multi-turn chat)
user_histories = {}

# ========================
# Gemini API Function
# ========================
def ask_gemini(user_id: int, user_input: str) -> str:
    # Initialize conversation if first message
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Add user message
    user_histories[user_id].append({"role": "user", "content": user_input})

    url = "https://api.studio.google.ai/v1/experiments/<gemini-model-id>:predict"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    payload = {
        "messages": user_histories[user_id],
        "max_output_tokens": 500
    }

    response = requests.post(url, json=payload, headers=headers)
    reply = response.json()["candidates"][0]["content"]

    # Add assistant response to history
    user_histories[user_id].append({"role": "assistant", "content": reply})
    return reply

# ========================
# Telegram Handlers
# ========================
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! I'm June, your PM assistant. Ask me anything about product strategy, roadmaps, or execution.")

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text

    # Call Gemini
    reply = ask_gemini(user_id, user_input)
    update.message.reply_text(reply)

# ========================
# Main Function
# ========================
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("June Telegram Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

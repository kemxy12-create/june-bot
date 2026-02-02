import os
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ========================
# Environment Variables
# ========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")   # New key
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

if not TELEGRAM_TOKEN or not GROQ_API_KEY or not SYSTEM_PROMPT:
    raise ValueError("TELEGRAM_TOKEN, GROQ_API_KEY, or SYSTEM_PROMPT not set")

# ========================
# Conversation Memory
# ========================
user_histories = {}

# ========================
# Groq API Function
# ========================
def ask_groq(user_id: int, user_input: str) -> str:
    if user_id not in user_histories:
        user_histories[user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    user_histories[user_id].append({"role": "user", "content": user_input})

    url = "https://api.groq.ai/v1/models/deepseek-r1/predict"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": user_histories[user_id]  # Groq expects messages as input
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        reply = response.json()["output"][0]["content"]
    except requests.exceptions.RequestException as e:
        reply = f"Sorry, I can't reach Groq right now. Error: {e}"

    user_histories[user_id].append({"role": "assistant", "content": reply})
    return reply

# ========================
# Telegram Handlers
# ========================
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Hello! I'm June, your PM assistant. Ask me anything about product strategy, roadmaps, or execution."
    )

def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_input = update.message.text

    reply = ask_groq(user_id, user_input)
    update.message.reply_text(reply)

# ========================
# Main Function
# ========================
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    print("June Telegram Bot is running on Groq...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

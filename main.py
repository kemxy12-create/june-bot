import os
import time
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or GROQ_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """
You are June, a calm, sharp AI product manager and founder-brain assistant.

You think in:
- user problems
- tradeoffs
- execution clarity
- realistic constraints

You avoid startup clichés and hallucinations.
You ask clarifying questions when needed.
You respond clearly, structured, and grounded.
"""

# Keep track of last update to avoid duplicates
last_update_id = None

def get_updates():
    global last_update_id
    url = f"{TELEGRAM_API}/getUpdates"
    if last_update_id:
        url += f"?offset={last_update_id + 1}"
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        return data.get("result", [])
    except Exception:
        return []

def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API}/sendMessage", json={"chat_id": chat_id, "text": text})

def query_groq(user_text):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
        result = resp.json()
        return result["choices"][0]["message"]["content"]
    except Exception:
        return "Sorry — I had a temporary issue. Try again."

# Main loop
while True:
    updates = get_updates()
    for u in updates:
        chat_id = u["message"]["chat"]["id"]
        user_text = u["message"].get("text", "")
        if not user_text:
            continue
        reply = query_groq(user_text)
        send_message(chat_id, reply)
        last_update_id = u["update_id"]
    time.sleep(2)  # poll every 2 seconds

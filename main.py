import os
import requests
from fastapi import FastAPI, Request

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

app = FastAPI()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

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
        reply = result["choices"][0]["message"]["content"]
    except Exception:
        reply = "Sorry — I had a temporary issue. Try again."

    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": reply}
    )

    return {"ok": True}

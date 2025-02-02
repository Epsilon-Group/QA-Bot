import os
import time
import requests
from dotenv import load_dotenv
from qa import qa
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params)
    return r.json()
def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
    if reply_markup:
        params["reply_markup"] = reply_markup
    requests.get(url, params=params)
def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates.get("ok"):
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue
                chat_id = message["chat"]["id"]
                text = message.get("text", "").strip()
                if text == "/questions":
                    qlist = ""
                    questions = list(qa.keys())
                    for i, q in enumerate(questions, 1):
                        qlist += f"{i}. {q}\n"
                    send_message(chat_id, qlist)
                    continue
                if text.isdigit():
                    idx = int(text) - 1
                    questions = list(qa.keys())
                    if 0 <= idx < len(questions):
                        answer = qa[questions[idx]]
                        send_message(chat_id, answer)
                        continue
                answer = qa.get(text, "جوابی برای این سوال موجود نیست.")
                send_message(chat_id, answer)
        time.sleep(1)
if __name__ == "__main__":
    main()

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
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    params = {"chat_id": chat_id, "text": text}
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
                text = message.get("text", "")
                answer = qa.get(text, "جوابی برای این سوال موجود نیست.")
                send_message(chat_id, answer)
        time.sleep(1)
if __name__ == "__main__":
    main()

import os
import time
import requests
import random
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
                if text == "/start":
                    send_message(chat_id, "سلام")
                    continue
                if text == "/help":
                    help_text = ("Available commands:\n"
                                 "start - Start the bot and show greeting message.\n"
                                 "help - Display help information and list all commands.\n"
                                 "questions - List available questions.\n"
                                 "random - Get a random Q&A pair.\n"
                                 "search - Search for questions by keyword.\n")
                    send_message(chat_id, help_text)
                    continue
                if text == "/questions":
                    qlist = ""
                    questions = list(qa.keys())
                    for i, q in enumerate(questions, 1):
                        qlist += f"{i}. {q}\n"
                    send_message(chat_id, qlist)
                    continue
                if text == "/random":
                    questions = list(qa.keys())
                    random_question = random.choice(questions)
                    answer = qa[random_question]
                    send_message(chat_id, f"Question: {random_question}\nAnswer: {answer}")
                    continue
                if text.startswith("/search "):
                    keyword = text[len("/search "):].strip()
                    matching = [q for q in qa.keys() if keyword.lower() in q.lower()]
                    if matching:
                        result = ""
                        for i, q in enumerate(matching, 1):
                            result += f"{i}. {q}\n"
                        send_message(chat_id, result)
                    else:
                        send_message(chat_id, "No matching questions found.")
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

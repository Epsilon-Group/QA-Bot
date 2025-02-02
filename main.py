import os
import time
import requests
import random
from dotenv import load_dotenv
from qa import qa

load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")  # شناسه کاربری مدیر (سازنده بات) که باید در فایل .env تنظیم شود
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
                    help_text = (
                        "دستورات موجود:\n"
                        "start - شروع و نمایش پیام خوش‌آمدگویی.\n"
                        "help - نمایش راهنمای دستورات و نحوه پرسیدن سوال.\n"
                        "questions - نمایش لیست سوالات از پیش تعریف‌شده.\n"
                        "random - دریافت یک پرسش و پاسخ تصادفی.\n"
                        "search - جستجو در سوالات بر اساس کلمه کلیدی (مثال: search ریاضی).\n"
                        "newfeature - ارسال پیشنهاد فیچر جدید به سازنده بات (مثال: newfeature اضافه کردن قابلیت X).\n\n"
                        "برای دریافت پاسخ از سوالات، شما می‌توانید:\n"
                        "1. شماره سوال را ارسال کنید (مثلاً 1 برای سوال اول)،\n"
                        "2. متن کامل سوال را وارد کنید، یا\n"
                        "3. بخشی از سوال را ارسال کنید تا در میان سوالات جستجو شود.\n"
                    )
                    send_message(chat_id, help_text)
                    continue
                if text == "/questions":
                    qlist = "لیست سوالات (برای دریافت پاسخ، شماره یا متن سوال را ارسال کنید):\n\n"
                    questions = list(qa.keys())
                    for i, q in enumerate(questions, 1):
                        qlist += f"{i}. {q}\n"
                    send_message(chat_id, qlist)
                    continue
                if text == "/random":
                    questions = list(qa.keys())
                    random_question = random.choice(questions)
                    answer = qa[random_question]
                    send_message(chat_id, f"سوال: {random_question}\n\nپاسخ: {answer}")
                    continue
                if text.startswith("/search"):
                    parts = text.split(maxsplit=1)
                    if len(parts) < 2 or not parts[1].strip():
                        send_message(chat_id, "برای استفاده از دستور search، باید پس از کلمه search، کلمه کلیدی را وارد کنید. مثال: search ریاضی")
                        continue
                    keyword = parts[1].strip().lower()
                    matching = [q for q in qa.keys() if keyword in q.lower()]
                    if matching:
                        result = "سوالات پیدا شده:\n\n"
                        for i, q in enumerate(matching, 1):
                            result += f"{i}. {q}\n"
                        send_message(chat_id, result)
                    else:
                        send_message(chat_id, "سوالی با این کلمه کلیدی یافت نشد.")
                    continue
                if text.startswith("/newfeature"):
                    parts = text.split(maxsplit=1)
                    if len(parts) < 2 or not parts[1].strip():
                        send_message(chat_id, "برای ارسال پیشنهاد فیچر جدید، دستور را به صورت:\nnewfeature متن پیشنهاد\nارسال کنید.")
                        continue
                    suggestion = parts[1].strip()
                    admin_message = f"پیشنهاد فیچر جدید از کاربر {chat_id}:\n\n{suggestion}"
                    if ADMIN_CHAT_ID:
                        send_message(ADMIN_CHAT_ID, admin_message)
                        send_message(chat_id, "پیشنهاد شما با موفقیت ارسال شد. سپاسگزاریم.")
                    else:
                        send_message(chat_id, "متاسفانه در ارسال پیشنهاد خطایی رخ داده است.")
                    continue
                if text.isdigit():
                    idx = int(text) - 1
                    questions = list(qa.keys())
                    if 0 <= idx < len(questions):
                        selected_question = questions[idx]
                        send_message(chat_id, f"سوال: {selected_question}\n\nپاسخ: {qa[selected_question]}")
                        continue
                matching = [q for q in qa.keys() if text.lower() in q.lower()]
                if matching:
                    if len(matching) == 1:
                        selected_question = matching[0]
                        send_message(chat_id, f"سوال: {selected_question}\n\nپاسخ: {qa[selected_question]}")
                    else:
                        result = "سوالات مشابه پیدا شده:\n\n"
                        for i, q in enumerate(matching, 1):
                            result += f"{i}. {q}\n"
                        send_message(chat_id, result)
                else:
                    send_message(chat_id, "جوابی برای این سوال موجود نیست.")
        time.sleep(1)

if __name__ == "__main__":
    main()

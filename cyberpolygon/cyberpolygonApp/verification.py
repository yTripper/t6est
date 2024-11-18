import os
from dotenv import load_dotenv
import requests
load_dotenv()


def send_verification_code_to_telegram(telegram_id, verification_code):
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    message = f'Ваш код верификации: {verification_code}'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={telegram_id}&text={message}"
    requests.get(url).json()
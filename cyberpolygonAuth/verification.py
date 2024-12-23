import os
import requests
from django.conf import settings


def send_verification_code_to_telegram(telegram_id, verification_code):
    TOKEN = settings.TELEGRAM_TOKEN
    message = f'Ваш код верификации: {verification_code}'
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={telegram_id}&text={message}"
    requests.get(url).json()
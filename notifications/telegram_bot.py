import requests
from django.conf import settings


def send_telegram_message(message: str) -> None:
    """Отправляет текстовое сообщение в Telegram-чат администраторов."""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not bot_token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        requests.post(url, json=payload, timeout=5)
    except requests.RequestException as e:
        print(f"Ошибка при отправке сообщения в Telegram: {e}")
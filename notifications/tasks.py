from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.telegram_bot import send_telegram_message


@shared_task
def check_overdue_borrowings():
    """Проверяет просроченные аренды и отправляет сводку в Telegram."""
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        send_telegram_message("🎉 Сегодня нет просроченных аренд!")
        return

    message = "⚠️ <b>ВНИМАНИЕ! Просроченные аренды:</b>\n\n"
    for borrowing in overdue_borrowings:
        days_overdue = (today - borrowing.expected_return_date).days
        message += (
            f"• <b>{borrowing.book.title}</b>\n"
            f"  Пользователь: {borrowing.user.email}\n"
            f"  Должен был вернуть: {borrowing.expected_return_date} (просрочено на {days_overdue} дн.)\n\n"
        )

    send_telegram_message(message)
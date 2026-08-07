from celery import shared_task
from django.utils import timezone

from borrowings.models import Borrowing
from notifications.telegram_bot import send_telegram_message


@shared_task
def check_overdue_borrowings():
    """Checks for overdue rentals and sends a summary to Telegram."""
    today = timezone.now().date()
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True,
    ).select_related("book", "user")

    if not overdue_borrowings.exists():
        send_telegram_message("🎉 There are no overdue rent payments today!")
        return

    message = "⚠️ <b>ATTENTION! Overdue rentals:</b>\n\n"
    for borrowing in overdue_borrowings:
        days_overdue = (today - borrowing.expected_return_date).days
        message += (
            f"• <b>{borrowing.book.title}</b>\n"
            f"  User: {borrowing.user.email}\n"
            f"  Was supposed to return: {borrowing.expected_return_date}"
            f"  (overdue by {days_overdue} дн.)\n\n"
        )

    send_telegram_message(message)

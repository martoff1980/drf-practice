from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Book
from borrowings.models import Borrowing

User = get_user_model()
BORROWINGS_URL = reverse("borrowings:borrowing-list")


class BorrowingApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="SOFT",
            inventory=2,
            daily_fee="1.50",
        )

    @patch("borrowings.views.send_telegram_message")
    @patch("borrowings.views.create_stripe_session")
    def test_create_borrowing_decreases_inventory(self, mock_stripe, mock_telegram):
        # Настраиваем мок Stripe
        mock_stripe.return_value = ("http://stripe.com/test", "session_123", 4.50)

        payload = {
            "book": self.book.id,
            "expected_return_date": (timezone.now() + timedelta(days=3)).date(),
        }

        response = self.client.post(BORROWINGS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Проверяем уменьшение инвентаря
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

        # Проверяем, что создалась запись аренды
        self.assertEqual(Borrowing.objects.count(), 1)
        
        # Проверяем вызов внешней функции отправки уведомления
        mock_telegram.assert_called_once()

    def test_create_borrowing_zero_inventory_fails(self):
        self.book.inventory = 0
        self.book.save()

        payload = {
            "book": self.book.id,
            "expected_return_date": (timezone.now() + timedelta(days=3)).date(),
        }

        response = self.client.post(BORROWINGS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing_increases_inventory(self):
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=timezone.now().date() + timedelta(days=2),
        )
        # Изначально при создании инвентарь уменьшался, делаем импровизированный тест
        self.book.inventory = 1
        self.book.save()

        return_url = reverse("borrowings:borrowing-return-borrowing", args=[borrowing.id])
        response = self.client.post(return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Инвентарь должен увеличиться обратно
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

        # Повторный возврат должен вернуть 400 Bad Request
        response_retry = self.client.post(return_url)
        self.assertEqual(response_retry.status_code, status.HTTP_400_BAD_REQUEST)
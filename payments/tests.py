from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Book
from borrowings.models import Borrowing
from payments.models import Payment

User = get_user_model()
PAYMENTS_URL = reverse("payments:payment-list")


class PaymentApiTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="user1@test.com", password="password")
        self.user2 = User.objects.create_user(email="user2@test.com", password="password")
        
        self.book = Book.objects.create(
            title="Book", author="Author", cover="HARD", inventory=5, daily_fee="2.00"
        )
        self.borrowing1 = Borrowing.objects.create(
            user=self.user1, book=self.book, expected_return_date="2026-08-10"
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user2, book=self.book, expected_return_date="2026-08-10"
        )

        self.payment1 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing1,
            session_url="https://stripe.com/1",
            session_id="sess_1",
            money_to_pay="10.00",
        )
        self.payment2 = Payment.objects.create(
            status="PENDING",
            type="PAYMENT",
            borrowing=self.borrowing2,
            session_url="https://stripe.com/2",
            session_id="sess_2",
            money_to_pay="15.00",
        )

    def test_user_sees_only_own_payments(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.payment1.id)
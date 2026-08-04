from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from books.models import Book

User = get_user_model()
BOOKS_URL = reverse("books:book-list")


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthenticatedBookApiTests(APITestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            cover="HARD",
            inventory=5,
            daily_fee="2.99",
        )

    def test_list_books_success(self):
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_book_forbidden(self):
        payload = {
            "title": "Refactoring",
            "author": "Martin Fowler",
            "cover": "SOFT",
            "inventory": 3,
            "daily_fee": "1.99",
        }
        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminBookApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@test.com", password="password123"
        )
        self.client.force_authenticate(user=self.admin)
        self.book = Book.objects.create(
            title="Clean Code",
            author="Robert Martin",
            cover="HARD",
            inventory=5,
            daily_fee="2.99",
        )

    def test_create_book_success(self):
        payload = {
            "title": "Design Patterns",
            "author": "GoF",
            "cover": "HARD",
            "inventory": 10,
            "daily_fee": "4.50",
        }
        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_book_success(self):
        url = detail_url(self.book.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
from rest_framework import serializers
from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        )


class BookListSerializer(serializers.ModelSerializer):
    """Облегченный сериализатор для списка книг"""
    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")
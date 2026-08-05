from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.serializers import BookSerializer
from borrowings.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "is_active",
        )
        read_only_fields = (
            "id",
            "borrow_date",
            "actual_return_date",
            "user",
            "is_active",
        )


class BorrowingListSerializer(BorrowingSerializer):
    """Detailed display of book information in the rental list"""

    book = BookSerializer(read_only=True)


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "expected_return_date", "book")

    def validate(self, attrs):
        data = super().validate(attrs)
        book = attrs["book"]

        # Validation of book availability
        if book.inventory < 1:
            raise ValidationError(
                {"book": "Unfortunately, this book is currently out of stock."}
            )

        # Return date validation
        if attrs["expected_return_date"] <= timezone.now().date():
            raise ValidationError(
                {
                    "expected_return_date":
                        "The expected return date must be later than today."
                }
            )

        return data

    def create(self, validated_data):
        with transaction.atomic():
            book = validated_data["book"]
            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(**validated_data)
            return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")
        read_only_fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise ValidationError(
                {"borrowing": "This book was already returned earlier."}
            )
        return attrs

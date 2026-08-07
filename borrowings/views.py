from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
    BorrowingSerializer,
)

from payments.models import Payment
from payments.stripe_utils import create_stripe_session

from notifications.telegram_bot import send_telegram_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user

        # For regular users — only their own rentals.
        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # Filtering for admins by the `user_id` query parameter
        user_id = self.request.query_params.get("user_id")
        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filtering by rental activity (?is_active=true/false)
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            is_active_bool = is_active.lower() == "true"
            queryset = queryset.filter(
                actual_return_date__isnull=is_active_bool
            )

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return BorrowingListSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    @action(detail=True, methods=["post"], url_path="return")
    def return_borrowing(self, request, pk=None):
        """POST borrowings/<id>/return/ — recording the return of a book"""
        borrowing = self.get_object()
        serializer = self.get_serializer(borrowing, data=request.data)
        (
            serializer.is_validate(raise_exception=True)
            if hasattr(serializer, "is_validate")
            else serializer.is_valid(raise_exception=True)
        )

        with transaction.atomic():
            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            # Returning the book to the warehouse
            book = borrowing.book
            book.inventory += 1
            book.save()

        return Response(
            BorrowingListSerializer(borrowing).data,
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)

        # Stripe Checkout session
        session_url, session_id, money_to_pay = create_stripe_session(
            borrowing=borrowing, request=self.request
        )

        # Fixed record in Payment
        Payment.objects.create(
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT,
            borrowing=borrowing,
            session_url=session_url,
            session_id=session_id,
            money_to_pay=money_to_pay,
        )

        # Telegram Notification
        message = (
            f"📖 <b>New rental!</b>\n\n"
            f"<b>Book:</b> {borrowing.book.title}\n"
            f"<b>User:</b> {borrowing.user.email}\n"
            f"<b>Return date:</b> {borrowing.expected_return_date}\n"
            f"<b>Amount due:</b> ${money_to_pay}"
        )
        send_telegram_message(message)

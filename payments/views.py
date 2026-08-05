import stripe
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for viewing payments and checking their status in Stripe
    """

    queryset = Payment.objects.select_related("borrowing")
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        return queryset

    @action(detail=False, methods=["get"], url_path="success")
    def success(self, request):
        """GET /api/payments/success/?session_id=..."""
        session_id = request.query_params.get("session_id")
        if not session_id:
            return Response(
                {"error": "The session_id parameter is mandatory."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.filter(session_id=session_id).first()
        if not payment:
            return Response(
                {"error": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Checking the status in Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == "paid":
            payment.status = Payment.Status.PAID
            payment.save()
            return Response(
                {
                    "message": "The payment was successful!",
                    "payment": PaymentSerializer(payment).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "The payment has not yet been completed."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"], url_path="cancel")
    def cancel(self, request):
        """GET /api/payments/cancel/"""
        return Response(
            {
                "message":
                    "The payment was cancelled. "
                    "You can complete the payment later "
                    "(the session is valid for 24 hours)."
            },
            status=status.HTTP_200_OK,
        )

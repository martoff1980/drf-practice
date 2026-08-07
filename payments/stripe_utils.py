import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_session(borrowing, request, payment_type="PAYMENT"):
    """
    Creates a Stripe payment session and returns
    (session_url, session_id, total_price)
    """
    # Calculation of the number of days
    days_borrowed = (
        borrowing.expected_return_date - borrowing.borrow_date
        ).days
    days_borrowed = max(days_borrowed, 1)  # Min 1 day

    # Calculation of the amount in $USD
    money_to_pay = borrowing.book.daily_fee * days_borrowed

    # Constructing the callback URL
    success_url = (
        request.build_absolute_uri(reverse("payments:payment-success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("payments:payment-cancel"))

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(
                        money_to_pay * 100
                    ),  # Stripe accepts the amount in cents.
                    "product_data": {
                        "name": f"Borrowing: {borrowing.book.title}",
                        "description": f"Fee for {days_borrowed} day(s)",
                    },
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return session.url, session.id, money_to_pay

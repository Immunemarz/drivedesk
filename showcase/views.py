import base64
import json

import requests
import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import TransactionLog


PRODUCTS = [
    {
        "name": "DriveDesk Tech Pouch",
        "slug": "drivedesk-tech-pouch",
        "category": "Carry",
        "price": "$50",
        "price_cents": 5000,
        "tagline": "The hero pouch for cables, charger, pen, cloth, and daily carry tools.",
        "details": "Structured pouch with elastic loops, zip mesh, microfiber sleeve, and compact desk-to-car carry.",
        "image_url": "https://images.pexels.com/photos/9185853/pexels-photo-9185853.jpeg?cs=srgb&dl=pexels-timur-weber-9185853.jpg&fm=jpg",
    },
    {
        "name": "Executive Carry Case",
        "slug": "executive-carry-case",
        "category": "Carry",
        "price": "$70",
        "price_cents": 7000,
        "tagline": "A larger organizer for charger bricks, adapters, notebook, and small tools.",
        "details": "Dual-layer hard-shell case with cord channels, pen sleeve, passport pocket, and grab loop.",
        "image_url": "https://images.pexels.com/photos/34929061/pexels-photo-34929061.jpeg?cs=srgb&dl=pexels-a-a-54155102-34929061.jpg&fm=jpg",
    },
    {
        "name": "Desk Reset Rail",
        "slug": "desk-reset-rail",
        "category": "Desk",
        "price": "$35",
        "price_cents": 3500,
        "tagline": "Hide the visual noise under your workstation.",
        "details": "Under-desk cable tray with magnetic clips, soft ties, and edge anchors for a cleaner surface.",
        "image_url": "https://images.pexels.com/photos/34934741/pexels-photo-34934741.jpeg?cs=srgb&dl=pexels-a-a-54155102-34934741.jpg&fm=jpg",
    },
    {
        "name": "Aluminum Laptop Riser",
        "slug": "aluminum-laptop-riser",
        "category": "Desk",
        "price": "$50",
        "price_cents": 5000,
        "tagline": "Better posture without making your desk look busy.",
        "details": "Low-profile riser with cable pass-through, non-slip base, and minimal brushed finish.",
        "image_url": "https://images.pexels.com/photos/13279384/pexels-photo-13279384.jpeg?cs=srgb&dl=pexels-pramodtiwari-13279384.jpg&fm=jpg",
    },
    {
        "name": "Commute Command Pouch",
        "slug": "commute-command-pouch",
        "category": "Car",
        "price": "$70",
        "price_cents": 7000,
        "tagline": "A cleaner glovebox and console pouch for the daily driver.",
        "details": "Vehicle pouch with charger, cloth, registration sleeve, pen, tire gauge, and emergency light.",
        "image_url": "https://images.pexels.com/photos/30563035/pexels-photo-30563035.jpeg?cs=srgb&dl=pexels-andreas-naslund-92380530-30563035.jpg&fm=jpg",
    },
    {
        "name": "MagSafe Dash Mount",
        "slug": "magsafe-dash-mount",
        "category": "Car",
        "price": "$39",
        "price_cents": 3900,
        "tagline": "Secure phone placement that still looks premium.",
        "details": "Strong magnetic mount with low-glare angle control and woven USB-C cable.",
        "image_url": "https://images.pexels.com/photos/4824425/pexels-photo-4824425.jpeg?cs=srgb&dl=pexels-maksgelatin-4824425.jpg&fm=jpg",
    },
    {
        "name": "Seat-Gap Organizer",
        "slug": "seat-gap-organizer",
        "category": "Car",
        "price": "$20",
        "price_cents": 2000,
        "tagline": "A simple fix for keys, cards, receipts, and cables.",
        "details": "Slim organizer with card sleeve, cable notch, and soft-touch interior.",
        "image_url": "https://images.pexels.com/photos/6969025/pexels-photo-6969025.jpeg?cs=srgb&dl=pexels-lynxexotics-6969025.jpg&fm=jpg",
    },
    {
        "name": "Full Reset Bundle",
        "slug": "full-reset-bundle",
        "category": "Bundles",
        "price": "$150",
        "price_cents": 15000,
        "tagline": "The best carry, desk, and car pieces in one daily system.",
        "details": "DriveDesk Tech Pouch, Desk Reset Rail, MagSafe Dash Mount, and microfiber pouch bundled together.",
        "image_url": "https://images.pexels.com/photos/30868621/pexels-photo-30868621.jpeg?cs=srgb&dl=pexels-efrem-efre-2786187-30868621.jpg&fm=jpg",
    },
    {
        "name": "Creator Transit Bundle",
        "slug": "creator-transit-bundle",
        "category": "Bundles",
        "price": "$195",
        "price_cents": 19500,
        "tagline": "A larger premium bundle for people moving between desk, studio, and car.",
        "details": "Executive Carry Case, Aluminum Laptop Riser, Commute Command Pouch, and cable essentials.",
        "image_url": "https://images.pexels.com/photos/34929061/pexels-photo-34929061.jpeg?cs=srgb&dl=pexels-a-a-54155102-34929061.jpg&fm=jpg",
    },
]

PRODUCT_LOOKUP = {product["slug"]: product for product in PRODUCTS}


def get_product_or_404(slug):
    product = PRODUCT_LOOKUP.get(slug)
    if not product:
        raise Http404("Product not found")
    return product


def parse_quantity(raw_value):
    try:
        quantity = int(raw_value)
    except (TypeError, ValueError):
        quantity = 1
    return max(1, min(quantity, 5))


def parse_cart_items(payload):
    raw_items = payload.get("cart_items", [])
    normalized = []
    for raw_item in raw_items:
        slug = (raw_item.get("slug") or "").strip()
        if slug not in PRODUCT_LOOKUP:
            continue
        quantity = parse_quantity(raw_item.get("quantity", 1))
        normalized.append((PRODUCT_LOOKUP[slug], quantity))
    return normalized


def transaction_items(cart_items):
    return [
        {
            "name": product["name"],
            "slug": product["slug"],
            "quantity": quantity,
            "unit_amount_cents": product["price_cents"],
            "line_amount_cents": product["price_cents"] * quantity,
        }
        for product, quantity in cart_items
    ]


def transaction_total_cents(cart_items):
    return sum(product["price_cents"] * quantity for product, quantity in cart_items)


def stripe_is_configured():
    return bool(settings.STRIPE_PUBLISHABLE_KEY and settings.STRIPE_SECRET_KEY)


def stripe_configuration_error():
    missing = []
    if not settings.STRIPE_PUBLISHABLE_KEY:
        missing.append("STRIPE_PUBLISHABLE_KEY")
    if not settings.STRIPE_SECRET_KEY:
        missing.append("STRIPE_SECRET_KEY")
    if not missing:
        return ""
    return f"Stripe is not configured. Missing: {', '.join(missing)}."


def notify_temp_gmail(subject, lines):
    body = "\n".join(lines)
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ORDER_NOTIFICATION_EMAIL],
        fail_silently=False,
    )


def paypal_access_token():
    credentials = f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_CLIENT_SECRET}"
    auth_header = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    response = requests.post(
        f"{settings.PAYPAL_API_BASE}/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def paypal_error_message(error):
    response = getattr(error, "response", None)
    if response is None:
        return str(error)
    try:
        details = response.json()
    except ValueError:
        return response.text or str(error)
    return (
        details.get("error_description")
        or details.get("message")
        or details.get("name")
        or details.get("error")
        or str(details)
    )


@ensure_csrf_cookie
def home(request):
    featured_products = [
        {
            "name": product["name"],
            "category": product["category"],
            "metric": product["price"],
            "note": product["tagline"],
            "image_url": product["image_url"],
        }
        for product in (PRODUCTS[0], PRODUCTS[4], PRODUCTS[6])
    ]
    return render(request, "showcase/home.html", {"products": featured_products})


def products(request):
    categories = ["All", "Desk", "Car", "Carry", "Bundles"]
    return render(
        request,
        "showcase/products.html",
        {"products": PRODUCTS, "categories": categories},
    )


def cart(request):
    return render(request, "showcase/cart.html", {"products": PRODUCTS})


@ensure_csrf_cookie
def checkout(request, slug):
    product = get_product_or_404(slug)
    return render(
        request,
        "showcase/checkout.html",
        {
            "product": product,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "stripe_configured": stripe_is_configured(),
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
        },
    )


@ensure_csrf_cookie
def checkout_cart(request):
    return render(
        request,
        "showcase/checkout.html",
        {
            "product": None,
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "stripe_configured": stripe_is_configured(),
            "paypal_client_id": settings.PAYPAL_CLIENT_ID,
            "cart_mode": True,
        },
    )


def checkout_success(request):
    if request.GET.get("provider") == "stripe" and request.GET.get("session_id"):
        session_id = request.GET["session_id"]
        TransactionLog.objects.filter(
            provider=TransactionLog.PROVIDER_STRIPE,
            external_id=session_id,
        ).update(status=TransactionLog.STATUS_PAID)
    return render(request, "showcase/checkout_success.html")


def checkout_cancel(request):
    slug = request.GET.get("product", "")
    product = PRODUCT_LOOKUP.get(slug)
    return render(request, "showcase/checkout_cancel.html", {"product": product})


@require_POST
def join_updates(request):
    payload = json.loads(request.body or "{}")
    email = (payload.get("email") or "").strip()
    if not email:
        return JsonResponse({"error": "Email is required."}, status=400)

    notify_temp_gmail(
        "DriveDesk product updates signup",
        [
            f"Email: {email}",
            "Source: homepage collection form",
        ],
    )
    return JsonResponse({"ok": True})


@require_POST
def send_feedback(request):
    payload = json.loads(request.body or "{}")
    name = (payload.get("name") or "").strip()
    email = (payload.get("email") or "").strip()
    message = (payload.get("message") or "").strip()

    if not name or not email or not message:
        return JsonResponse({"error": "Name, email, and feedback are required."}, status=400)

    notify_temp_gmail(
        "DriveDesk customer feedback",
        [
            f"Name: {name}",
            f"Email: {email}",
            "",
            "Feedback:",
            message,
        ],
    )
    return JsonResponse({"ok": True})


@require_POST
def create_stripe_checkout_session(request):
    configuration_error = stripe_configuration_error()
    if configuration_error:
        return JsonResponse({"error": configuration_error}, status=400)

    payload = json.loads(request.body or "{}")
    customer_name = (payload.get("customer_name") or "").strip()
    customer_email = (payload.get("customer_email") or "").strip()

    cart_items = parse_cart_items(payload)
    if not cart_items:
        slug = payload.get("slug", "")
        if not slug:
            return JsonResponse({"error": "Your cart is empty."}, status=400)
        quantity = parse_quantity(payload.get("quantity", 1))
        product = get_product_or_404(slug)
        cart_items = [(product, quantity)]

    line_items = []
    summary_lines = []

    for product, quantity in cart_items:
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": product["price_cents"],
                    "product_data": {
                        "name": product["name"],
                        "description": product["details"],
                        "images": [product["image_url"]],
                    },
                },
                "quantity": quantity,
            }
        )
        summary_lines.append(f"{product['name']} x {quantity}")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            customer_email=customer_email or None,
            payment_method_types=["card"],
            metadata={
                "items": " | ".join(summary_lines),
                "customer_name": customer_name,
                "customer_email": customer_email,
            },
            success_url=request.build_absolute_uri(f"{reverse('checkout_success')}?provider=stripe&session_id={{CHECKOUT_SESSION_ID}}"),
            cancel_url=request.build_absolute_uri(reverse("checkout_cancel")),
        )
    except stripe.error.StripeError as error:
        TransactionLog.objects.create(
            provider=TransactionLog.PROVIDER_STRIPE,
            status=TransactionLog.STATUS_FAILED,
            customer_name=customer_name,
            customer_email=customer_email,
            items=transaction_items(cart_items),
            amount_cents=transaction_total_cents(cart_items),
            currency="usd",
            notes=str(error),
        )
        return JsonResponse({"error": str(error)}, status=400)

    TransactionLog.objects.create(
        provider=TransactionLog.PROVIDER_STRIPE,
        status=TransactionLog.STATUS_STARTED,
        external_id=session.id,
        customer_name=customer_name,
        customer_email=customer_email,
        items=transaction_items(cart_items),
        amount_cents=transaction_total_cents(cart_items),
        currency="usd",
        notes="Stripe Checkout session created.",
    )

    notify_temp_gmail(
        "Stripe checkout started",
        [
            f"Items: {', '.join(summary_lines)}",
            f"Name: {customer_name or 'N/A'}",
            f"Email: {customer_email or 'N/A'}",
            "Provider: Stripe Checkout",
        ],
    )

    return JsonResponse({"checkout_url": session.url})


@require_POST
def create_paypal_order(request):
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        return JsonResponse({"error": "PayPal is not configured."}, status=400)

    payload = json.loads(request.body or "{}")
    customer_name = (payload.get("customer_name") or "").strip()
    customer_email = (payload.get("customer_email") or "").strip()
    cart_items = parse_cart_items(payload)
    if not cart_items:
        slug = payload.get("slug", "")
        if not slug:
            return JsonResponse({"error": "Your cart is empty."}, status=400)
        quantity = parse_quantity(payload.get("quantity", 1))
        product = get_product_or_404(slug)
        cart_items = [(product, quantity)]

    purchase_units = []
    summary_lines = []

    total_cents = transaction_total_cents(cart_items)
    for product, quantity in cart_items:
        summary_lines.append(f"{product['name']} x {quantity}")
    purchase_units.append(
        {
            "description": "DriveDesk cart checkout" if len(cart_items) > 1 else cart_items[0][0]["name"],
            "amount": {"currency_code": "USD", "value": f"{total_cents / 100:.2f}"},
            "custom_id": "cart-checkout" if len(cart_items) > 1 else cart_items[0][0]["slug"],
        }
    )

    try:
        access_token = paypal_access_token()
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": purchase_units,
                "payment_source": {"paypal": {"experience_context": {"shipping_preference": "NO_SHIPPING"}}},
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        message = paypal_error_message(error)
        TransactionLog.objects.create(
            provider=TransactionLog.PROVIDER_PAYPAL,
            status=TransactionLog.STATUS_FAILED,
            customer_name=customer_name,
            customer_email=customer_email,
            items=transaction_items(cart_items),
            amount_cents=total_cents,
            currency="usd",
            notes=message,
        )
        return JsonResponse({"error": message}, status=400)

    notify_temp_gmail(
        "PayPal checkout started",
        [
            f"Items: {', '.join(summary_lines)}",
            f"Name: {customer_name or 'N/A'}",
            f"Email: {customer_email or 'N/A'}",
            "Provider: PayPal",
        ],
    )

    order_id = response.json()["id"]
    TransactionLog.objects.create(
        provider=TransactionLog.PROVIDER_PAYPAL,
        status=TransactionLog.STATUS_STARTED,
        external_id=order_id,
        customer_name=customer_name,
        customer_email=customer_email,
        items=transaction_items(cart_items),
        amount_cents=total_cents,
        currency="usd",
        notes="PayPal order created.",
    )

    return JsonResponse({"order_id": order_id})


@require_POST
def capture_paypal_order(request):
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        return JsonResponse({"error": "PayPal is not configured."}, status=400)

    payload = json.loads(request.body or "{}")
    order_id = payload.get("order_id", "")
    customer_name = (payload.get("customer_name") or "").strip()
    customer_email = (payload.get("customer_email") or "").strip()
    cart_items = parse_cart_items(payload)
    if cart_items:
        summary_lines = [f"{product['name']} x {quantity}" for product, quantity in cart_items]
    else:
        slug = payload.get("slug", "")
        if not slug:
            return JsonResponse({"error": "Your cart is empty."}, status=400)
        quantity = parse_quantity(payload.get("quantity", 1))
        product = get_product_or_404(slug)
        summary_lines = [f"{product['name']} x {quantity}"]

    try:
        access_token = paypal_access_token()
        response = requests.post(
            f"{settings.PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        message = paypal_error_message(error)
        TransactionLog.objects.filter(
            provider=TransactionLog.PROVIDER_PAYPAL,
            external_id=order_id,
        ).update(status=TransactionLog.STATUS_FAILED, notes=message)
        return JsonResponse({"error": message}, status=400)

    TransactionLog.objects.filter(
        provider=TransactionLog.PROVIDER_PAYPAL,
        external_id=order_id,
    ).update(
        status=TransactionLog.STATUS_PAID,
        customer_name=customer_name,
        customer_email=customer_email,
        notes="PayPal order captured.",
    )

    notify_temp_gmail(
        "PayPal order captured",
        [
            f"Items: {', '.join(summary_lines)}",
            f"Name: {customer_name or 'N/A'}",
            f"Email: {customer_email or 'N/A'}",
            f"PayPal order id: {order_id}",
        ],
    )

    return JsonResponse({"ok": True, "redirect_url": f"{reverse('checkout_success')}?provider=paypal"})

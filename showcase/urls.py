from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("cart/", views.cart, name="cart"),
    path("checkout/cart/", views.checkout_cart, name="checkout_cart"),
    path("checkout/success/", views.checkout_success, name="checkout_success"),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),
    path("checkout/<slug:slug>/", views.checkout, name="checkout"),
    path("api/join-updates/", views.join_updates, name="join_updates"),
    path("api/send-feedback/", views.send_feedback, name="send_feedback"),
    path("api/stripe/create-checkout-session/", views.create_stripe_checkout_session, name="create_stripe_checkout_session"),
    path("api/paypal/create-order/", views.create_paypal_order, name="create_paypal_order"),
    path("api/paypal/capture-order/", views.capture_paypal_order, name="capture_paypal_order"),
]

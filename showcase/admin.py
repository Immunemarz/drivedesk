from django.contrib import admin

from .models import Coupon, TransactionLog


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ("provider", "status", "amount_cents", "customer_email", "external_id", "created_at")
    list_filter = ("provider", "status", "created_at")
    search_fields = ("external_id", "customer_email", "customer_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "percent_off", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code",)

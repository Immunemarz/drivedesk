from django.db import models


class TransactionLog(models.Model):
    STATUS_STARTED = "started"
    STATUS_PAID = "paid"
    STATUS_FAILED = "failed"

    PROVIDER_STRIPE = "stripe"
    PROVIDER_PAYPAL = "paypal"

    provider = models.CharField(max_length=24)
    status = models.CharField(max_length=24, default=STATUS_STARTED)
    external_id = models.CharField(max_length=140, blank=True)
    customer_name = models.CharField(max_length=160, blank=True)
    customer_email = models.EmailField(blank=True)
    items = models.JSONField(default=list, blank=True)
    amount_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=8, default="usd")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        label = self.external_id or f"transaction-{self.pk}"
        return f"{self.provider} {self.status} {label}"


class Coupon(models.Model):
    code = models.CharField(max_length=40, unique=True)
    percent_off = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} ({self.percent_off}% off)"

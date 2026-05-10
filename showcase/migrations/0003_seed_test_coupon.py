# Generated for DriveDesk test coupon seed.

from django.db import migrations


def create_test_coupon(apps, schema_editor):
    Coupon = apps.get_model("showcase", "Coupon")
    Coupon.objects.update_or_create(
        code="TEST30",
        defaults={"percent_off": 30, "is_active": True},
    )


def remove_test_coupon(apps, schema_editor):
    Coupon = apps.get_model("showcase", "Coupon")
    Coupon.objects.filter(code="TEST30").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("showcase", "0002_coupon"),
    ]

    operations = [
        migrations.RunPython(create_test_coupon, remove_test_coupon),
    ]

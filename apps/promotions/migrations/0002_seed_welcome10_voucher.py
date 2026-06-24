from django.db import migrations


def seed_welcome10(apps, schema_editor):
    Voucher = apps.get_model('promotions', 'Voucher')
    Voucher.objects.get_or_create(
        code='WELCOME10',
        defaults={
            'description': 'Diskon 10% untuk pembelian pertama kamu!',
            'discount_type': 'percentage',
            'discount_amount': 10,
            'min_purchase': 200000,
            'is_active': True,
        }
    )


def reverse_welcome10(apps, schema_editor):
    Voucher = apps.get_model('promotions', 'Voucher')
    Voucher.objects.filter(code='WELCOME10').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_welcome10, reverse_welcome10),
    ]

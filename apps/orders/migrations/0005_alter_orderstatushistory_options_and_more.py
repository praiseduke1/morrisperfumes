from django.db import migrations, models

STATUS_MAP = {
    'pending': 'pending_payment',
    'paid': 'paid',
    'processing': 'processing',
    'shipped': 'shipped',
    'completed': 'delivered',
    'cancelled': 'cancelled',
}


def migrate_order_status(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for old, new in STATUS_MAP.items():
        Order.objects.filter(status=old).update(status=new)


def migrate_history_status(apps, schema_editor):
    OrderStatusHistory = apps.get_model('orders', 'OrderStatusHistory')
    for obj in OrderStatusHistory.objects.all():
        obj.status = STATUS_MAP.get(obj.to_status, obj.to_status)
        obj.save(update_fields=['status'])


def reverse_migrate_order_status(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    reverse_map = {v: k for k, v in STATUS_MAP.items()}
    for new, old in reverse_map.items():
        Order.objects.filter(status=new).update(status=old)


def reverse_migrate_history_status(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_voucher_order_discount_amount_order_subtotal_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderstatushistory',
            options={'ordering': ['created_at'], 'verbose_name': 'Riwayat Status Pesanan', 'verbose_name_plural': 'Riwayat Status Pesanan'},
        ),
        migrations.AddField(
            model_name='orderstatushistory',
            name='status',
            field=models.CharField(blank=True, choices=[('pending_payment', 'Pending Payment'), ('paid', 'Paid'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default=None, max_length=20, null=True, verbose_name='Status'),
        ),
        migrations.RunPython(migrate_history_status, reverse_migrate_history_status),
        migrations.RemoveField(
            model_name='orderstatushistory',
            name='changed_by',
        ),
        migrations.RemoveField(
            model_name='orderstatushistory',
            name='from_status',
        ),
        migrations.RemoveField(
            model_name='orderstatushistory',
            name='to_status',
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pending_payment', 'Pending Payment'), ('paid', 'Paid'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending_payment', max_length=20, verbose_name='Status'),
        ),
        migrations.RunPython(migrate_order_status, reverse_migrate_order_status),
    ]

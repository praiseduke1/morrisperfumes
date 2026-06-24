import uuid

from django.db import migrations, models


def backfill_midtrans_order_id(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    for order in Order.objects.filter(midtrans_order_id__isnull=True):
        order.midtrans_order_id = uuid.uuid4()
        order.save(update_fields=['midtrans_order_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_province'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='midtrans_order_id',
            field=models.UUIDField(null=True, verbose_name='ID Midtrans'),
        ),
        migrations.RunPython(backfill_midtrans_order_id, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='midtrans_order_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='ID Midtrans'),
        ),
    ]

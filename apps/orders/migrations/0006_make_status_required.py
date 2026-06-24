from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_orderstatushistory_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstatushistory',
            name='status',
            field=models.CharField(choices=[('pending_payment', 'Pending Payment'), ('paid', 'Paid'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], max_length=20, verbose_name='Status'),
        ),
    ]

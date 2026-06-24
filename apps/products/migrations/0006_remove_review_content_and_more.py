from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_fragrancefamily_product_fragrance_families'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='is_verified_purchase',
        ),
        migrations.RemoveField(
            model_name='review',
            name='title',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='content',
            new_name='comment',
        ),
    ]

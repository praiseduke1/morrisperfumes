from django.db import migrations


def migrate_profile_addresses(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('accounts', 'Profile')
    CustomerAddress = apps.get_model('accounts', 'CustomerAddress')

    for user in User.objects.all():
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            continue

        if not profile.address or not profile.address.strip():
            continue

        if CustomerAddress.objects.filter(user=user).exists():
            continue

        full_name = f'{user.first_name} {user.last_name}'.strip()
        if not full_name:
            full_name = user.username

        CustomerAddress.objects.create(
            user=user,
            label='Rumah',
            recipient_name=full_name,
            phone=profile.phone,
            address=profile.address,
            is_default=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_address_system_refactor'),
    ]

    operations = [
        migrations.RunPython(migrate_profile_addresses, migrations.RunPython.noop),
    ]

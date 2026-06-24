from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create superuser admin/admin123'

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(username='admin').exists():
            self.stdout.write('  ~ Superuser admin already exists')
            return

        User.objects.create_superuser(
            username='admin',
            email='admin@parfumoray.com',
            password='admin123',
        )
        self.stdout.write(self.style.SUCCESS('  + Superuser admin created (admin/admin123)'))

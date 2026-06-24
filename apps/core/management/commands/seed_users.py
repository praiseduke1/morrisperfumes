from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

CUSTOMERS = [
    {'username': 'budi', 'email': 'budi@example.com', 'password': 'customer123'},
    {'username': 'siti', 'email': 'siti@example.com', 'password': 'customer123'},
    {'username': 'andi', 'email': 'andi@example.com', 'password': 'customer123'},
]


class Command(BaseCommand):
    help = 'Create sample customer accounts'

    def handle(self, *args, **options):
        User = get_user_model()
        created_count = 0
        for data in CUSTOMERS:
            if User.objects.filter(username=data['username']).exists():
                self.stdout.write(f'  ~ Customer {data["username"]} already exists')
                continue
            User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
            )
            self.stdout.write(f'  + Customer {data["username"]} created')
            created_count += 1

        if created_count:
            self.stdout.write(self.style.SUCCESS(f'  Created {created_count} customer(s)'))
        else:
            self.stdout.write('  No new customers created')

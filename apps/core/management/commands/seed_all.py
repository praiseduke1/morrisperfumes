from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run all seeders in correct dependency order'

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('SEED_ALL — Memulai seeding lengkap')
        self.stdout.write('=' * 50)

        steps = [
            ('seed_admin', 'Superuser'),
            ('seed_users', 'Customer accounts'),
            ('seed_indonesia_regions', 'Regions (prov/kota/kec/kodepos)'),
            ('seed_data', 'Categories, products, vouchers'),
        ]

        for command_name, label in steps:
            self.stdout.write(f'\n--- {label} ---')
            try:
                call_command(command_name)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  FAILED: {e}'))

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('SEED_ALL selesai'))
        self.stdout.write('=' * 50)

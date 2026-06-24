from django.core.management.commands.makemigrations import Command as MakeMigrationsCommand
from apps.core.backup import backup_database


class Command(MakeMigrationsCommand):
    help = 'Auto-backup database before making migrations'

    def handle(self, *args, **options):
        backup_database()
        super().handle(*args, **options)

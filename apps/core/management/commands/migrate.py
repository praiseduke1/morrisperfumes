from django.core.management.commands.migrate import Command as MigrateCommand
from apps.core.backup import backup_database


class Command(MigrateCommand):
    help = 'Auto-backup database before running migrations'

    def handle(self, *args, **options):
        backup_database()
        super().handle(*args, **options)

import datetime
import os
import shutil

BACKUP_DIR = 'backups'
DB_PATH = 'db.sqlite3'


def get_backup_path():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(BACKUP_DIR, f'db_backup_{timestamp}.sqlite3')


def backup_database():
    if not os.path.exists(DB_PATH):
        print(f'[BACKUP] Database file not found: {DB_PATH}. Skipping backup.')
        return None
    dest = get_backup_path()
    try:
        shutil.copy2(DB_PATH, dest)
        size_mb = os.path.getsize(dest) / (1024 * 1024)
        print(f'[BACKUP] Database backed up to: {dest} ({size_mb:.1f} MB)')
        return dest
    except Exception as e:
        print(f'[BACKUP] FAILED: {e}')
        raise


def restore_backup(backup_path):
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f'Backup not found: {backup_path}')
    shutil.copy2(backup_path, DB_PATH)
    print(f'[RESTORE] Restored: {backup_path} → {DB_PATH}')


def list_backups():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith('db_backup_') and f.endswith('.sqlite3')],
        reverse=True
    )
    return backups

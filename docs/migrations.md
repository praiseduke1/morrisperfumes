# Migration Safety Guide

## Prosedur Migrasi Aman

### Sebelum Migrasi

```bash
# Backup otomatis (dijalankan oleh custom manage.py migrate/makemigrations)
python manage.py migrate --plan   # Lihat perubahan tanpa menjalankan
python manage.py migrate          # Backup + execute
```

### Menambahkan Field Baru

#### Field biasa (nullable, tanpa unique)
```python
# models.py
field = models.CharField(max_length=100, blank=True, default='')

# migration aman: AddField langsung
```

#### Field UNIQUE dengan data existing
```python
# models.py — JANGAN langsung unique=True
field = models.UUIDField(null=True)  # Sementara

# Migration: 3-step strategy
# Step 1: AddField(null=True)
# Step 2: RunPython backfill unique values
# Step 3: AlterField(unique=True, null=False)
```

#### Mengubah tipe kolom
```bash
# JANGAN lakukan langsung
# Buat backup dulu
python manage.py migrate --plan
# Verifikasi tidak ada loss of data
```

### Rollback Migration

```bash
# Lihat history
python manage.py showmigrations

# Rollback satu migration
python manage.py migrate <app_name> <previous_migration>

# Contoh: rollback orders dari 0009 ke 0008
python manage.py migrate orders 0008
```

## Larangan

| Larangan | Alasan |
|----------|--------|
| `DROP TABLE` | Data hilang permanen |
| `DELETE FROM <table>` tanpa backup | Data hilang |
| `migrate --fake` tanpa verifikasi | State tidak sinkron |
| `makemigrations --merge` tanpa review | Konflik tidak terdeteksi |
| Edit migration yang sudah di-commit | History rusak |

## Auto-Backup

Sejak implementasi safety policy, `python manage.py migrate` dan `makemigrations` otomatis membuat backup ke `backups/db_backup_*.sqlite3` sebelum menjalankan operasi.

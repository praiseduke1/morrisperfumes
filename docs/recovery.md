# Database Recovery Guide

## Jika Database Rusak

### Step 1: Jangan Panik
**JANGAN** menghapus `db.sqlite3`. JANGAN migrate ulang dari nol.

### Step 2: Cek Backup

```bash
python -c "
import os; from apps.core.backup import list_backups
for b in list_backups():
    size = os.path.getsize(f'backups/{b}')
    print(f'{b} ({size/1024:.0f} KB)')
"
```

### Step 3: Restore dari Backup

```bash
python -c "
from apps.core.backup import restore_backup
restore_backup('backups/db_backup_20260623_*.sqlite3')
"
```

Ganti `*` dengan timestamp backup yang diinginkan.

### Step 4: Jika Tidak Ada Backup

Gunakan seeder untuk recover data:

```bash
# Semua data
python manage.py seed_all

# Atau step-by-step
python manage.py seed_admin          # Superuser admin/admin123
python manage.py seed_users          # Customer budi, siti, andi
python manage.py seed_indonesia_regions  # 38 prov, 521 kota, dll
python manage.py seed_data           # 5 kategori, 12 produk, 4 voucher
```

Semua seeder **idempotent** — aman dijalankan berulang.

## Data yang Dikembalikan oleh Seeder

| Seeder | Data |
|--------|------|
| `seed_admin` | Superuser `admin` / `admin123` |
| `seed_users` | 3 customer: `budi`, `siti`, `andi` (password: `customer123`) |
| `seed_indonesia_regions` | 38 provinsi, 521 kota, 654 kecamatan, 252 kode pos |
| `seed_data` | 5 fragrance families, 5 categories, 12 produk Morris, 4 voucher |

## Verification

```bash
# Cek semua data
python manage.py seed_all  # Idempotent — tidak bikin duplikat

# Cek manual
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()
4
>>> from apps.products.models import Product
>>> Product.objects.count()
12
```

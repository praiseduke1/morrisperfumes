# Database Safety Policy

## Larangan Mutlak

DILARANG melakukan hal berikut tanpa konfirmasi user:

1. **Menghapus `db.sqlite3`** — dalam keadaan apapun
2. **Menghapus database** (drop database, `DROP TABLE`, dll)
3. **Menghapus migration files** (`rm apps/*/migrations/0*.py`)
4. **`migrate --fake` tanpa memahami state aktual**
5. **Migrate dari nol** (`migrate` setelah hapus semua tabel)

## Prosedur Aman Saat Migrasi Gagal

```
┌─────────────────────────────────────────┐
│  Migrasi gagal                          │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  1. Backup database otomatis            │
│     backups/db_backup_YYYYMMDD_HHMMSS   │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  2. Analisis error message              │
│     - Baca traceback lengkap            │
│     - Identifikasi operasi mana gagal   │
│     - Cek constraint/schema conflict    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  3. Tawarkan solusi ke user             │
│     - Solusi A: Rollback + perbaiki     │
│     - Solusi B: Fake + manual fix       │
│     - Solusi C: Backup + restore        │
│     JANGAN ambil keputusan sendiri      │
└─────────────────────────────────────────┘
```

## Checklist Migrasi Aman

Sebelum `makemigrations` atau `migrate`:

- [ ] Backup database (`backups/db_backup_*.sqlite3`)
- [ ] Apakah migration menambahkan `unique=True` ke tabel existing?
- [ ] Jika ya: gunakan 3-step strategy (null → backfill → alter)
- [ ] Apakah migration mengubah tipe kolom?
- [ ] Apakah migration menghapus kolom?
- [ ] Apakah ada data di tabel yang dimodifikasi?

## Recovery Plan

Jika database rusak:

1. **Jangan panik, jangan hapus apa pun**
2. Cari backup terbaru di `backups/`
3. Copy backup: `copy backups/db_backup_*.sqlite3 db.sqlite3`
4. Laporkan ke user
5. Analisis penyebab sebelum mencoba lagi

# DEVELOPMENT_RULES.md

> Dokumen ini berisi aturan yang WAJIB dipatuhi oleh AI/developer saat melakukan coding pada proyek Parfum Morris.
> Anggap sebagai **single source of truth** untuk pengembangan.

---

## 1. Prinsip Umum

### 1.1 Jangan Mengubah Arsitektur Tanpa Alasan Kuat
- Struktur Django apps (core, accounts, products, carts, orders, payments, promotions) sudah dirancang dengan separation of concerns.
- Jika ingin menambah fitur baru, evaluasi app mana yang paling bertanggung jawab.
- Jangan memindahkan model/view/URL antar app tanpa diskusi.

### 1.2 Jangan Menghapus Fitur Lama
- Semua fitur yang sudah berjalan dan lulus test TIDAK boleh dihapus.
- Jika ada perubahan yang mempengaruhi fitur lama, pastikan backward compatibility.

### 1.3 Analisis Kode Sebelum Perubahan
- **WAJIB** membaca file yang akan diubah minimal 1 kali sebelum melakukan edit.
- Pahami konteks dan dependencies file tersebut.
- Cek import dan relasi yang terpengaruh.

### 1.4 Single Source of Truth (SSOT)
- **DATABASE_SCHEMA.md** = satu-satunya referensi untuk semua model dan field.
- **PROJECT_CONTEXT.md** = gambaran umum proyek, tujuan, dan prinsip.
- **FEATURES.md** = status fitur.
- **DEVELOPMENT_RULES.md** = aturan coding.
- Jangan duplikasi informasi model di file docs lain.

---

## 2. Database

### 2.1 Migration
- Setiap perubahan pada model **WAJIB** menggunakan migration.
- Jalankan `python manage.py makemigrations` setelah ubah model.
- Jalankan `python manage.py migrate` sebelum testing.
- Jangan mengedit migration yang sudah diaplikasi (kecuali untuk squash).

### 2.2 SQLite Compatibility
- Gunakan field yang didukung SQLite (semua field Django standar aman).
- Hindari database-specific features (PostgreSQL array field, MySQL fulltext, dll).
- Jangan gunakan `CONCAT` atau fungsi database spesifik di query.

### 2.3 Query Optimization
- Gunakan `select_related` untuk ForeignKey/OneToOne yang selalu diakses.
- Gunakan `prefetch_related` untuk ManyToMany dan reverse ForeignKey.
- Hindari N+1 query dengan inspect logs/debug toolbar.
- Gunakan `.only()` / `.defer()` jika hanya perlu sebagian field (untuk performa).

---

## 3. Django Best Practice

### 3.1 Models
- Gunakan `class Meta` dengan `verbose_name` dan `verbose_name_plural` dalam Bahasa Indonesia.
- Gunakan `TextChoices` atau `IntegerChoices` untuk field dengan pilihan tetap.
- Beri `related_name` eksplisit pada setiap ForeignKey/OneToOneField.
- Gunakan `__str__` yang informatif.

### 3.2 Views
- Gunakan **Class-Based Views** untuk halaman publik (ListView, DetailView, TemplateView, CreateView, UpdateView).
- Gunakan **Function-Based Views** dengan `@login_required` untuk halaman terproteksi (cart, orders, payments).
- Selalu validasi kepemilikan resource (user hanya bisa akses order/payment miliknya sendiri).

### 3.3 URLs
- Gunakan `app_name` untuk setiap app URLs.
- Gunakan named URL patterns (jangan hardcode URL di template).
- URL parameter harus jelas (slug untuk produk, id untuk order/payment).

### 3.4 Forms
- Gunakan Django Forms untuk validasi input.
- Jangan pernah percaya input user, validasi di server side.
- Gunakan `ModelForm` jika form berhubungan langsung dengan model.

### 3.5 Admin
- Daftarkan semua model di admin.
- Gunakan `@admin.register()` decorator.
- Sediakan `search_fields`, `list_filter`, `list_display` yang berguna.
- Gunakan `filter_horizontal` untuk ManyToMany field.
- Jangan expose field sensitif.

---

## 4. Frontend (Tailwind CSS)

### 4.1 Styling
- Semua tampilan menggunakan **Tailwind CSS via CDN** — jangan tambah CSS custom kecuali darurat.
- Gunakan utility classes, jangan buat custom CSS file baru.
- Gunakan color palette Morris + Gold yang sudah didefinisikan di `base.html` tailwind.config.
- Morris palette: `morris-50` s.d. `morris-950`, `gold-400`, `gold-500`, `gold-600`.
- Font: `Playfair Display` untuk heading (serif), `Inter` untuk body (sans-serif).

### 4.2 WCAG AA Color Contrast Compliance
- **WAJIB** pastikan semua teks memenuhi WCAG AA (minimum 4.5:1 untuk teks normal, 3:1 untuk teks besar).
- Palmer referensi kontras:
  - `text-white` on `morris-950` (#261f1b) = 14.6:1 ✅
  - `text-gold-400` (#d4a853) on `morris-950` = 5.3:1 ✅
  - `text-morris-400` (#ab9379) on `morris-950` = 4.3:1 ✅
  - `text-morris-500` (#967b60) on `morris-950` = 3.4:1 ❌ (jangan pakai)
- Jangan gunakan semi-transparent background (e.g., `bg-morris-800/50`) untuk card yang menampung teks putih — teks menjadi tidak terbaca.

### 4.3 Templates
- Template inheritance dari `base.html`.
- Gunakan komponen reusable di `templates/includes/`.
- Blok yang tersedia di base.html: `title`, `content`, `extra_scripts`, `extra_head`, `meta_description`, `meta_keywords`, `og_title`, `og_description`.
- Gunakan template tags: `rupiah`, `query_transform`, `cart_count`.

### 4.4 Responsive
- Semua halaman harus mobile responsive.
- Gunakan breakpoint Tailwind: `sm:`, `md:`, `lg:`, `xl:`.
- Test di viewport mobile (320px - 428px) dan desktop (1280px+).

---

## 5. Keamanan

### 5.1 Environment Variables
- Semua data sensitif **WAJIB** via environment variable di `.env`.
- Jangan hardcode secret key, database password, API key di kode.
- File .env jangan di-commit ke repository (sudah di .gitignore).

### 5.2 Authentication
- Halaman cart, orders, payments **WAJIB** `@login_required`.
- Gunakan `get_object_or_404` dengan filter `user=request.user`.
- Login URL: `accounts:login`.

### 5.3 Role Separation (Admin vs Customer)
- Superuser (`is_superuser=True`) **DILARANG** mengakses fitur customer:
  - Cart (add, update, remove, detail)
  - Orders (create, detail, list, cancel)
  - Payments (checkout, finish, unfinish, error)
  - Dashboard customer & profile update
  - Wishlist
- Gunakan decorator `@customer_required` dari `apps.core.decorators` untuk FBV.
- Gunakan `CustomerRequiredMixin` dari `apps.core.mixins` untuk CBV.
- Keduanya akan redirect superuser ke `/admin/` dengan pesan warning.
- Di frontend: sembunyikan tombol cart/checkout/dashboard untuk superuser.
- Tampilkan banner "Anda login sebagai Administrator" dengan link ke Admin Panel.
- Decorator `@customer_required` dipasang **setelah** `@login_required`.

### 5.4 Midtrans Security
- **WAJIB** verifikasi HMAC signature di callback.
- **WAJIB** validasi gross_amount match.
- Jangan expose `MIDTRANS_SERVER_KEY` di frontend (hanya `MIDTRANS_CLIENT_KEY`).
- Gunakan server key hanya di server-side (notification handler).

### 5.5 Payment
- **WAJIB** cek `was_paid_before` sebelum decrement stok (anti double-decrement).
- **WAJIB** validasi order ownership sebelum checkout.
- Jangan proses callback yang signature-nya tidak valid.

---

## 6. Testing

### 6.1 pytest
- Semua test menggunakan pytest + pytest-django.
- Setiap test class harus decorator `@pytest.mark.django_db`.
- Test coverage minimal untuk model, form, dan view.

### 6.2 Sebelum Commit/Push
- Jalankan `python -m pytest` — pastikan semua test lulus (saat ini 85+ tests).
- Jika ada test baru yang belum dibuat, buat minimal test untuk skenario utama.

---

## 7. Code Style

### 7.1 Python
- Ikuti PEP 8.
- Gunakan import ordering: standard library → Django → third-party → local apps.
- Jangan tambahkan komentar yang tidak perlu.

### 7.2 HTML/Templates
- Gunakan 4 spaces indentation (bukan tabs).
- Format tag dengan rapi.

### 7.3 Naming Convention
- Model: PascalCase (Product, Category, FragranceNote).
- Fields: snake_case (note_type, order_number, total_price).
- Views: PascalCase untuk CBV (ProductDetailView), snake_case untuk FBV (order_create).
- URLs: snake_case (product_list, by_note, order_detail).
- Templates: snake_case (product_detail.html, order_list.html).

---

## 8. Version Control

- Jangan commit file .env, db.sqlite3, __pycache__, .pyc.
- Jangan commit media files (kecuali sample/default).
- Tulis commit message yang deskriptif.

---

## 9. Database Safety (WAJIB)

### 9.1 Larangan Mutlak
DILARANG melakukan hal berikut **tanpa konfirmasi user**:
- **Menghapus `db.sqlite3`** dalam keadaan apapun
- **Menghapus database** (drop, truncate, delete all rows)
- **Menghapus migration files**
- **Migrate dari nol** (rollback semua migration)

### 9.2 Jika Migrasi Gagal
1. **Backup dulu** — backup otomatis dibuat oleh custom migrate/makemigrations
2. **Analisis error** — baca traceback, identifikasi operasi mana yang gagal
3. **Tawarkan solusi** — berikan opsi ke user, minta persetujuan
4. **Jangan bertindak sendiri** — terutama jangan hapus database

### 9.3 Menambahkan Field UNIQUE
Untuk field `unique=True` dengan data existing:
1. Tambah field dengan `null=True` (tanpa unique)
2. `RunPython` untuk backfill nilai unik
3. `AlterField` + `unique=True` + `null=False`

JANGAN pernah `AddField(unique=True)` langsung dengan callable default.

### 9.4 Auto-Backup
Setiap `python manage.py migrate` atau `makemigrations` otomatis backup ke `backups/db_backup_*.sqlite3`. Jika backup gagal, proses dibatalkan.

---

## 10. Jika Ragu

- Baca dokumentasi di `docs/` sebelum memulai task.
- Cari kode serupa yang sudah ada di codebase sebagai referensi.
- Tanya user jika ada keputusan arsitektur yang perlu dikonfirmasi.

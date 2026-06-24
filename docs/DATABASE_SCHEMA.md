# DATABASE_SCHEMA.md

> Single source of truth for all database models, fields, and relationships.

## Diagram Relasi Database

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                      │
│  ┌──────────┐     ┌──────────────────┐     ┌─────────────┐      ┌──────────────┐    │
│  │  User    │     │  Profile         │     │  Category   │      │ Fragrance    │    │
│  │──────────│     │──────────────────│     │─────────────│      │ Family       │    │
│  │ id (PK)  │◄────│ user_id (PK,FK)  │     │ id (PK)     │      │──────────────│    │
│  │ username │     │ phone            │     │ name        │      │ id (PK)      │    │
│  │ email    │     │ address          │     │ slug(unique)│      │ name         │    │
│  │ password │     │ created_at       │     │ description │      │ slug (unique)│    │
│  └────┬─────┘     │ updated_at       │     └──────┬──────┘      │ description  │    │
│       │           └──────────────────┘            │             └──────┬───────┘    │
│       │                                           │                    │            │
│       │  ┌──────────────────┐    ┌─────────────────┴──────┐           │            │
│       ├──│  Cart            │    │  Product               │           │            │
│       │  │──────────────────│    │────────────────────────│           │            │
│       │  │ user_id (PK,FK)  │    │ id (PK)                │           │            │
│       │  │ created_at       │    │ category_id (FK) ──────┼───────────┘            │
│       │  │ updated_at       │    │ brand_id (FK) ─────────┼─┐                      │
│       │  └────────┬─────────┘    │ name                   │ │                      │
│       │           │              │ slug (unique)          │ │                      │
│       │  ┌────────┴──────────┐   │ description            │ │                      │
│       │  │  CartItem         │   │ price                  │ │                      │
│       │  │───────────────────│   │ stock                  │ │     ┌────────────┐   │
│       │  │ id (PK)           │   │ image                  │ │     │  Brand     │   │
│       │  │ cart_id (FK)──────┼───│ is_available           │ │     │────────────│   │
│       │  │ product_id (FK)───┼─┐ │ gender_target          │ │     │ id (PK)    │   │
│       │  │ variant_id (FK)───┼─┼─│ occasion               │ │     │ name       │   │
│       │  │ quantity          │ │ │ sillage                │ │     │ slug (uni) │   │
│       │  │ unique: cart+prod │ │ │ longevity              │ │     │ description│   │
│       │  │       +variant    │ │ │ season                 │ │     │ logo       │   │
│       │  └───────────────────┘ │ │ fragrance_families(M2M)─┼──────┘ created_at  │   │
│       │                        │ │ created_at             │ │     │ updated_at │   │
│       │  ┌──────────────────┐  │ │ updated_at             │ │     └────────────┘   │
│       ├──│  Order           │  │ └────────────────────────┘ │                      │
│       │  │──────────────────│  │                            │                      │
│       │  │ id (PK)          │  │  ManyToMany                │                      │
│       │  │ user_id (FK)     │  │                            │                      │
│       │  │ order_number     │  │  ┌────────────────────┐   │                      │
│       │  │ (unique, auto)   │  │  │  FragranceNote    │   │                      │
│       │  │ status           │  │  │───────────────────│   │                      │
│       │  │ subtotal         │  │  │ id (PK)           │   │                      │
│       │  │ discount_amount  │  │  │ name              │   │                      │
│       │  │ total_price      │  │  │ note_type         │   │                      │
│       │  │ voucher (FK)     │  │  │ slug (unique)     │   │                      │
│       │  │ recipient_name   │  │  │ description       │   │                      │
│       │  │ phone            │  │  │ created_at        │   │                      │
│       │  │ shipping_address │  │  │ updated_at        │   │                      │
│       │  │ city             │  │  └───────────────────┘   │                      │
│       │  │ postal_code      │  │                           │                      │
│       │  │ notes            │  │  ┌────────────────────┐   │                      │
│       │  │ created_at       │  │  │  ProductVariant   │   │                      │
│       │  │ updated_at       │  │  │───────────────────│   │                      │
│       │  └────────┬─────────┘  │  │ id (PK)           │   │                      │
│       │           │            │  │ product_id (FK)────┼───┘                      │
│       │  ┌────────┴──────────┐ │  │ size_ml           │                           │
│       │  │  OrderItem        │ │  │ price             │                           │
│       │  │───────────────────│ │  │ stock             │                           │
│       │  │ id (PK)           │ │  │ sku               │                           │
│       │  │ order_id (FK)─────┼─┘  │ is_available      │                           │
│       │  │ product_id (FK)───┼─┐  │ unique: prod+size │                           │
│       │  │ product_name      │ │  └───────────────────┘                           │
│       │  │ variant_name      │ │                                                 │
│       │  │ price             │ │  ┌────────────────────┐                         │
│       │  │ quantity          │ │  │  ProductImage      │                         │
│       │  └───────────────────┘ │  │───────────────────│                         │
│       │                        │  │ id (PK)           │                         │
│       │  ┌──────────────────┐  │  │ product_id (FK)────┼─────────────────────────┘
│       │  │  OrderStatus     │  │  │ image             │                         │
│       │  │  History         │  │  │ alt_text          │                         │
│       │  │──────────────────│  │  │ is_primary        │                         │
│       │  │ id (PK)          │  │  │ sort_order        │                         │
│       │  │ order_id (FK)────┼──┘  └───────────────────┘                         │
│       │  │ from_status      │                                                   │
│       │  │ to_status        │  ┌────────────────────┐                           │
│       │  │ changed_by       │  │  Review            │                           │
│       │  │ notes            │  │───────────────────│                           │
│       │  │ created_at       │  │ id (PK)           │                           │
│       │  └──────────────────┘  │ product_id (FK)────┼───────────────────────────┘
│       │                        │ user_id (FK) ──────┼────┐                      │
│       │  ┌──────────────────┐  │ rating             │    │                      │
│       ├──│  CustomerAddress │  │ comment            │    │                      │
│       │  │──────────────────│  │ created_at         │    │                      │
│       │  │ id (PK)          │  │ updated_at         │    │                      │
│       │  │ user_id (FK) ────┼──┘ unique: prod+user │    │                      │
│       │  │ label            │  └────────────────────┘    │                      │
│       │  │ recipient_name   │                            │                      │
│       │  │ phone            │  ┌────────────────────┐   │                      │
│       │  │ address          │  │  Wishlist          │   │                      │
│       │  │ city             │  │───────────────────│   │                      │
│       │  │ postal_code      │  │ id (PK)           │   │                      │
│       │  │ is_default       │  │ user_id (FK) ──────┼───┘                      │
│       │  │ created_at       │  │ product_id (FK)────┼──────────────────────────┘
│       │  └──────────────────┘  │ variant_id (FK)   │                           │
│       │                        │ unique:            │                           │
│       │  ┌──────────────────┐  │   user+prod+var   │                           │
│       ├──│  Payment         │  │ created_at         │                           │
│       │  │──────────────────│  └────────────────────┘                           │
│       │  │ id (PK)          │                                                   │
│       │  │ order_id (FK) ◄──┼───(OneToOne)                                     │
│       │  │ transaction_id   │                                                   │
│       │  │ snap_token       │  ┌────────────────────┐                           │
│       │  │ snap_redirect_url│  │  Voucher           │                           │
│       │  │ payment_method   │  │  (orders)          │                           │
│       │  │ amount           │  │───────────────────│                           │
│       │  │ status           │  │ id (PK)           │                           │
│       │  │ fraud_status     │  │ code (unique)     │                           │
│       │  │ payment_time     │  │ discount_type     │                           │
│       │  │ raw_response     │  │ discount_amount   │                           │
│       │  │ (JSON)           │  │ min_purchase      │                           │
│       │  │ created_at       │  │ max_discount      │                           │
│       │  │ updated_at       │  │ max_uses          │                           │
│       │  └────────┬─────────┘  │ used_count        │                           │
│       │           │            │ is_active         │                           │
│       │  ┌────────┴──────────┐│ valid_from        │                           │
│       │  │  PaymentStatus    ││ valid_until       │                           │
│       │  │  History          ││ created_at        │                           │
│       │  │───────────────────││ updated_at        │                           │
│       │  │ id (PK)           ││                   │                           │
│       │  │ payment_id (FK)───┼└────────────────────┘                           │
│       │  │ from_status       │                                                   │
│       │  │ to_status         │  ┌────────────────────┐                           │
│       │  │ raw_response(JSON)│  │  Voucher           │                           │
│       │  │ created_at        │  │  (promotions)      │                           │
│       │  └───────────────────┘  │───────────────────│                           │
│       │                         │ id (PK)           │                           │
│       │  ┌──────────────────┐   │ code (unique)     │                           │
│       │  │  Voucher         │   │ description       │                           │
│       │  │  (promotions)    │   │ discount_type     │                           │
│       │  │──────────────────│   │ discount_amount   │                           │
│       │  │ id (PK)          │   │ min_purchase      │                           │
│       │  │ user_id (FK) ────┼───│ max_discount      │                           │
│       │  │ voucher (FK) ────┼───│ expired_date      │                           │
│       │  │ status           │   │ is_active         │                           │
│       │  │ assigned_at      │   │ created_at        │                           │
│       │  │ used_at          │   └────────────────────┘                           │
│       │  │ expires_at       │                                                   │
│       │  └──────────────────┘                                                   │
│       │                                                                         │
│       └─────────────────────────────────────────────────────────────────────────┘
```

---

## User (Django Built-in)

**Tujuan:** Model bawaan Django untuk autentikasi pengguna.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| username | CharField(150) | Username unik |
| email | EmailField | Email |
| password | CharField | Hashed password |
| first_name | CharField(150) | Nama depan |
| last_name | CharField(150) | Nama belakang |
| is_active | BooleanField | Status aktif |
| date_joined | DateTimeField | Tanggal registrasi |

**Relasi:**
- OneToOne → Profile (via `user.profile`)
- OneToOne → MemberProfile (via `user.member_profile`)
- OneToOne → Cart (via `user.cart`)
- OneToMany → Order (via `user.orders`)
- OneToMany → CustomerAddress (via `user.addresses`)
- OneToMany → Wishlist (via `user.wishlist_items`)
- OneToMany → Review (via `user.reviews`)
- OneToMany → UserVoucher (via `user.user_vouchers`)
- OneToMany → PointTransaction (via `user.point_transactions`)

---

## Profile

**Tujuan:** Menyimpan data tambahan pengguna (telepon). Alamat telah dipindahkan ke CustomerAddress.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | OneToOneField(User) | Relasi ke User |
| phone | CharField(20) | Nomor telepon |
| address | TextField | Alamat lengkap (deprecated — gunakan CustomerAddress) |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Relasi:**
- OneToOne → User (via `user`)

---

## MemberProfile

**Tujuan:** Menyimpan data membership dan loyalty (level, poin, total belanja) per pengguna.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | OneToOneField(User) | Relasi ke User |
| level | CharField(20) | Level: `SILVER`, `GOLD`, `PLATINUM` |
| total_points | PositiveIntegerField(default=0) | Total poin terkumpul |
| total_spending | DecimalField(14,0, default=0) | Total belanja seumur hidup |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Level Threshold:**
- SILVER: ≥ Rp 0 (default)
- GOLD: ≥ Rp 1.000.000
- PLATINUM: ≥ Rp 5.000.000

**Methods:**
- `upgrade_level()` — Naikkan level jika `total_spending` mencapai threshold.
- `earn_points(amount)` — Hitung poin berdasarkan level multiplier (1x Silver, 1.5x Gold, 2x Platinum).

**Relasi:**
- OneToOne → User (via `user`)

---

## PointTransaction

**Tujuan:** Riwayat transaksi poin (earn, redeem, level upgrade). Append-only.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | ForeignKey(User) | Pengguna |
| points | IntegerField | Jumlah poin (+ untuk earn, - untuk redeem) |
| type | CharField(10) | Tipe: `EARN`, `REDEEM`, `UPGRADE` |
| description | CharField(255) | Deskripsi transaksi |
| created_at | DateTimeField(auto_now_add) | Dibuat |

**Relasi:**
- ManyToOne → User (via `user`)

---

## Category

**Tujuan:** Mengelompokkan produk parfum berdasarkan kategori (misal: Eau de Parfum, Attar, Oil).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| name | CharField(100) | Nama kategori |
| slug | SlugField (unique) | Slug untuk URL |
| description | TextField | Deskripsi kategori |

**Relasi:**
- OneToMany → Product (via `category.products`)

---

## FragranceFamily

**Tujuan:** Mengelompokkan produk berdasarkan keluarga aroma (misal: Woody, Floral, Oriental).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| name | CharField(100) | Nama keluarga aroma |
| slug | SlugField (unique) | Slug untuk URL filtering |
| description | TextField | Deskripsi |

**Relasi:**
- ManyToMany → Product (via `fragrance_families`)

---

## FragranceNote

**Tujuan:** Master data aroma parfum. Satu aroma dapat digunakan oleh banyak produk, dan satu produk dapat memiliki banyak aroma.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| name | CharField(100) | Nama aroma (misal: Bergamot, Vanilla, Musk) |
| note_type | CharField(10) | Tipe: `TOP`, `MIDDLE`, `BASE` |
| slug | SlugField (unique) | Slug untuk URL filtering |
| description | TextField | Deskripsi karakter aroma |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Choices (note_type):**
- `TOP` — Top Notes (aroma awal yang langsung tercium)
- `MIDDLE` — Middle/Heart Notes (aroma utama setelah top notes menguap)
- `BASE` — Base Notes (aroma dasar yang bertahan lama)

**Relasi:**
- ManyToMany → Product (via `fragrance_notes`)

---

## Product

**Tujuan:** Data utama produk parfum yang dijual.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| category | ForeignKey(Category) | Kategori produk |
| brand | ForeignKey(Brand, null, blank, SET_NULL) | Merek produk (SET_NULL saat brand dihapus) |
| fragrance_notes | ManyToManyField(FragranceNote) | Aroma produk |
| fragrance_families | ManyToManyField(FragranceFamily) | Keluarga aroma |
| name | CharField(200) | Nama produk |
| slug | SlugField (unique) | Slug untuk URL detail |
| description | TextField | Deskripsi produk |
| price | DecimalField(12,0) | Harga dasar produk |
| stock | PositiveIntegerField(default=0) | Stok dasar (fallback tanpa varian) |
| image | ImageField(null, blank) | Gambar utama produk |
| is_available | BooleanField(default=True) | Status tersedia |
| gender_target | CharField(10) | Target: `men`, `women`, `unisex` |
| occasion | CharField(10) | Kesempatan: `daily`, `office`, `casual`, `formal`, `evening` |
| sillage | CharField(10) | Keharuman: `intimate`, `moderate`, `heavy` |
| longevity | CharField(10) | Daya tahan: `short`, `moderate`, `long`, `very_long` |
| season | CharField(10) | Musim: `spring`, `summer`, `fall`, `winter`, `all` |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Choices untuk new Morris fields:**

**Gender:**
- `men` — For Men
- `women` — For Women
- `unisex` — Unisex (default)

**Occasion:**
- `daily` — Daily (default)
- `office` — Office
- `casual` — Casual
- `formal` — Formal
- `evening` — Evening

**Sillage:**
- `intimate` — Intimate
- `moderate` — Moderate (default)
- `heavy` — Heavy

**Longevity:**
- `short` — 1–3 hours
- `moderate` — 3–6 hours (default)
- `long` — 6–9 hours
- `very_long` — 9+ hours

**Season:**
- `spring` — Spring
- `summer` — Summer
- `fall` — Fall
- `winter` — Winter
- `all` — All Season (default)

**Methods:**
- `has_variants()` — Apakah produk punya varian ukuran.
- `min_price()` — Harga termurah dari semua varian (atau 0 jika tidak ada varian).
- `total_stock()` — Total stok dari semua varian.

**Relasi:**
- ManyToOne → Category (via `category`)
- ManyToOne → Brand (via `brand`)
- ManyToMany → FragranceNote (via `fragrance_notes`)
- ManyToMany → FragranceFamily (via `fragrance_families`)
- OneToMany → ProductVariant (via `variants`)
- OneToMany → ProductImage (via `images`)
- OneToMany → Review (via `reviews`)
- OneToMany → CartItem (via `cart_items`)
- OneToMany → OrderItem (via `order_items`)

---

## Brand

**Tujuan:** Master data merek parfum (3NF — memisahkan brand dari Product).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| name | CharField(100) | Nama merek |
| slug | SlugField (unique) | Slug untuk URL |
| description | TextField | Deskripsi merek |
| logo | ImageField(null, blank, upload_to='brands/') | Logo merek |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Relasi:**
- OneToMany → Product (via `product_set`)

---

## ProductVariant

**Tujuan:** Varian ukuran produk (misal: 30ml, 50ml, 100ml) dengan harga dan stok masing-masing.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| product | ForeignKey(Product) | Produk induk |
| size_ml | PositiveIntegerField | Ukuran dalam mililiter |
| price | DecimalField(12,0) | Harga varian |
| stock | PositiveIntegerField(default=0) | Stok varian |
| sku | CharField(50, blank, unique) | SKU unik varian |
| is_available | BooleanField(default=True) | Status tersedia |

**Constraints:**
- `unique_together = ['product', 'size_ml']` — Satu ukuran hanya sekali per produk.

**Relasi:**
- ManyToOne → Product (via `product`)
- OneToMany → CartItem (via `cartitem_set`, nullable)
- OneToMany → Wishlist (via `wishlist_set`, nullable)

---

## ProductImage

**Tujuan:** Galeri gambar per produk (multiple images dengan urutan).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| product | ForeignKey(Product) | Produk induk |
| image | ImageField | File gambar |
| alt_text | CharField(200, blank) | Teks alternatif |
| is_primary | BooleanField(default=False) | Gambar utama |
| sort_order | PositiveIntegerField(default=0) | Urutan tampil |

**Relasi:**
- ManyToOne → Product (via `product`)

---

## Review

**Tujuan:** Rating dan ulasan produk per pengguna.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| product | ForeignKey(Product) | Produk diulas |
| user | ForeignKey(User) | Pemberi ulasan |
| rating | PositiveSmallIntegerField | Rating 1-5 |
| comment | TextField(blank) | Komentar ulasan |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Constraints:**
- `unique_together = ['product', 'user']` — Satu user hanya bisa memberi satu rating per produk.

**Methods:**
- `has_purchased_product()` — Cek apakah user sudah pernah membeli produk ini (via OrderItem dengan status completed/paid).

**Relasi:**
- ManyToOne → Product (via `product`)
- ManyToOne → User (via `user`)

---

## Cart

**Tujuan:** Menyimpan keranjang belanja per pengguna. Setiap user hanya memiliki satu keranjang.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | OneToOneField(User) | Pemilik keranjang |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Methods:**
- `total_price()` — Jumlah harga semua item
- `total_items()` — Jumlah total quantity semua item

**Relasi:**
- OneToOne → User (via `user`)
- OneToMany → CartItem (via `items`)

---

## CartItem

**Tujuan:** Menyimpan item dalam keranjang belanja.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| cart | ForeignKey(Cart) | Keranjang induk |
| product | ForeignKey(Product) | Produk |
| variant | ForeignKey(ProductVariant, null, blank, CASCADE) | Varian ukuran (nullable, ikut terhapus jika varian dihapus) |
| quantity | PositiveIntegerField(default=1) | Jumlah |

**Constraints:**
- `unique_together = ['cart', 'product', 'variant']` — Satu produk+varian hanya sekali per keranjang. Variant null diperlakukan sebagai kombinasi unik terpisah.

**Methods:**
- `unit_price()` — Harga dari variant jika ada, atau product.price.
- `total_price()` — `unit_price() * quantity`

**Relasi:**
- ManyToOne → Cart (via `cart`)
- ManyToOne → Product (via `product`)
- ManyToOne → ProductVariant (via `variant`, nullable)

---

## Order

**Tujuan:** Menyimpan data pesanan setelah checkout.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | ForeignKey(User) | Pembeli |
| order_number | CharField(30, unique, auto) | Nomor pesanan: `ORD-YYYYMMDD-XXXXXX` |
| status | CharField(20) | Status: `pending_payment`, `paid`, `processing`, `shipped`, `delivered`, `cancelled` |
| subtotal | DecimalField(12,0) | Subtotal sebelum diskon |
| discount_amount | DecimalField(12,0, default=0) | Nilai diskon |
| total_price | DecimalField(12,0) | Total harga final (subtotal - discount) |
| voucher | ForeignKey('orders.Voucher', null, SET_NULL) | Voucher yang digunakan |
| recipient_name | CharField(100) | Nama penerima |
| phone | CharField(20) | Nomor telepon penerima |
| shipping_address | TextField | Alamat pengiriman |
| city | CharField(100) | Kota |
| province | CharField(100) | Provinsi |
| postal_code | CharField(10) | Kode pos |
| notes | TextField | Catatan pesanan |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Status Flow:**
```
PENDING_PAYMENT → PAID → PROCESSING → SHIPPED → DELIVERED
       ↓
  CANCELLED (hanya dari PENDING_PAYMENT)
```

**Relasi:**
- ManyToOne → User (via `user`)
- ManyToOne → Voucher (via `voucher`, nullable)
- OneToMany → OrderItem (via `items`)
- OneToOne → Payment (via `payment`)

---

## OrderItem

**Tujuan:** Snapshot item pesanan. Menyimpan nama, harga, dan varian produk saat order dibuat (melindungi dari perubahan data produk di masa depan).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| order | ForeignKey(Order) | Pesanan induk |
| product | ForeignKey(Product, null, SET_NULL) | Produk asli (nullable untuk history) |
| product_name | CharField(200) | Nama produk saat order |
| variant_name | CharField(50, blank) | Nama varian saat order (misal: "50ml") |
| price | DecimalField(12,0) | Harga per unit saat order |
| quantity | PositiveIntegerField(default=1) | Jumlah |

**Methods:**
- `total_price()` — `price * quantity`

**Relasi:**
- ManyToOne → Order (via `order`)
- ManyToOne → Product (via `product`, nullable)

---

## Voucher (orders)

**Tujuan:** Global promo codes — kode diskon yang bisa digunakan siapa saja dengan memasukkan kode di session.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| code | CharField(50, unique) | Kode voucher (uppercase) |
| discount_type | CharField(20) | Tipe: `percentage` (%), `fixed` (Rp) |
| discount_amount | DecimalField(12,0) | Nilai diskon (persen/nominal) |
| min_purchase | DecimalField(12,0, default=0) | Minimum belanja |
| max_discount | DecimalField(12,0, null) | Maks diskon (khusus persen) |
| max_uses | PositiveIntegerField(default=0) | Maks penggunaan total (0 = unlimited) |
| used_count | PositiveIntegerField(default=0) | Sudah dipakai |
| is_active | BooleanField(default=True) | Status aktif |
| valid_from | DateTimeField | Mulai berlaku |
| valid_until | DateTimeField | Berakhir |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Methods:**
- `is_valid(subtotal)` — Validasi aktif, masa berlaku, min purchase, max uses.
- `calculate_discount(subtotal)` — Hitung diskon: fixed → min(amount, subtotal); percentage → subtotal * % (capped max_discount).

**Relasi:**
- OneToMany → Order (via `orders`, nullable)

---

## OrderStatusHistory

**Tujuan:** Audit trail perubahan status Order. Append-only (read-only di admin, no add). Menyimpan snapshot status saat dibuat/diubah.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| order | ForeignKey(Order) | Pesanan terkait |
| status | CharField(20) | Status order pada saat ini |
| notes | TextField(blank) | Catatan perubahan |
| created_at | DateTimeField(auto_now_add) | Waktu perubahan |

**Auto-create:** via `Order.save()` override — saat order baru dibuat (1 entry) dan setiap kali status berubah (+1 entry).

**Relasi:**
- ManyToOne → Order (via `order`)

---

## Payment

**Tujuan:** Menyimpan data pembayaran dan integrasi dengan Midtrans Snap.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| order | OneToOneField(Order) | Pesanan terkait |
| transaction_id | CharField(255) | ID transaksi Midtrans |
| snap_token | CharField(255) | Snap token untuk modal pembayaran |
| snap_redirect_url | URLField | Redirect URL Midtrans |
| payment_method | CharField(50) | Metode pembayaran (credit_card, gopay, dll) |
| amount | DecimalField(12,0) | Jumlah pembayaran |
| status | CharField(20) | Status: `pending`, `success`, `failed`, `expired` |
| fraud_status | CharField(50) | Status fraud dari Midtrans |
| payment_time | DateTimeField(null) | Waktu pembayaran |
| raw_response | JSONField(default=dict) | Full response Midtrans (debug) |
| created_at | DateTimeField(auto_now_add) | Dibuat |
| updated_at | DateTimeField(auto_now) | Diupdate |

**Relasi:**
- OneToOne → Order (via `order`)
- OneToMany → PaymentStatusHistory (via `status_history`)

---

## PaymentStatusHistory

**Tujuan:** Audit trail perubahan status Payment. Append-only (read-only di admin, no add).

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| payment | ForeignKey(Payment) | Pembayaran terkait |
| from_status | CharField(20, null) | Status sebelumnya (null untuk CREATED) |
| to_status | CharField(20) | Status baru |
| raw_response | JSONField(null) | Full response Midtrans saat transisi |
| created_at | DateTimeField(auto_now_add) | Waktu perubahan |

**Auto-create:** via `Payment.save()` override — setiap kali status berubah, history entry dibuat.

**Relasi:**
- ManyToOne → Payment (via `payment`)

---

## CustomerAddress

**Tujuan:** Multi-address per user (alamat pengiriman). User bisa punya banyak alamat dengan satu default.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | ForeignKey(User) | Pemilik alamat |
| label | CharField(50) | Label (Rumah, Kantor, Kos, dll) |
| recipient_name | CharField(100) | Nama penerima |
| phone | CharField(20) | Telepon penerima |
| address | TextField | Alamat lengkap |
| city | CharField(100) | Kota |
| province | CharField(100) | Provinsi |
| postal_code | CharField(10) | Kode pos |
| latitude | FloatField(null) | Latitude (untuk integrasi ongkir) |
| longitude | FloatField(null) | Longitude (untuk integrasi ongkir) |
| is_default | BooleanField(default=False) | Alamat default |
| created_at | DateTimeField(auto_now_add) | Dibuat |

**Constraints:**
- Hanya satu `is_default=True` per user (dipaksa di `save()`).

**Methods:**
- `save()` — Jika `is_default=True`, semua alamat lain milik user di-set `is_default=False`.

**Relasi:**
- ManyToOne → User (via `user`)

**Alur Checkout:**
1. GET `/orders/create/` — Pre-fill form dari `CustomerAddress` default (jika ada).
2. User dapat memilih alamat tersimpan atau mengisi manual.
3. POST `/orders/create/` — Snapshot alamat disimpan ke `Order.recipient_name`, `Order.phone`, `Order.shipping_address`, `Order.city`, `Order.province`, `Order.postal_code`.
4. Data `CustomerAddress` TIDAK di-FK ke Order — histori pesanan tetap utuh meskipun alamat diubah.

---

## Wishlist

**Tujuan:** Favorit / wishlist per user (produk yang diinginkan). Tanpa varian — satu wishlist per produk.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | ForeignKey(User) | Pemilik wishlist |
| product | ForeignKey(Product) | Produk favorit |
| created_at | DateTimeField(auto_now_add) | Dibuat |

**Constraints:**
- `unique_together = ['user', 'product']` — Satu produk hanya sekali per user.

**Relasi:**
- ManyToOne → User (via `user`)
- ManyToOne → Product (via `product`)

---

## Voucher (promotions)

**Tujuan:** Voucher template untuk promosi per-user. Dikelola melalui `promotions` app. Terpisah dari `orders.Voucher`.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| code | CharField(50, unique) | Kode voucher (e.g. `WELCOME10`) |
| description | TextField | Deskripsi untuk customer |
| discount_type | CharField(20) | `percentage` or `fixed` |
| discount_amount | DecimalField(12,0) | Nilai diskon (% or Rp) |
| min_purchase | DecimalField(12,0, default=0) | Minimum belanja |
| max_discount | DecimalField(12,0, null) | Cap untuk percentage discount |
| expired_date | DateField(null) | Template voucher expires |
| is_active | BooleanField(default=True) | Harus True untuk bisa di-assign |
| created_at | DateTimeField(auto_now_add) | Dibuat |

**Relasi:**
- OneToMany → UserVoucher (via `user_vouchers`)

---

## UserVoucher (promotions)

**Tujuan:** Per-user assignment voucher promosi dengan expiry individual.

| Field | Type | Keterangan |
|---|---|---|
| id | AutoField (PK) | Primary key |
| user | ForeignKey(User) | Penerima |
| voucher | ForeignKey(Voucher) | Voucher template |
| status | CharField(20) | `available`, `used`, `expired` |
| assigned_at | DateTimeField(auto_now_add) | Ditugaskan |
| used_at | DateTimeField(null) | Digunakan |
| expires_at | DateTimeField | Per-user expiry (e.g. 30d dari registrasi) |

**Relasi:**
- ManyToOne → User (via `user`)
- ManyToOne → Voucher (via `voucher`)

---

## Ringkasan Migrasi

| Migration | App | Description |
|---|---|---|
| 0001 | All | Initial schema |
| accounts.0002 | accounts | CustomerAddress, Wishlist |
| accounts.0003 | accounts | Remove Wishlist.variant, ubah unique_together |
| accounts.0004 | accounts | MemberProfile, PointTransaction |
| products.0004 | products | Brand, ProductImage, Review + Product.brand FK |
| orders.0003 | orders | OrderStatusHistory |
| orders.0004 | orders | Voucher model + Order fields (subtotal, discount_amount, voucher) |
| orders.0005 | orders | Ubah OrderStatusHistory dari from_status/to_status jadi status |
| orders.0006 | orders | Ubah status Order (PENDING→PENDING_PAYMENT, COMPLETED→DELIVERED) |
| payments.0002 | payments | PaymentStatusHistory |
| products.0007 | products | Morris fields (gender_target, occasion, sillage, longevity, season) |
| promotions.0001 | promotions | Voucher, UserVoucher models |
| promotions.0002 | promotions | Seed WELCOME10 voucher data |

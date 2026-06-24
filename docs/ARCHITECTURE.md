# ARCHITECTURE.md

## Struktur Folder Proyek

```
D:\opencode\parfumoray\
├── .env                          # Environment variables (secret key, midtrans keys)
├── .env.example                  # Template for .env
├── .gitignore
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── manage.py                     # Django CLI entry point
├── db.sqlite3                    # SQLite database (development)
│
├── parfumoray/                   # Django project package
│   ├── __init__.py
│   ├── settings.py               # Project settings (apps, middleware, database, etc.)
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI application for production
│   └── asgi.py                   # ASGI application (future websocket support)
│
├── apps/                         # All Django applications
│   ├── __init__.py
│   │
│   ├── core/                     # Shared utilities
│   │   ├── admin_utils.py        # Helper functions for admin (format_rupiah, status_badge)
│   │   ├── context_processors.py # Cart count + wishlist IDs context processors
│   │   ├── decorators.py         # @customer_required decorator
│   │   ├── mixins.py             # CustomerRequiredMixin
│   │   └── templatetags/
│   │       └── core_tags.py      # Template tags (rupiah filter, query_transform)
│   │
│   ├── accounts/                 # User management
│   │   ├── models.py             # Profile, CustomerAddress, Wishlist models
│   │   ├── forms.py              # Registration, login, profile forms
│   │   ├── views.py              # Auth views (register, login, dashboard, profile, member_dashboard)
│   │   ├── urls.py               # Auth URL patterns
│   │   ├── admin.py              # Profile, CustomerAddress, Wishlist admin
│   │   ├── signals.py            # Auto-create profile on user creation
│   │   ├── tests.py              # Account form & view tests
│   │   └── templates/accounts/   # Account templates (login, register, dashboard, etc.)
│   │
│   ├── products/                 # Product catalog
│   │   ├── models.py             # Category, FragranceFamily, FragranceNote, Brand, Product, ProductVariant, ProductImage, Review
│   │   ├── views.py              # HomeView, ProductListView, ProductDetailView, AboutView, FragranceGuideView, ProductByNoteView
│   │   ├── reviews.py            # ReviewFormView, ReviewDeleteView
│   │   ├── urls.py               # Product URL patterns (including /about-morris/, /fragrance-guide/)
│   │   ├── admin.py              # All product app admin registrations
│   │   ├── tests.py              # Product model tests
│   │   └── templates/products/   # Product templates (home, list, detail, about, fragrance_guide, review_form, review_forbidden)
│   │
│   ├── carts/                    # Shopping cart
│   │   ├── models.py             # Cart, CartItem
│   │   ├── forms.py              # CartAddForm
│   │   ├── views.py              # Cart views (detail, add, update, remove, voucher_apply, voucher_remove)
│   │   ├── urls.py               # Cart URL patterns
│   │   ├── admin.py              # CartAdmin with CartItemInline
│   │   └── tests.py              # Cart view tests
│   │
│   ├── orders/                   # Order processing
│   │   ├── models.py             # Order, OrderItem, OrderStatusHistory, Voucher
│   │   ├── forms.py              # CheckoutForm
│   │   ├── views.py              # Order views (create, detail, list, cancel, track)
│   │   ├── urls.py               # Order URL patterns
│   │   ├── admin.py              # OrderAdmin with OrderItemInline, VoucherAdmin
│   │   └── tests.py              # Order model & view tests
│   │
│   ├── payments/                 # Payment integration
│   │   ├── models.py             # Payment, PaymentStatusHistory
│   │   ├── views.py              # Checkout, finish, unfinish, error, notification
│   │   ├── urls.py               # Payment URL patterns
│   │   ├── admin.py              # PaymentAdmin
│   │   ├── midtrans.py           # Midtrans API client (create transaction, status, verify)
│   │   └── tests.py              # Payment model & view tests
│   │
│   └── promotions/               # Customer vouchers
│       ├── models.py             # Voucher, UserVoucher
│       ├── views.py              # voucher_list
│       ├── urls.py               # URLs under /accounts/vouchers/
│       ├── services.py           # assign_welcome_voucher()
│       ├── admin.py              # VoucherAdmin, UserVoucherAdmin
│       └── apps.py               # AppConfig with ready() for signals
│
├── templates/                    # Global templates
│   ├── base.html                 # Base template (Tailwind CDN, Morris palette, navbar, footer)
│   └── includes/
│       ├── navbar.html           # Responsive navigation bar (Morris dark)
│       ├── footer.html           # Site footer (Morris dark)
│       ├── alert.html            # Toast messages (auto-dismiss)
│       ├── product_card.html     # Reusable product card (Morris themed)
│       └── empty_state.html      # Empty state component
│
├── static/                       # Static files
│   ├── css/                      # Custom CSS (currently empty)
│   └── js/                       # Custom JS (currently empty)
│
├── media/                        # User-uploaded files
│   └── products/                 # Product images
│
└── docs/                         # Project documentation
    ├── PROJECT_CONTEXT.md
    ├── ARCHITECTURE.md
    ├── DATABASE_SCHEMA.md
    ├── API_FLOW.md
    ├── FEATURES.md
    ├── TODO.md
    ├── CHANGELOG.md
    ├── DEVELOPMENT_RULES.md
    └── PROMOTIONS.md
```

## Tanggung Jawab Setiap Django App

### `apps.core` — Shared Utilities
- Menyediakan fungsi bantu yang digunakan lintas app.
- `format_rupiah(amount)` — Format angka ke mata uang Rupiah.
- `status_badge_html(status, colors)` — HTML badge untuk status dengan warna.
- Template tag `rupiah` — Filter untuk template.
- Template tag `query_transform` — Mempertahankan query params saat pagination/filter.
- Context processor `cart_count` — Jumlah item keranjang (melewati superuser).
- Context processor `wishlist_ids` — Set of product IDs in wishlist (melewati superuser).
- Decorator `@customer_required` — Blokir superuser dari view customer.
- Mixin `CustomerRequiredMixin` — Sama untuk CBV.

### `apps.accounts` — User Management
- Mengelola autentikasi dan profil pengguna.
- Registrasi dengan validasi email unik.
- Login dengan redirect ke halaman sebelumnya.
- Dashboard customer (statistik pesanan, riwayat).
- Edit profil (username, email, telepon, alamat).
- Password reset flow (4 langkah).
- **CustomerAddress** — Multi-address per user dengan label & default.
- **Wishlist** — Favorit per user+product+variant (unique together).

### `apps.products` — Product Catalog
- **Category** — Pengelompokan produk berdasarkan kategori.
- **FragranceFamily** — Keluarga aroma (Woody, Floral, dll), ManyToMany ke Product.
- **Brand** — Merek parfum (3NF, FK on Product).
- **FragranceNote** — Master data aroma dengan tipe (TOP/MIDDLE/BASE).
  - Satu aroma bisa digunakan oleh banyak produk.
  - Satu produk bisa memiliki banyak aroma.
- **Product** — Data utama produk parfum.
  - Relasi ManyToMany ke FragranceNote dan FragranceFamily, FK ke Brand.
  - Morris fields: gender_target, occasion, sillage, longevity, season.
  - Image, price, stock management via variants.
- **ProductVariant** — Varian ukuran (ml) dengan price, stock, SKU sendiri.
- **ProductImage** — Galeri gambar per produk (is_primary, sort_order, alt_text).
- **Review** — Rating 1-5 per user+product (unique together), `has_purchased_product()`.
- **Brand pages**: `/about-morris/`, `/fragrance-guide/`.

### `apps.carts` — Shopping Cart
- Setiap user memiliki satu keranjang (OneToOne).
- CartItem dengan unique_together (cart, product, variant) — variant nullable.
- CartItem bisa merujuk ke ProductVariant untuk produk dengan multiple ukuran.
- Validasi stok (variant-aware) saat menambah item.
- Voucher apply/remove di halaman cart.

### `apps.orders` — Order Processing
- Membuat pesanan dari keranjang (snapshot data produk).
- OrderItem menyimpan nama, harga, dan variant_name saat order dibuat (history).
- **OrderStatusHistory** — Audit trail append-only, auto-created via Order.save() override.
- **Voucher** — Global promo codes (session-based). Diskon persen/nominal dengan min purchase, usage limit, periode berlaku.
- Status order: PENDING → PAID → PROCESSING → SHIPPED → COMPLETED.
- Cancel hanya untuk status PENDING.

### `apps.payments` — Payment Integration
- Integrasi dengan Midtrans Snap API.
- Generate Snap token untuk pembayaran.
- Callback notification handler (CSRF exempt, HMAC signature verification).
- Update status payment dan order berdasarkan callback.
- Decrement stok produk saat pembayaran sukses (first success only).
- **PaymentStatusHistory** — Audit trail append-only, auto-created via Payment.save() override.

### `apps.promotions` — Customer Vouchers
- **Voucher** — Template promo (code, discount type, amount, min purchase, expiry).
- **UserVoucher** — Per-user assignment with individual expiry and status tracking.
- **WELCOME10**: Auto-assigned 10% voucher on registration (via `services.assign_welcome_voucher()`).
- Terpisah dari `orders.Voucher` (global session-based codes).

## Alur Komunikasi Antar Aplikasi

```
User → products (browse catalog, filter by family/brand/note/category)
     → products (add review, add wishlist)
     → accounts (manage addresses, view vouchers)
     → carts (add items — variant-aware)
     → orders (checkout, create order)
     → payments (Midtrans Snap checkout)
     → payments (notification callback)
     → orders (update status → auto OrderStatusHistory)
     → payments (update status → auto PaymentStatusHistory)
```

```
products.models.Brand ──→ products.models.Product
                                ↓ FK
accounts.models.CustomerAddress → accounts.models.User
accounts.models.Wishlist → accounts.models.User
                                ↓
carts.models.CartItem → carts.models.Cart → accounts.models.User
    ↑ FK (nullable)
products.models.ProductVariant
                                ↓
orders.models.OrderItem → orders.models.Order → accounts.models.User
    ↑ FK (nullable)         ↓
products.models.ProductVariant  orders.models.OrderStatusHistory
                                ↓
payments.models.Payment → orders.models.Order
    ↓
payments.models.PaymentStatusHistory
                                ↓
promotions.models.UserVoucher → promotions.models.Voucher
    ↑
accounts.models.User
```

## Separation of Concerns

- **Products** tidak tahu tentang cart/orders/payments.
- **Carts** hanya tahu tentang Product (FK).
- **Orders** membuat snapshot dari Cart, tidak bergantung pada Cart setelahnya.
- **Payments** hanya tahu tentang Order.
- **Core** tidak tergantung app lain.
- **Promotions** terpisah, hanya dipanggil dari accounts (registrasi) dan orders (checkout).

## Best Practice yang Digunakan

1. **Class-based views** untuk halaman publik (ListView, DetailView, TemplateView).
2. **Function-based views** dengan decorator `@login_required` untuk halaman terproteksi.
3. **Model-level choices** menggunakan `TextChoices` kelas.
4. **Signals** untuk operasi otomatis (auto-create profile).
5. **Middleware Whitenoise** untuk static files di production.
6. **Environment variables** via `.env` + `python-dotenv`.
7. **Prepopulated fields** di admin untuk auto-slug.
8. **`filter_horizontal`** untuk ManyToMany widget di admin.

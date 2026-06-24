# CHANGELOG.md

## v2.1.0 (2026-06-17) — Collection Page Simplification & Luxury Visual Redesign

### Added
- **Luxury Warm Color Palette**: New global design system — warm cream body bg (`#F3ECE4`), dark brown navbar/sidebar/footer (`#1A1411`, `#2A1F1A`), amber accent replacing gold (`amber-600` buttons, `amber-400` hover), solid white product cards with subtle shadows.
- **Custom CSS utility classes**: `card-shadow`, `card-shadow-hover`, `sidebar-shadow` for refined layering.
- **Collection Page Empty State**: Light-themed empty state (white icon circle, stone text, amber CTA).

### Changed
- **Sidebar Filter Simplified**: Removed entire "Aroma" (fragrance note) and "Keluarga Aroma" (fragrance family) filter cards from Collection page sidebar. Kategori remains as the only filter.
- **ProductListView Optimized**: Removed `note_slug`/`family_slug` query params and their `.filter()` calls; removed `fragrance_notes`, `fragrance_families`, `selected_note`, `selected_family` from context — saves 2 DB queries per page load.
- **ProductByNoteView Cleaned**: Removed unused `note`, `fragrance_notes`, `fragrance_families`, `selected_note` context.
- **Product Card Redesigned**: Solid white card (`bg-white`) with warm badges (stone/amber for gender, amber/rose for notes), **amber-600 buttons with dark text** (`text-stone-900`), muted stock indicators, custom hover shadow.
- **Sidebar Restyled**: Dark brown background (`bg-[#2A1F1A]`), category active state uses `bg-amber-600 text-stone-900`, inactive links use `text-stone-400` with subtle hover.
- **Search Input**: Changed from dark (`bg-morris-900`) to light theme (`bg-white border-stone-300`).
- **Pagination**: Changed from dark borders to white cards with stone borders, amber active state.
- **Navbar Overhaul**: `bg-[#1A1411]` (dark brown), amber underlines (was gold), amber-600 buttons with dark text, stone-400 nav links, stone-800 dropdown menu.
- **Footer Overhaul**: `bg-[#1A1411]`, amber link hovers, stone-500/600 text/icons, amber brand accent.
- **Loading Overlay**: Switched to `bg-[#1A1411]/60` with amber spinner.
- **Scrollbar**: Custom warm stone scrollbar colors.
- **Detail Page Family Link**: Changed from `?family={{ family.slug }}` query param to plain `{% url 'products:list' %}`.

### Removed
- **Aroma Filter Section**: Entire fragrance note list with colored dots, product counts, and reset link removed from sidebar.
- **Keluarga Aroma Section**: Entire fragrance family filter card removed from sidebar.
- **Hidden Form Inputs**: `note` and `family` query parameters removed from search and category filter links.
- **Sidebar Dynamic Header**: Title/subtitle for `note` and `selected_family` context removed; only category-based heading remains.

### Preserved (No Data Loss)
- `FragranceNote` and `FragranceFamily` models and data remain intact.
- `products/note/<slug>/` and `products/family/<slug>/` URLs still work when linked from detail pages.
- Fragrance Guide page, product detail note/family display, and admin unchanged.

### Documentation
- All 9 doc files updated to reflect sidebar simplification and new luxury color palette.

### Tests
- All 85 tests pass with no modifications needed (UI-only / context cleanup changes).

---

## v2.0.0 (2026-06-17) — Parfum Morris Rebrand & Color Contrast Audit

### Added
- **Product Morris Fields**: `gender_target` (men/women/unisex), `occasion` (daily/office/casual/formal/evening), `sillage` (intimate/moderate/heavy), `longevity` (short/moderate/long/very_long), `season` (spring/summer/fall/winter/all). All with TextChoices and safe defaults.
- **About Morris page** (`/about-morris/`): Brand story, three value cards (Premium Quality, Expertly Crafted, Made with Love), mission statement. Dark Morris theme.
- **Fragrance Guide page** (`/fragrance-guide/`): Five fragrance families, notes pyramid (Top/Middle/Base), four-step choosing guide, CTA to collection. Dark theme.
- **Homepage Hero Rebrand**: Title "Find Your Signature Scent", Morris colour scheme, gold accent buttons, Fragrance Guide link, stats bar (50+ variants / 100% authentic / 24h long lasting / Free delivery).
- **Product Card Rebrand**: `bg-morris-900/50` cards, gender/occasion badges, note badges with colour by type, wishlist link fix (no nested `<a>`).
- **Product Detail New Fields**: Five-column grid showing gender/occasion/season/longevity/sillage with solid `bg-morris-950` cards.
- **Product List Rebrand**: Full dark theme — sidebar filters with gold-active state, dark search input, dark pagination, empty state with gold CTA.
- **Seed Data Update**: All 12 products rebranded to Morris names (e.g. "Morris Noir", "Jasmine Royale"), English copywriting, each with gender/occasion/season/sillage/longevity values assigned.

### Changed
- **Color Palette**: Defined custom `morris` (50–950) and `gold` (400/500/600) in tailwind.config.
- **Navbar Logo**: Gold subtitle `text-gold-500` → `text-gold-400` for WCAG AA (5.3:1).
- **Footer**: Body/copyright text `text-morris-500` → `text-morris-400` for 4.3:1 contrast.
- **Product Admin**: Updated fieldsets to include new fields in "Target & Karakter" and "Kinerja" sections.
- **Homepage**: Category count `text-morris-500` → `text-morris-400` for contrast.

### Fixed
- **CRITICAL**: Product detail data cards — `bg-morris-800/50` → `bg-morris-950` (invisible text on semi-transparent light bg).
- **CRITICAL**: About / Fragrance Guide pages — added `bg-morris-950` section bg, cards changed to `bg-morris-900` + `border-morris-700`.
- **WCAG FAIL**: Product card category label `text-gold-500` (2.8:1) → `text-gold-400` (5.3:1).
- **WCAG FAIL**: Empty states text `text-morris-500` → `text-morris-400`.
- **Nested `<a>` bug**: Wishlist link in product card refactored to use `{% url %}` without nesting anchor tags.

### Documentation
- **Full docs rewrite**: All 9 doc files updated to reflect Parfum Morris rebrand, new fields, promotions app, FragranceFamily model, and current project state. Single Source of Truth principle established.

### Migration
- `products.0007_add_product_morris_fields` — Additive migration for gender_target, occasion, sillage, longevity, season.

---

## v1.5.0 (2026-06-16) — Discount/Voucher System

### Added
- **Voucher Model**: Kode diskon dengan tipe persen/nominal, min_purchase, max_discount, usage limit, periode berlaku.
- **Voucher.is_valid()**: Validasi lengkap (aktif, masa berlaku, min purchase, max uses).
- **Voucher.calculate_discount()**: Hitung diskon otomatis (persen dengan max_discount, nominal capped di subtotal).
- **VoucherAdmin**: Admin dengan search, filter, fieldsets, formatted display.
- **Cart Voucher UI**: Input kode voucher di sidebar keranjang + tombol Pakai/Hapus.
- **Checkout Discount**: Voucher diterapkan saat checkout, diskon tercermin di total akhir.
- **Order Discount Fields**: `subtotal`, `discount_amount`, `voucher` FK — menyimpan riwayat diskon.
- **Usage Counter**: `used_count` increment otomatis saat order dibuat (race-condition safe via F()).
- **Session-based**: Kode voucher disimpan di session, hilang otomatis jika tidak valid saat checkout.

### Changed
- `Order` model: added `subtotal`, `discount_amount`, `voucher` FK.
- `OrderAdmin`: fieldsets include voucher info, readonly fields updated.
- Cart template: voucher section + discount line + final total.
- Checkout template: discount breakdown + final total.
- Order detail template: subtotal/discount/total breakdown (only when discount applies).

### Migration
- `orders.0004`: Voucher model + Order fields (subtotal, discount_amount, voucher).

---

## v1.4.1 (2026-06-16) — Promotions App & Welcome Voucher

### Added
- **Promotions App**: New Django app with `Voucher` (template promo) and `UserVoucher` (per-user assignment) models.
- **WELCOME10 Voucher**: Auto-assignment of 10% discount voucher on registration (min Rp 200k, 30 days validity).
- **assign_welcome_voucher()**: Idempotent service function called from RegisterView.
- **Customer Voucher List**: `/accounts/vouchers/` — shows assigned vouchers with status badges.
- **Checkout Integration**: UserVoucher selection at checkout, takes precedence over global session voucher.
- **VoucherAdmin, UserVoucherAdmin**: Admin registration in promotions app.

### Migration
- `promotions.0001`: Voucher, UserVoucher models.
- `promotions.0002`: Seed WELCOME10 voucher data.

---

## v1.4.0 (2026-06-16) — Database Redesign & New Entities

### Added
- **Brand Model**: Entitas brand terpisah (3NF). FK `brand` pada Product.
- **ProductImage Model**: Galeri gambar per produk dengan `is_primary`, `sort_order`, `alt_text`.
- **Review Model**: Rating 1-5 per user+product (unique together), `has_purchased_product()` method.
- **FragranceFamily Model**: Keluarga aroma (Woody, Floral, Oriental, dll), ManyToMany ke Product.
- **CustomerAddress Model**: Multi-address per user dengan label dan default flag.
- **Wishlist Model**: Favorit per user+product+variant (unique together).
- **OrderStatusHistory Model**: Audit trail append-only untuk perubahan status Order.
- **PaymentStatusHistory Model**: Audit trail append-only untuk perubahan status Payment, menyertakan `raw_response`.
- **BrandAdmin, ProductImageInline, ReviewAdmin (read-only)**: Admin baru.
- **CustomerAddressAdmin, WishlistAdmin**: Admin baru di accounts.
- **OrderStatusHistoryAdmin (read-only, no add)**: Admin baru di orders.
- **PaymentStatusHistoryAdmin (read-only, no add)**: Admin baru di payments.

### Changed
- **Order.save() override**: Auto-create OrderStatusHistory on status change. Fixed PK bug (save first, then create history for new orders).
- **Payment.save() override**: Auto-create PaymentStatusHistory on status change. Same PK fix.
- **Order bulk actions in admin**: Iterate over queryset and call `order.save()` (triggers history).
- **OrderItem**: Added `variant_name` snapshot field.
- **CartItem**: Added `variant` FK (nullable) + updated `unique_together` to `[cart, product, variant]`.
- **ProductAdmin**: Removed price/stock from `list_editable` (now managed via variants).
- **Product model**: Added `has_variants()`, `min_price()`, `total_stock()` methods, removed old `price`/`stock` list_editable.

### Fixed
- **Order.save() PK bug**: New orders failed FK constraint when creating OrderStatusHistory before first save.
- **Payment.save() PK bug**: Same issue for PaymentStatusHistory.

### Migrations
- `products.0004`: Brand, ProductImage, Review + Product.brand FK
- `accounts.0002`: CustomerAddress, Wishlist
- `orders.0003`: OrderStatusHistory
- `payments.0002`: PaymentStatusHistory

---

## v1.3.0 (2026-06-16)

### Added
- **Forgot Password System**: Implementasi Django Password Reset bawaan dengan 4 halaman:
  - `/forgot-password/` — Form input email dengan desain premium
  - `/forgot-password/sent/` — Konfirmasi email terkirim
  - `/reset/<uidb64>/<token>/` — Form password baru dengan validasi
  - `/reset/success/` — Konfirmasi sukses + tombol login
- **Email Configuration**: SMTP-ready via environment variables.
- **File-based Email Backend**: Development mode menyimpan email ke file di `emails/`.
- **Tests**: 4 test baru untuk forgot password, create new password, invalid token, expired token. Total: 50 tests.

### Changed
- URL paths: `/password-reset/` → `/forgot-password/`, `/reset/done/` → `/reset/success/`.
- Template files renamed for consistency.

---

## v1.2.0 (2026-06-16)

### Added
- **Product Variant System**: Setiap produk bisa memiliki banyak varian ukuran (ml) dengan harga dan stok masing-masing.
- **`ProductVariant` model** — fields: `product` (FK), `size_ml`, `price`, `stock`, `sku`, `is_available`.
- **`ProductVariantInline`** di admin — tambah/edit varian langsung dari halaman Product.
- **Size picker** di halaman detail produk — pilih ukuran (30ml/50ml/100ml) sebelum tambah ke keranjang.
- **Variant-aware cart** — `CartItem.variant` FK nullable; harga & stok dari variant jika ada.
- **Variant snapshot di order** — `OrderItem.variant_name` untuk riwayat pesanan.
- **`has_variants()`, `min_price()`, `total_stock()`** methods di Product model.
- **33 variant seed data** untuk 11 produk.

### Changed
- `Product.list_editable` → hanya `is_available` (stok via variants).
- `unique_together` CartItem: `[cart, product]` → `[cart, product, variant]`.
- Product card: produk dengan varian → tombol "Pilih Ukuran" (link ke detail).
- Cart/Checkout/Order templates: tampilkan info varian.

---

## v1.1.0 (2026-06-16)

### Added
- **Role Separation System**: Pemisahan akses Superuser (Admin) dan Customer.
- **`@customer_required` Decorator**: Memblokir superuser dari mengakses view customer.
- **`CustomerRequiredMixin`**: Mixin untuk Class-Based Views.
- **Frontend Role Protection**: Banner "Anda login sebagai Administrator" di navbar.
- **Admin Banner**: Navbar menampilkan banner amber dengan link ke Admin Panel saat superuser login.

### Security
- Server-side validation on all customer views prevents superuser access.

---

## v1.0.0 (2026-06-16)

### Added
- **Fragrance Note System**: Model `FragranceNote` dengan `note_type` (TOP/MIDDLE/BASE) dan relasi ManyToMany ke `Product`.
- **Fragrance Note Admin**: `FragranceNoteAdmin` dengan search, filter by type, product count.
- **Product Admin Enhancement**: `filter_horizontal` untuk fragrance_notes, fragrance count di list display.
- **Product Detail Page**: Fragrance notes grouping dalam card premium (Top/Middle/Base) dengan link ke filter by note.
- **Filter by Fragrance Note**: Sidebar aroma di product list page, halaman `/products/note/<slug>/`.
- **Product Card Badges**: Badge kecil menampilkan 1-3 aroma utama dengan warna sesuai tipe note.
- **Query Optimization**: `prefetch_related('fragrance_notes')` di semua product queries.
- **Seed Data**: 16 fragrance notes (6 TOP, 5 MIDDLE, 5 BASE) dengan assignment ke semua produk.
- **Documentation System**: `docs/` folder dengan dokumentasi lengkap.

### Fixed
- **`format_html` TypeError**: Fixed `apps/products/admin.py:56` — mengganti `format_html` tanpa args dengan plain string (Django 6.0.5 requirement).

---

## v0.9.0 (2026-06-15)

### Added
- **Midtrans Payment Callback**: Notification handler dengan HMAC signature verification.
- **Stock Decrement**: Auto-decrement stok produk saat payment success (dengan anti double-decrement).
- **Payment Status Handlers**: Success, pending, error pages dengan verifikasi status transaksi.
- **Production Security**: HSTS, SSL redirect, secure cookies, XSS filtering.

---

## v0.8.0 (2026-06-15)

### Added
- **Midtrans Snap Integration**: Payment checkout page dengan Snap.js popup.
- **Payment Model**: transaction_id, snap_token, snap_redirect_url, raw_response (JSON).
- **Payment Views**: checkout, finish, unfinish, error, notification (CSRF exempt).
- **Midtrans API Client**: create_transaction, get_transaction_status, verify_signature.

---

## v0.7.0 (2026-06-15)

### Added
- **Order Management**: Order creation from cart, OrderItem snapshots, status management.
- **Order Views**: list, detail, create, cancel (PENDING only).
- **Checkout Form**: Pre-fill from profile (name, phone, address).
- **Validation**: Stock validation before order creation.
- **Order Admin**: Status badges (color-coded), bulk actions (process/ship/complete/cancel), OrderItem inline.

---

## v0.6.0 (2026-06-15)

### Added
- **Shopping Cart System**: Cart and CartItem models.
- **Cart Views**: detail, add (stock validation), update (capped by stock), remove.
- **Cart Admin**: CartItem inline, total items/price display.
- **Cart Count Context Processor**: Badge di navbar.

---

## v0.5.0 (2026-06-15)

### Added
- **Product Detail Page**: Image, price, stock indicator, description, quantity selector, add to cart button.
- **Related Products**: Same category products (4 items).
- **Breadcrumb Navigation**.

---

## v0.4.0 (2026-06-15)

### Added
- **Product List Page**: Search by name/description, filter by category (sidebar).
- **Pagination**: 12 products per page with query_transform template tag.
- **Product Card Component**: Reusable with image, name, price, stock status, add to cart.
- **Empty State**: When no products match.

---

## v0.3.0 (2026-06-15)

### Added
- **Home Page**: Hero section, categories grid, featured products (8 items), new arrivals (4 items), stats bar, CTA section.

---

## v0.2.0 (2026-06-15)

### Added
- **Product Model**: Category with ForeignKey, price (Decimal), stock, image, is_available.
- **Product Admin**: Thumbnail preview, rupiah formatting, prepopulated slug, bulk actions.
- **Category Model**: name, slug, description.
- **django-cleanup** integration for auto image cleanup.

---

## v0.1.0 (2026-06-15)

### Added
- **Django project initialization** dengan project package `parfumoray`.
- **Django apps structure**: core, accounts, products, carts, orders, payments.
- **Settings configuration**: SQLite database, Tailwind CSS via CDN, Indonesian locale, Asia/Jakarta timezone, Whitenoise.
- **Core utilities**: `format_rupiah()`, `status_badge_html()`, `rupiah` template filter, `query_transform` tag.
- **Context processors**: `cart_count` for navbar badge.
- **Accounts app**: Profile model, registration, login, logout, password reset.
- **Dashboard**: Order statistics, order history, profile view/edit.
- **Tailwind CSS styling**: Responsive navbar, footer, alert messages, forms.
- **Base template**: Google Fonts (Playfair Display + Inter), consistent layout.
- **pytest configuration** with `pytest.ini`.
- **Environment variables** via `.env` + `python-dotenv`.

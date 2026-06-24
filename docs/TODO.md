# TODO.md

> Status: ✅ Selesai | 🔄 Sedang Dikerjakan | ⏳ Rencana

---

## Backend

### Framework & Setup
- [x] Django project initialization
- [x] Django apps structure (core, accounts, products, carts, orders, payments, promotions)
- [x] Environment variables configuration
- [x] Database setup (SQLite)
- [x] Static files (Whitenoise)
- [x] Midtrans integration setup
- [x] pytest configuration

### Models & Database
- [x] Category model
- [x] FragranceFamily model (keluarga aroma, ManyToMany dengan Product)
- [x] Product model (with Morris fields: gender_target, occasion, sillage, longevity, season)
- [x] FragranceNote model (ManyToMany dengan Product)
- [x] Brand model (3NF, FK on Product)
- [x] ProductImage model (gallery per produk)
- [x] Review model (rating 1-5 per user+product, comment)
- [x] CustomerAddress model (multi-address per user)
- [x] Wishlist model (favorit per user+product, tanpa variant)
- [x] ProductVariant model (size/ml, price, stock, SKU)
- [x] Voucher model (orders) — global session-based promo codes
- [x] Voucher model (promotions) — template promo
- [x] UserVoucher model (promotions) — per-user assignment
- [x] Cart & CartItem models (variant-aware)
- [x] Order & OrderItem models (snapshot data, variant_name)
- [x] OrderStatusHistory model (audit trail)
- [x] Payment model
- [x] PaymentStatusHistory model (audit trail)
- [x] Profile model (OneToOne User)
- [x] MemberProfile model (loyalty level/poin, Silver/Gold/Platinum)
- [x] PointTransaction model (riwayat poin: earn/redeem/upgrade)
- [x] All migrations applied (no data loss)

### Admin
- [x] CategoryAdmin (product count, search, prepopulated slug)
- [x] ProductAdmin (thumbnail, fragrance notes filter_horizontal, Morris fields fieldsets, bulk actions, ImageInline, VariantInline)
- [x] FragranceNoteAdmin (search by name, filter by type, product count)
- [x] BrandAdmin (product count, search)
- [x] ReviewAdmin (read-only, rating filter)
- [x] CartAdmin (CartItem inline, total price/items)
- [x] OrderAdmin (status badges, user link, OrderItem inline, bulk actions iterate+save)
- [x] OrderStatusHistoryAdmin (read-only, no add)
- [x] VoucherAdmin (orders) — search, filter, fieldsets
- [x] VoucherAdmin (promotions) — manage templates
- [x] UserVoucherAdmin (promotions) — filter by status, search
- [x] PaymentAdmin (order link, transaction ID, raw response collapse)
- [x] PaymentStatusHistoryAdmin (read-only, no add)
- [x] ProfileAdmin (user link, phone search)
- [x] MemberProfileAdmin (level filter, total spending, read-only)
- [x] PointTransactionAdmin (read-only, no add/change)
- [x] CustomerAddressAdmin
- [x] WishlistAdmin
- [x] Admin Dashboard (analytics, inventory, sales, member levels)

### Authentication
- [x] User registration (form validation, email unique)
- [x] User login (next parameter, redirect_authenticated_user)
- [x] User logout
- [x] Password reset (4-step flow)
- [x] Profile management (update)
- [x] Dashboard (order statistics, history)
- [x] Member dashboard + member benefits page
- [x] Signal auto-create profile

### Products
- [x] Product list with search & filter by category (notes/family filters removed from sidebar UI, still accessible via `/products/note/<slug>/` and `/products/family/<slug>/` URLs)
- [x] Product detail with fragrance notes grouping (Top/Middle/Base)
- [x] Product detail with Morris fields grid (gender, occasion, season, longevity, sillage)
- [x] Product filter by fragrance note (`/products/note/<slug>/`)
- [x] Product card with note badges + gender/occasion badges (Morris theme)
- [x] Related products (same category)
- [x] Pagination (12 per page)
- [x] Product variant system (size/ml)
- [x] Brand management (separate entity)
- [x] Product image gallery
- [x] About Morris page (`/about-morris/`)
- [x] Fragrance Guide page (`/fragrance-guide/`)
- [ ] Product comparison ⏳

### Cart
- [x] Add to cart (stock validation, variant-aware)
- [x] Update quantity (increase, decrease, auto-delete at 0)
- [x] Remove item
- [x] Cart count in navbar
- [x] Cart detail with item list
- [x] Voucher input/apply/remove at cart

### Orders
- [x] Checkout form (pre-fill from profile, discount breakdown, UserVoucher selection)
- [x] Create order (validate stock, snapshot items, clear cart, consume voucher)
- [x] Order list (per user)
- [x] Order detail
- [x] Cancel order (PENDING_PAYMENT only)
- [x] Status management (PENDING_PAYMENT/PAID/PROCESSING/SHIPPED/DELIVERED/CANCELLED)
- [x] Order tracking page with timeline visual
- [x] Order status audit trail (OrderStatusHistory)
- [x] Session-based voucher (global codes)
- [x] UserVoucher selection at checkout
- [ ] Shipping cost calculation ⏳
- [ ] Invoice PDF ⏳

### Payments
- [x] Midtrans Snap token generation
- [x] Checkout page with Snap.js
- [x] Payment success page (verify with Midtrans API)
- [x] Payment pending/unfinish page
- [x] Payment error page
- [x] Notification handler (callback)
- [x] HMAC signature verification
- [x] Update Order status from callback
- [x] Decrement stock on first success (anti double-decrement)
- [x] Auto-update MemberProfile (total_spending, earn_points, upgrade_level) on success
- [x] Payment status audit trail (PaymentStatusHistory)
- [ ] Payment retry for expired/failed ⏳
- [ ] Refund handling ⏳

### Notifications
- [ ] WhatsApp integration ⏳
- [ ] Email real sending (SMTP) ⏳

---

## Frontend

### Public Pages
- [x] Home page (hero Morris branding, categories, featured, new arrivals, stats, CTA)
- [x] About Morris page (brand story, values, mission)
- [x] Fragrance Guide page (families, notes pyramid, how to choose)
- [x] Product list page (search, sidebar filter, grid, pagination) — luxury warm palette (cream bg, dark brown sidebar, amber accents, white cards)
- [x] Product detail page (image, info, fragrance notes, Morris fields, add to cart)

### Auth Pages
- [x] Login page
- [x] Register page
- [x] Password reset pages
- [x] Dashboard page
- [x] Profile edit page
- [x] Member benefits page
- [x] Member dashboard page (level, points, history)

### Cart & Order Pages
- [x] Cart detail page (with voucher input)
- [x] Checkout page (with discount breakdown)
- [x] Order list page
- [x] Order detail page
- [x] Order tracking page (timeline visual)

### Payment Pages
- [x] Payment checkout page (Snap.js embed)
- [x] Payment success page
- [x] Payment unfinish page
- [x] Payment error page

### Components
- [x] Navbar (responsive, mobile menu, dark brown luxury, admin banner)
- [x] Footer (dark brown luxury, WCAG AA compliant)
- [x] Product card (white card, warm gender/occasion badges, note badges, amber-600 CTA, wishlist)
- [x] Alert messages (auto-dismiss)
- [x] Empty state
- [x] Breadcrumb

### UI/UX
- [x] Tailwind CSS via CDN with custom Morris palette config
- [x] Google Fonts (Playfair Display + Inter)
- [x] Morris color palette (morris-50 to morris-950, gold-400/500/600)
- [x] Luxury warm palette (cream bg `#F3ECE4`, dark brown `#1A1411`/`#2A1F1A`, amber accents, white cards)
- [x] Custom CSS utilities (card-shadow, card-shadow-hover, sidebar-shadow)
- [x] WCAG AA color contrast compliance (verified audit)
- [x] Responsive design (mobile, tablet, desktop)
- [x] Animations (hover, transitions, fade-in)
- [x] Image lazy loading
- [x] Skeleton loading
- [x] Favicon (production-ready)

---

## Payment Integration

- [x] Midtrans merchant account setup (sandbox)
- [x] Snap.js integration
- [x] Transaction status checking
- [x] Signature verification
- [x] Callback handling
- [ ] Midtrans production ⏳

---

## Security

- [x] Environment variables for secret keys
- [x] CSRF protection
- [x] Login required for protected views
- [x] Customer/superuser role separation
- [x] Midtrans HMAC signature verification
- [x] Order ownership validation
- [x] Gross amount validation (callback)
- [x] HSTS, SSL redirect, secure cookies (production)
- [ ] Rate limiting for API endpoints ⏳

---

## Optimization

- [x] select_related for category (product queries)
- [x] prefetch_related for fragrance_notes, fragrance_families
- [x] Cart items select_related('product')
- [x] Database indexing
- [x] Redis caching (falls back to locmem)
- [x] Image optimization (WebP filter)
- [ ] N+1 query audit ⏳

---

## Testing

- [x] pytest configuration
- [x] Product model tests (incl. variant)
- [x] Account form tests
- [x] Auth view tests
- [x] MemberProfile & PointTransaction tests (level, points, upgrade)
- [x] Cart view tests (variant-aware cart)
- [x] Order model & view tests (status history, voucher)
- [x] Payment model & view tests (status history)
- [x] 85+ total tests passing
- [ ] Core app tests (context_processor, template tags) ⏳
- [ ] Payment notification test (valid/invalid signature) ⏳
- [ ] Integration test (full checkout flow) ⏳

---

## Deployment

- [x] Whitenoise static files
- [x] Production security settings
- [ ] Docker compose ⏳
- [ ] CI/CD pipeline (GitHub Actions) ⏳
- [ ] PostgreSQL migration ⏳
- [ ] Domain + SSL ⏳
- [ ] Sentry error tracking ⏳

---

## Documentation

- [x] PROJECT_CONTEXT.md
- [x] ARCHITECTURE.md
- [x] DATABASE_SCHEMA.md
- [x] API_FLOW.md
- [x] FEATURES.md
- [x] TODO.md
- [x] CHANGELOG.md
- [x] DEVELOPMENT_RULES.md
- [x] PROMOTIONS.md
- [ ] SEO meta tags structured data (JSON-LD) ⏳

# PROMOTIONS — Parfum Morris

> Refer to DATABASE_SCHEMA.md for authoritative model field definitions.

## Overview

The `promotions` app manages customer-facing discount vouchers with per-user assignment. It provides:

- **Voucher** templates (admin-managed promo definitions like WELCOME10)
- **UserVoucher** (per-user assignments with individual expiry)
- Auto-assignment of welcome vouchers on registration
- Voucher selection at checkout

This is separate from the global `orders.Voucher` model which powers session-based promo codes.

## Models

See `apps/promotions/models.py` or DATABASE_SCHEMA.md for full field definitions.

### `promotions.Voucher`
Voucher template: code, discount type/amount, min purchase, max discount cap, expiry date, active flag.

### `promotions.UserVoucher`
Per-user assignment: FK to User and Voucher, status (available/used/expired), assigned_at, used_at, expires_at.

## WELCOME10 Voucher

| Property | Value |
|---|---|
| Code | `WELCOME10` |
| Discount | 10% |
| Min Purchase | Rp 200,000 |
| Max Discount | — (unlimited) |
| Validity | 30 days from registration |

### Auto-Assignment

Defined in `apps/promotions/services.py:assign_welcome_voucher()`. Called from `RegisterView.form_valid()` in `apps/accounts/views.py`.

Logic:
1. Look up `Voucher.objects.get(code='WELCOME10', is_active=True)`
2. If already assigned to this user → skip (idempotent)
3. Create `UserVoucher` with `expires_at = now() + timedelta(days=30)`

If the voucher template does not exist (e.g. not yet created via Admin), the service silently returns `None`.

## Customer Voucher List

**URL:** `/accounts/vouchers/`  
**View:** `promotions.views.voucher_list`  
**Template:** `promotions/voucher_list.html`  
**Nav link:** Dashboard sidebar → "Voucher Saya"

Shows all vouchers assigned to the logged-in user, with status badges and a "Gunakan Sekarang" button for available ones.

## Checkout Integration

In `apps/orders/views.py:order_create()`:

1. **GET:** `get_available_vouchers(user, subtotal)` returns active, non-expired vouchers meeting min_purchase.
2. **POST:** If `user_voucher_id` in request data, validate and apply its discount (capped at subtotal, fixed amount or percentage with optional max_discount cap).
3. **Consumption:** After order creation, mark `UserVoucher.status = USED` and set `used_at`.

If no UserVoucher is selected, the existing session-based `voucher_code` flow (global `orders.Voucher`) is used as fallback.

## Admin

Both models are registered in `apps/promotions/admin.py`:

- **VoucherAdmin** — manage voucher templates (code, discount, min purchase, expiry)
- **UserVoucherAdmin** — view assignments, filter by status, search by user/voucher

## Coexistence

| Type | Model | Scope | Lifecycle |
|---|---|---|---|
| Global promo codes | `orders.Voucher` | Any user with the code | Session-based, manual entry |
| Customer vouchers | `promotions.UserVoucher` | Per-user assignment | Auto-assigned, per-user expiry |

Both can exist in the same checkout flow; UserVoucher takes precedence when explicitly selected.

# Order / Checkout Module — Black-Box Test Report

**Date:** 2026-06-26  
**Test file:** `tests_order.py`  
**Total tests:** 69  
**Passed:** 69  
**Failed:** 0  
**Duration:** 86.51s  

---

## Test Groups

| Group | Tests | Description |
|---|---|---|
| `TestCheckoutAddressSelection` | 5 | Default address prefilled, profile fallback, address list in context, login required, empty cart redirect |
| `TestCheckoutShipping` | 2 | No shipping cost field on Order, total = subtotal - discount |
| `TestCheckoutVoucherCalculation` | 9 | Percentage discount, max_discount cap, fixed discount, discount capped at subtotal, voucher context on GET, invalid voucher cleared, UserVoucher marked USED, used_count incremented, session cleared after order |
| `TestCheckoutTotalPrice` | 3 | No voucher, multiple items, voucher + multiple items |
| `TestCheckoutFormValidation` | 8 | Valid form, phone not 08, phone too short, address too short, missing required fields, cascade hierarchy (city/district/postal_code mismatch), form errors rendered |
| `TestOrderCreation` | 13 | Successful creation, OrderItem creation, cart cleared, redirect to payment, address saved as text, default status, status history, insufficient stock rejected, variant product order items, empty cart redirect, success message, notes saved |
| `TestOrderDetail` | 5 | Shows order info, shows items, other user 404, login required, status badge |
| `TestOrderHistory` | 5 | Lists all orders, newest first, only own orders, empty list, login required |
| `TestOrderCancel` | 8 | Cancel pending, non-pending redirects, non-pending error message, success message, other user 404, login required, status history updated, cannot cancel shipped |
| `TestOrderConfirmReceived` | 4 | Confirm delivered, non-delivered rejected, other user 404, success message |
| `TestOrderTracking` | 2 | Shows pending status, shows paid status |
| `TestCheckoutEdgeCases` | 5 | Long recipient name, phone with formatting, address with newlines, order number format, multiple variants same product |

---

## Address Selection

| Scenario | Expected | Actual |
|---|---|---|
| GET with default address | Form prefilled from default CustomerAddress | ✅ |
| GET without address | Form prefilled from Profile (username, phone) | ✅ |
| GET with addresses | Address list in context | ✅ |
| GET without login | 302 redirect | ✅ |
| GET without cart items | 302 redirect + warning message | ✅ |

---

## Shipping

| Scenario | Expected | Actual |
|---|---|---|
| `shipping_cost` field on Order | NOT present | ✅ |
| `shipping_fee` field on Order | NOT present | ✅ |
| `total = subtotal - discount` (no shipping) | Always holds | ✅ |

**Key finding:** Shipping is hardcoded as "Gratis" in the checkout template. There is no shipping cost calculation anywhere in the codebase. The `Order` model has address fields but no shipping cost field. RajaOngkir integration is listed as a future priority.

---

## Voucher Calculation

| Scenario | Input | Expected Discount | Actual |
|---|---|---|---|
| Percentage (20%), subtotal=200000 | `PCT20` | 40000 (20% of 200k) | ✅ |
| Percentage capped by max_discount (50% off, max 30000) | `PCT50` | 30000 (capped) | ✅ |
| Fixed discount (50000) | `FIXED50` | 50000 | ✅ |
| Fixed discount exceeds subtotal (999999 vs 200000) | `BIGFIX` | 200000 (capped at subtotal) | ✅ |
| UserVoucher marked USED after checkout | `PCT20` | — | ✅ |
| `used_count` incremented when no UserVoucher | `PCT20` | — | ✅ |
| Session voucher cleared after order | `PCT20` | — | ✅ |
| Invalid voucher cleared on GET | `INVALID` | — | ✅ |
| Voucher context on GET | `PCT20` | 40000 | ✅ |

### Discount Calculation Rules (verified)

```
Percentage: amount = min(subtotal × discount_amount / 100, max_discount, subtotal)
Fixed:      amount = min(discount_amount, subtotal)
```

---

## Total Price

| Scenario | Subtotal | Discount | Expected Total | Actual |
|---|---|---|---|---|
| No voucher, 1 product × 2 qty | 200,000 | 0 | 200,000 | ✅ |
| No voucher, 2 products (1×100k + 3×25k) | 175,000 | 0 | 175,000 | ✅ |
| Fixed 30k voucher + multiple items | 175,000 | 30,000 | 145,000 | ✅ |

---

## Checkout Validation

| Validation Rule | Status |
|---|---|
| Valid cascade (all 4 levels match) | ✅ |
| Phone must start with 08 | ✅ |
| Phone minimum 10 digits | ✅ |
| Shipping address minimum 10 characters | ✅ |
| Required fields (name, phone, address, province, city, district, postal_code) | ✅ |
| City must belong to selected province | ✅ |
| District must belong to selected city | ✅ |
| Postal code must belong to selected district | ✅ |
| Form errors rendered on invalid POST (200) | ✅ |

---

## Order Creation

| Scenario | Status |
|---|---|
| Order created with correct user | ✅ |
| Order number format (`ORD-YYYYMMDD-XXXXXX`) | ✅ |
| Order items created from cart items | ✅ |
| Cart cleared after order | ✅ |
| Redirect to `payments:checkout/{order.id}` | ✅ |
| Address fields saved as text (not FK) | ✅ |
| Default status `PENDING_PAYMENT` | ✅ |
| `OrderStatusHistory` created on creation | ✅ |
| Insufficient stock rejected (order not created) | ✅ |
| Variant product items with correct price/name | ✅ |
| Empty cart on POST → redirect | ✅ |
| Success message on creation | ✅ |
| Notes field saved | ✅ |

---

## Order Detail

| Scenario | Status |
|---|---|
| Shows order number | ✅ |
| Shows product names and quantities | ✅ |
| Other user gets 404 | ✅ |
| Requires login (302) | ✅ |
| Shows status badge ("Pending") | ✅ |

---

## Order History

| Scenario | Status |
|---|---|
| Lists all orders for user | ✅ |
| Orders sorted newest first | ✅ |
| Only shows own orders | ✅ |
| Empty list returns 200 | ✅ |
| Requires login (302) | ✅ |

---

## Cancel Order

| Scenario | Status |
|---|---|
| Cancel `PENDING_PAYMENT` → `CANCELLED` | ✅ |
| Cancel `PAID` → stays `PAID` (redirect) | ✅ |
| Cancel `PROCESSING` → error message | ✅ |
| Cancel `SHIPPED` → stays `SHIPPED` | ✅ |
| Success message on cancel | ✅ |
| Other user gets 404 | ✅ |
| Requires login (302) | ✅ |
| Status history updated (includes CANCELLED) | ✅ |

**Rule:** Only orders with status `PENDING_PAYMENT` can be cancelled.

---

## Confirm Received

| Scenario | Status |
|---|---|
| Confirm `DELIVERED` → `COMPLETED` | ✅ |
| Confirm `PENDING_PAYMENT` → stays (redirect) | ✅ |
| Other user gets 404 | ✅ |
| Success message on confirm | ✅ |

**Rule:** Only orders with status `DELIVERED` can be confirmed as received.

---

## Order Tracking Timeline

| Scenario | Status |
|---|---|
| Track `PENDING_PAYMENT` order — 200 | ✅ |
| Track `PAID` order — shows "Pembayaran Dikonfirmasi" | ✅ |

---

## Edge Cases

| Scenario | Status |
|---|---|
| Recipient name with 100 characters | ✅ Accepted |
| Phone with formatting `(0812) 3456-7890` | ✅ Accepted (form validation passes due to digit check) |
| Shipping address with newlines | ✅ Preserved |
| Order number format (`ORD-` prefix, date, hex) | ✅ Validated |
| Multiple variants of same product in one order | ✅ Both items created with correct prices |

---

## Existing Tests (Covered by `apps/orders/tests.py`)

The following were already tested in the existing test suite and are not duplicated:

- Order model: `test_order_number_auto_generated`, `test_order_default_status_pending_payment`, `test_str_representation`
- Status history: creation on new/same-status/change, `__str__`
- Basic view tests: list login, detail own/not-owner, cancel pending/non-pending, insufficient stock
- Track view: own/not-owner/login/cancelled
- Form hierarchy: valid/city-not-in-province/district-not-in-city/save-converts-fk
- Voucher flow: apply valid/expired/min-purchase/quota/does-not-create-order, cart detail discount, checkout without/with voucher, expired voucher rejected, usage recorded, discount cap

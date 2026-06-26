# Payment Module — Black-Box Test Report

**Date:** 2026-06-26  
**Test file:** `tests_payment.py`  
**Total tests:** 66  
**Passed:** 66  
**Failed:** 0  
**Duration:** 55.10s  

---

## Test Groups

| Group | Tests | Description |
|---|---|---|
| `TestPaymentCheckout` | 10 | Snap token generation, idempotency, Midtrans error handling, login/auth guards |
| `TestPaymentPending` | 4 | Unfinish page, other-user 404, login required, nonexistent order |
| `TestPaymentSuccess` | 7 | Capture/settlement success, stock deduction, member points, other-user 404, duplicate idempotency |
| `TestPaymentFailure` | 4 | Deny/cancel/expire via finish, raw response saved |
| `TestPaymentError` | 3 | Error page, other-user 404, login required |
| `TestPaymentInvalidSignature` | 1 | Finish view calls Midtrans API (no signature check at finish) |
| `TestPaymentWebhook` | 21 | JSON parsing, missing fields, invalid order, signature, amount mismatch, settlement/capture/deny/cancel/expire/pending, stock/points via webhook, history, duplicate idempotency, ORDER- prefix fallback |
| `TestPaymentOrderStatusUpdate` | 3 | Initial pending status, `_process_successful_payment` sets PAID + paid_at |
| `TestPaymentModel` | 5 | `__str__`, default status, history created on new/save, history on status change, not duplicated, `__str__` format |
| `TestPaymentVerifySignature` | 3 | Valid sig, invalid sig, wrong order_id |
| `TestPaymentParseOrderId` | 4 | With/without prefix, empty string, None |
| `TestPaymentEdgeCases` | 3 | Zero-amount payment, OneToOne duplicate blocked, audit trail, raw response storage |

---

## Checkout — Snap Token

| Scenario | Expected | Actual |
|---|---|---|
| GET without login | 302 redirect | ✅ |
| GET for another user's order | 404 | ✅ |
| GET for already-paid order | 200 + "sudah dibayar" message | ✅ |
| `create_transaction` called, token stored in DB | 200 + token in context | ✅ |
| Existing snap token → `create_transaction` NOT called | 200, existing token preserved | ✅ |
| Midtrans API error → error page rendered | 200 + error message | ✅ |
| Payment record created on first access | 1 Payment row | ✅ |
| Context contains `client_key` | matches `settings.MIDTRANS_CLIENT_KEY` | ✅ |
| GET with nonexistent order | 404 | ✅ |

---

## Pending (Unfinish)

| Scenario | Status |
|---|---|
| Unfinish page loads for own order | ✅ 200 + "Tertunda" |
| Other user's order → 404 | ✅ |
| Requires login → 302 | ✅ |
| Nonexistent order → 404 | ✅ |

---

## Success (Finish)

| Scenario | Status |
|---|---|
| `capture` + `fraud_status=accept` → SUCCESS + PAID | ✅ |
| `settlement` → SUCCESS + PAID, `payment_method` saved | ✅ |
| Stock deducted via `F('stock') - quantity` | ✅ |
| MemberProfile `total_spending` incremented + points earned | ✅ |
| Other user's order → 404 | ✅ |
| Duplicate notification (same order, same status) → stock NOT deducted twice | ✅ |

---

## Failure via Finish

| Scenario | Status |
|---|---|
| `deny` → FAILED + CANCELLED | ✅ |
| `cancel` → FAILED + CANCELLED | ✅ |
| `expire` → FAILED + CANCELLED | ✅ |
| Raw response saved on failure | ✅ |

---

## Error Page

| Scenario | Status |
|---|---|
| Error page loads for own order | ✅ 200 + "Gagal" |
| Other user's order → 404 | ✅ |
| Requires login → 302 | ✅ |

---

## Webhook

| Scenario | Expected | Actual |
|---|---|---|
| Invalid JSON body | 400 | ✅ |
| Missing `order_id` or `transaction_status` | 400 | ✅ |
| Order ID not a valid UUID | 404 | ✅ |
| Order ID with `ORDER-` + invalid UUID | 404 | ✅ |
| Invalid signature key | 403 | ✅ |
| Order not found (valid UUID) | 404 | ✅ |
| Payment not found (order exists, no Payment) | 404 | ✅ |
| Amount mismatch (`gross_amount` != `total_price`) | 400 | ✅ |
| `settlement` → SUCCESS + PAID + `transaction_id` saved | 200 + `OK` | ✅ |
| `capture` + `fraud_status=accept` → SUCCESS | 200 | ✅ |
| `deny` → FAILED + CANCELLED | 200 | ✅ |
| `cancel` → FAILED + CANCELLED | 200 | ✅ |
| `expire` → FAILED + CANCELLED | 200 | ✅ |
| `pending` → PENDING (order unchanged) | 200 | ✅ |
| Stock deducted via webhook settlement | 47 (50 - 3) | ✅ |
| Member points earned via webhook | > 0 + spending updated | ✅ |
| Payment history entry created on webhook success | 2 entries | ✅ |
| Duplicate webhook → stock NOT deducted twice | 49 (not 48) | ✅ |
| Order ID without `ORDER-` prefix → still processed | 200 + SUCCESS | ✅ |

---

## Order Status Update via `_process_successful_payment`

| Scenario | Status |
|---|---|
| Default: payment PENDING, order PENDING_PAYMENT | ✅ |
| `_process_successful_payment` → order PAID + payment SUCCESS | ✅ |
| `_process_successful_payment` → order.paid_at set | ✅ |

---

## Model

| Scenario | Status |
|---|---|
| `__str__` = `Pembayaran #ORD-...` | ✅ |
| Default status = `pending` | ✅ |
| History entry created on new Payment (1 entry: `pending`) | ✅ |
| History entry on status change (2 entries: `success`, `pending` — newest first) | ✅ |
| Saving without status change → no duplicate history | ✅ |
| History `__str__` contains `→` | ✅ |

---

## Signature Verification

| Scenario | Status |
|---|---|
| Valid SHA-512 signature → True | ✅ |
| Invalid hex string → False | ✅ |
| Wrong order_id in signature → False | ✅ |

---

## `_parse_order_id`

| Scenario | Input | Expected | Actual |
|---|---|---|---|
| With `ORDER-` prefix | `ORDER-abc-123` | `abc-123` | ✅ |
| Without prefix | `abc-123` | `abc-123` | ✅ |
| Empty string | `""` | `""` | ✅ |
| `None` | `None` | `None` | ✅ |

---

## Edge Cases

| Scenario | Status |
|---|---|
| Payment with zero amount (free order) — created with PENDING status | ✅ |
| OneToOne constraint — second Payment for same Order raises `IntegrityError` | ✅ |
| Audit trail: 3 status changes (`pending` → `success` → `failed`) yields 3 history entries | ✅ |
| Raw response stored as JSON in `raw_response` field | ✅ |

---

## API Request/Response Summary

### Checkout (`GET /payment/checkout/{id}/`)
- Calls `midtransclient.Snap.create_transaction()` with item details, customer details, callbacks
- Returns rendered checkout template with `snap_token` and `client_key`
- On Midtrans error: renders error template with message

### Finish (`GET /payment/finish/{id}/`)
- Calls `midtransclient.Snap.transactions.status()` to get current transaction status
- `capture`/`settlement` → `_process_successful_payment()` → SUCCESS + PAID + stock/points
- `deny`/`cancel`/`expire` → FAILED + CANCELLED
- Other statuses → default fallback (renders success template)

### Webhook (`POST /payment/notification/`)
- Validates: JSON parse → UUID format → signature (SHA-512) → order exists → payment exists → amount matches
- Status mapping: `capture`+`accept`/`settlement` → SUCCESS; `deny`/`cancel`/`expire` → FAILED; `pending` → PENDING
- Returns HTTP 200 with body `OK` on all successful processing
- Error codes: 400 (bad request/amount), 403 (signature), 404 (not found)

### `_process_successful_payment()` (internal)
```
Transaction atomic:
  1. Set payment.transaction_id, .payment_method, .fraud_status, .raw_response
  2. Parse transaction_time → payment.payment_time
  3. payment.status = SUCCESS, order.status = PAID
  4. If NOT already paid before:
     a. Deduct stock: Product.objects.filter(id=item.product_id).update(stock=F('stock') - quantity)
     b. member.total_spending += total_price
     c. member.earn_points(total_price)
     d. member.upgrade_level()
```

---

## Code Coverage Areas

| Module | Coverage |
|---|---|
| `apps/payments/views.py` (233 lines) | All view functions: `checkout`, `payment_finish`, `payment_unfinish`, `payment_error`, `payment_notification`, `_ensure_order_owner`, `_process_successful_payment`, `_parse_order_id` |
| `apps/payments/models.py` (82 lines) | `Payment.save()` (status history tracking), `PaymentStatusHistory`, all field types |
| `apps/payments/midtrans.py` (73 lines) | `create_transaction`, `get_transaction_status`, `verify_signature` |
| `apps/orders/models.py` | `Order.Status` transitions (PENDING_PAYMENT → PAID/CANCELLED), `midtrans_order_id` |

---

## Status Transition Table

### Payment → Order
| Payment Status | Order Status | Trigger |
|---|---|---|
| `pending` | `pending_payment` | Initial state |
| `success` | `paid` | `_process_successful_payment` |
| `failed` | `cancelled` | `payment_finish` (deny/cancel/expire) or webhook |
| `expired` | `cancelled` | webhook |

### Idempotency
- `_process_successful_payment` checks `was_paid_before` to skip stock/points on re-processing
- Webhook handler calls `_process_successful_payment` which handles duplicate detection
- Stock uses `F('stock') - quantity` (atomic decrement, still guarded by the `was_paid_before` flag)

---

## Bugs Found

### PAY-01: `_ensure_order_owner` causes `DisallowedRedirect` when `LOGIN_URL` is a named URL

**File:** `apps/payments/views.py:69-72`  
**Severity:** Medium  
**Description:** `settings.LOGIN_URL = 'accounts:login'` is a named URL pattern. The redirect string `f'{settings.LOGIN_URL}?next=...'` becomes `'accounts:login?next=...'` which Django's `redirect()` interprets as a URL with protocol `accounts:`, raising `DisallowedRedirect` (status 400).  
**Fix applied:** `redirect(f'{reverse(settings.LOGIN_URL)}?next=...')` and return `Http404` for authenticated non-owners instead of redirecting.

### Test Bugs Logged (awareness only, not app bugs)
- **Order cascade tests:** Model-level `payment.status` changes do NOT cascade to `order.status` — only `_process_successful_payment()` does this. Tests updated to call `_process_successful_payment()` directly.
- **History ordering:** `PaymentStatusHistory.Meta.ordering = ['-created_at']` (newest first). Tests updated to expect `['success', 'pending']` instead of `['pending', 'success']`.

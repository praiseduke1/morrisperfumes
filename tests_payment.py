"""
Comprehensive Black-Box Tests — Payment Module
Tests: Sandbox Payment, Snap Token, Pending, Success, Failure,
      Cancel, Expired, Invalid Signature, Webhook, Order Status Update
"""
import hashlib
import json
import uuid
from datetime import timedelta
from unittest.mock import patch, MagicMock

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from apps.accounts.models import MemberProfile
from apps.orders.models import Order, OrderItem
from apps.orders.forms import CheckoutForm
from apps.payments.models import Payment, PaymentStatusHistory
from apps.payments.views import _process_successful_payment
from apps.products.models import Category, Product


# ============================================================
# Fixtures
# ============================================================
@pytest.fixture
def category():
    return Category.objects.create(name='Parfum', slug='parfum')


@pytest.fixture
def product(category):
    return Product.objects.create(
        name='Test Parfum', slug='test-parfum',
        category=category, price=100000, stock=50, is_available=True,
    )


@pytest.fixture
def customer():
    user = User.objects.create_user(
        username='pelanggan', password='pass123', email='cust@test.com',
    )
    MemberProfile.objects.get_or_create(user=user)
    return user


@pytest.fixture
def other_user():
    return User.objects.create_user(
        username='orang_lain', password='pass123', email='other@test.com',
    )


@pytest.fixture
def logged_client(customer):
    client = Client()
    client.login(username='pelanggan', password='pass123')
    return client


@pytest.fixture
def order(customer):
    return Order.objects.create(
        user=customer, total_price=100000,
        recipient_name='Budi', phone='08123456789',
        shipping_address='Jl. Merdeka No. 10, Jakarta',
        province='Aceh', city='Kab. Simeulue',
        district='Alafan', postal_code='12345',
    )


@pytest.fixture
def order_with_items(customer, product, order):
    OrderItem.objects.create(
        order=order, product=product, product_name=product.name,
        price=product.price, quantity=2,
    )
    return order


@pytest.fixture
def payment(order):
    return Payment.objects.create(
        order=order, snap_token='dummy-snap-token',
        snap_redirect_url='https://app.sandbox.midtrans.com/snap/v1/redir',
        amount=order.total_price,
    )


def _valid_signature(order_id, status_code='200', gross_amount='100000'):
    data = f'{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}'
    return hashlib.sha512(data.encode()).hexdigest()


# ============================================================
# CHECKOUT — SNAP TOKEN
# ============================================================
@pytest.mark.django_db
class TestPaymentCheckout:
    def test_requires_login(self):
        resp = Client().get(reverse('payments:checkout', args=[1]))
        assert resp.status_code == 302

    def test_other_user_404(self, logged_client, order, other_user):
        order2 = Order.objects.create(user=other_user, total_price=50000)
        resp = logged_client.get(reverse('payments:checkout', args=[order2.id]))
        assert resp.status_code == 404

    def test_non_pending_order_shows_error(self, logged_client, order):
        order.status = Order.Status.PAID
        order.save()
        resp = logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert resp.status_code == 200
        assert 'sudah dibayar' in resp.content.decode().lower()

    @patch('apps.payments.views.create_transaction')
    def test_snap_token_generated(self, mock_create, logged_client, order):
        mock_create.return_value = {
            'token': 'snap-token-12345',
            'redirect_url': 'https://app.sandbox.midtrans.com/snap/v1/redir/abc',
        }
        resp = logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert resp.status_code == 200
        payment = Payment.objects.get(order=order)
        assert payment.snap_token == 'snap-token-12345'
        assert 'snap-token-12345' in resp.content.decode()
        assert payment.amount == order.total_price

    @patch('apps.payments.views.create_transaction')
    def test_snap_token_not_regenerated(self, mock_create, logged_client, order, payment):
        resp = logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert resp.status_code == 200
        mock_create.assert_not_called()
        payment.refresh_from_db()
        assert payment.snap_token == 'dummy-snap-token'

    @patch('apps.payments.views.create_transaction')
    def test_midtrans_error_shows_error_page(self, mock_create, logged_client, order):
        mock_create.side_effect = Exception('Connection timeout')
        resp = logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert resp.status_code == 200
        content = resp.content.decode()
        assert 'Gagal terhubung' in content or 'error' in content.lower()

    @patch('apps.payments.views.create_transaction')
    def test_payment_created_on_first_access(self, mock_create, logged_client, order):
        mock_create.return_value = {
            'token': 'snap-token-abc',
            'redirect_url': 'https://app.sandbox.midtrans.com/snap/v1/redir/abc',
        }
        assert Payment.objects.filter(order=order).count() == 0
        logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert Payment.objects.filter(order=order).count() == 1

    @patch('apps.payments.views.create_transaction')
    def test_checkout_context_contains_client_key(self, mock_create, logged_client, order):
        mock_create.return_value = {
            'token': 'snap-token-abc',
            'redirect_url': 'https://app.sandbox.midtrans.com/snap/v1/redir/abc',
        }
        resp = logged_client.get(reverse('payments:checkout', args=[order.id]))
        assert resp.context['client_key'] == settings.MIDTRANS_CLIENT_KEY

    def test_checkout_without_order_404(self, logged_client):
        resp = logged_client.get(reverse('payments:checkout', args=[99999]))
        assert resp.status_code == 404


# ============================================================
# PAYMENT — PENDING (UNFINISH)
# ============================================================
@pytest.mark.django_db
class TestPaymentPending:
    def test_unfinish_page_loads(self, logged_client, order):
        resp = logged_client.get(reverse('payments:unfinish', args=[order.id]))
        assert resp.status_code == 200
        assert 'Tertunda' in resp.content.decode()

    def test_unfinish_other_user_404(self, logged_client, other_user):
        order2 = Order.objects.create(user=other_user, total_price=50000)
        resp = logged_client.get(reverse('payments:unfinish', args=[order2.id]))
        assert resp.status_code == 404

    def test_unfinish_requires_login(self, order):
        resp = Client().get(reverse('payments:unfinish', args=[order.id]))
        assert resp.status_code == 302

    def test_unfinish_nonexistent_order(self, logged_client):
        resp = logged_client.get(reverse('payments:unfinish', args=[99999]))
        assert resp.status_code == 404


# ============================================================
# PAYMENT — SUCCESS (FINISH)
# ============================================================
@pytest.mark.django_db
class TestPaymentSuccess:
    @patch('apps.payments.views.get_transaction_status')
    def test_capture_success(self, mock_status, logged_client, customer, order, payment):
        mock_status.return_value = {
            'transaction_status': 'capture',
            'fraud_status': 'accept',
            'transaction_id': 'trx-capture-001',
            'payment_type': 'credit_card',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        resp = logged_client.get(reverse('payments:finish', args=[order.id]))
        assert resp.status_code == 200
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.SUCCESS
        assert order.status == Order.Status.PAID
        assert payment.transaction_id == 'trx-capture-001'

    @patch('apps.payments.views.get_transaction_status')
    def test_settlement_success(self, mock_status, logged_client, customer, order, payment):
        mock_status.return_value = {
            'transaction_status': 'settlement',
            'transaction_id': 'trx-settlement-001',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        resp = logged_client.get(reverse('payments:finish', args=[order.id]))
        assert resp.status_code == 200
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.SUCCESS
        assert order.status == Order.Status.PAID
        assert payment.payment_method == 'bank_transfer'

    @patch('apps.payments.views.get_transaction_status')
    def test_success_stock_deducted(self, mock_status, logged_client, customer, product, order, payment):
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            price=product.price, quantity=2,
        )
        mock_status.return_value = {
            'transaction_status': 'settlement',
            'transaction_id': 'trx-stock-001',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        logged_client.get(reverse('payments:finish', args=[order.id]))
        product.refresh_from_db()
        assert product.stock == 48  # 50 - 2

    @patch('apps.payments.views.get_transaction_status')
    def test_success_member_points_earned(self, mock_status, logged_client, customer, order, payment):
        mock_status.return_value = {
            'transaction_status': 'settlement',
            'transaction_id': 'trx-pts-001',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        member = MemberProfile.objects.get(user=customer)
        member.total_spending = 0
        member.total_points = 0
        member.save()
        logged_client.get(reverse('payments:finish', args=[order.id]))
        member.refresh_from_db()
        assert member.total_spending == order.total_price
        assert member.total_points > 0

    @patch('apps.payments.views.get_transaction_status')
    def test_success_other_user_404(self, mock_status, logged_client, other_user, order, payment):
        order2 = Order.objects.create(user=other_user, total_price=50000)
        payment2 = Payment.objects.create(order=order2, amount=50000)
        mock_status.return_value = {'transaction_status': 'settlement'}
        resp = logged_client.get(reverse('payments:finish', args=[order2.id]))
        assert resp.status_code == 404

    @patch('apps.payments.views.get_transaction_status')
    def test_duplicate_notification_idempotent(self, mock_status, logged_client, customer, product, order, payment):
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            price=product.price, quantity=2,
        )
        mock_status.return_value = {
            'transaction_status': 'settlement',
            'transaction_id': 'trx-dup-001',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        logged_client.get(reverse('payments:finish', args=[order.id]))
        product.refresh_from_db()
        assert product.stock == 48
        logged_client.get(reverse('payments:finish', args=[order.id]))
        product.refresh_from_db()
        assert product.stock == 48  # not 46


# ============================================================
# PAYMENT — FAILURE (DENY / CANCEL / EXPIRE via FINISH)
# ============================================================
@pytest.mark.django_db
class TestPaymentFailure:
    @patch('apps.payments.views.get_transaction_status')
    def test_deny_via_finish(self, mock_status, logged_client, order, payment):
        mock_status.return_value = {'transaction_status': 'deny'}
        resp = logged_client.get(reverse('payments:finish', args=[order.id]))
        assert resp.status_code == 200
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        assert order.status == Order.Status.CANCELLED

    @patch('apps.payments.views.get_transaction_status')
    def test_cancel_via_finish(self, mock_status, logged_client, order, payment):
        mock_status.return_value = {'transaction_status': 'cancel'}
        logged_client.get(reverse('payments:finish', args=[order.id]))
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        assert order.status == Order.Status.CANCELLED

    @patch('apps.payments.views.get_transaction_status')
    def test_expire_via_finish(self, mock_status, logged_client, order, payment):
        mock_status.return_value = {'transaction_status': 'expire'}
        logged_client.get(reverse('payments:finish', args=[order.id]))
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        assert order.status == Order.Status.CANCELLED

    @patch('apps.payments.views.get_transaction_status')
    def test_failure_raw_response_saved(self, mock_status, logged_client, order, payment):
        raw = {'transaction_status': 'deny', 'status_code': '202'}
        mock_status.return_value = raw
        logged_client.get(reverse('payments:finish', args=[order.id]))
        payment.refresh_from_db()
        assert payment.raw_response == raw


# ============================================================
# PAYMENT — ERROR PAGE
# ============================================================
@pytest.mark.django_db
class TestPaymentError:
    def test_error_page_loads(self, logged_client, order):
        resp = logged_client.get(reverse('payments:error', args=[order.id]))
        assert resp.status_code == 200
        assert 'Gagal' in resp.content.decode()

    def test_error_other_user_404(self, logged_client, other_user):
        order2 = Order.objects.create(user=other_user, total_price=50000)
        resp = logged_client.get(reverse('payments:error', args=[order2.id]))
        assert resp.status_code == 404

    def test_error_requires_login(self, order):
        resp = Client().get(reverse('payments:error', args=[order.id]))
        assert resp.status_code == 302


# ============================================================
# PAYMENT — INVALID SIGNATURE
# ============================================================
@pytest.mark.django_db
class TestPaymentInvalidSignature:
    def test_finish_invalid_signature_still_proceeds(self, logged_client, order, payment):
        """Finish view calls Midtrans API directly, not signature verification."""
        with patch('apps.payments.views.get_transaction_status') as mock_status:
            mock_status.return_value = {'transaction_status': 'settlement', 'transaction_id': 'trx-001'}
            resp = logged_client.get(reverse('payments:finish', args=[order.id]))
            assert resp.status_code == 200


# ============================================================
# WEBHOOK — NOTIFICATION
# ============================================================
@pytest.mark.django_db
class TestPaymentWebhook:
    def _post(self, data):
        return Client().post(
            reverse('payments:notification'),
            data=json.dumps(data),
            content_type='application/json',
        )

    def _order_id(self, order):
        return f'ORDER-{order.midtrans_order_id}'

    def _sig(self, order_id, status_code='200', gross_amount='100000'):
        return _valid_signature(order_id, status_code, gross_amount)

    # --- Invalid input ---

    def test_invalid_json(self):
        resp = Client().post(
            reverse('payments:notification'),
            data='not json',
            content_type='application/json',
        )
        assert resp.status_code == 400

    def test_missing_fields(self):
        resp = self._post({})
        assert resp.status_code == 400

    def test_invalid_order_id(self):
        data = {
            'order_id': 'not-a-uuid',
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': '100000',
            'signature_key': 'some-sig',
        }
        resp = self._post(data)
        assert resp.status_code == 404

    def test_invalid_uuid_format(self):
        data = {
            'order_id': 'ORDER-not-a-valid-uuid',
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': '100000',
            'signature_key': 'some-sig',
        }
        resp = self._post(data)
        assert resp.status_code == 404

    def test_invalid_signature(self):
        data = {
            'order_id': f'ORDER-{uuid.uuid4()}',
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': '100000',
            'signature_key': 'invalid-sig',
        }
        resp = self._post(data)
        assert resp.status_code == 403

    def test_order_not_found(self):
        oid = f'ORDER-{uuid.uuid4()}'
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': '100000',
            'signature_key': self._sig(oid),
        }
        resp = self._post(data)
        assert resp.status_code == 404

    def test_payment_not_found(self, order):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 404
        assert 'Pembayaran' not in resp.content.decode() or resp.status_code == 404

    def test_amount_mismatch(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': '999999',
            'signature_key': self._sig(oid, gross_amount='999999'),
        }
        resp = self._post(data)
        assert resp.status_code == 400

    # --- Settlement success ---

    def test_settlement_success(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'transaction_id': 'trx-webhook-001',
            'payment_type': 'bank_transfer',
            'fraud_status': 'accept',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        assert resp.content == b'OK'
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.SUCCESS
        assert order.status == Order.Status.PAID
        assert payment.transaction_id == 'trx-webhook-001'

    def test_capture_with_fraud_accept(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'capture',
            'fraud_status': 'accept',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'transaction_id': 'trx-capture-webhook',
            'payment_type': 'credit_card',
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.SUCCESS

    # --- Deny / Cancel / Expire ---

    def test_deny(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'deny',
            'status_code': '202',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, '202', str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        order.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        assert order.status == Order.Status.CANCELLED

    def test_cancel(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'cancel',
            'status_code': '202',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, '202', str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_expire(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'expire',
            'status_code': '202',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, '202', str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.FAILED
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    # --- Pending ---

    def test_pending(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'pending',
            'status_code': '201',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, '201', str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.PENDING
        order.refresh_from_db()
        assert order.status == Order.Status.PENDING_PAYMENT  # unchanged

    # --- Stock deduction via webhook ---

    def test_webhook_stock_deducted(self, order, payment, product):
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            price=product.price, quantity=3,
        )
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        self._post(data)
        product.refresh_from_db()
        assert product.stock == 47  # 50 - 3

    # --- Member points via webhook ---

    def test_webhook_member_points(self, order, payment, customer):
        member = MemberProfile.objects.get(user=customer)
        member.total_spending = 0
        member.total_points = 0
        member.save()
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        self._post(data)
        member.refresh_from_db()
        assert member.total_spending == order.total_price
        assert member.total_points > 0

    # --- Payment history created ---

    def test_webhook_payment_history(self, order, payment):
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        assert payment.status_history.count() == 1
        self._post(data)
        assert payment.status_history.count() == 2
        latest = payment.status_history.order_by('-created_at').first()
        assert latest.to_status == Payment.PaymentStatus.SUCCESS

    # --- Duplicate webhook idempotent ---

    def test_duplicate_webhook_idempotent(self, order, payment, product):
        OrderItem.objects.create(
            order=order, product=product, product_name=product.name,
            price=product.price, quantity=1,
        )
        oid = self._order_id(order)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': self._sig(oid, gross_amount=str(int(order.total_price))),
        }
        self._post(data)
        product.refresh_from_db()
        assert product.stock == 49
        self._post(data)
        product.refresh_from_db()
        assert product.stock == 49  # not 48

    # --- ORDER- prefix handling ---

    def test_without_order_prefix(self, order, payment):
        """Webhook should handle order_id with or without ORDER- prefix."""
        oid = str(order.midtrans_order_id)
        data = {
            'order_id': oid,
            'transaction_status': 'settlement',
            'status_code': '200',
            'gross_amount': str(int(order.total_price)),
            'signature_key': _valid_signature(oid, gross_amount=str(int(order.total_price))),
        }
        resp = self._post(data)
        assert resp.status_code == 200
        payment.refresh_from_db()
        assert payment.status == Payment.PaymentStatus.SUCCESS


# ============================================================
# ORDER — STATUS UPDATE AFTER PAYMENT
# ============================================================
@pytest.mark.django_db
class TestPaymentOrderStatusUpdate:
    def test_payment_pending_order_pending(self, order, payment):
        assert payment.status == Payment.PaymentStatus.PENDING
        assert order.status == Order.Status.PENDING_PAYMENT

    def test_process_successful_payment_order_paid(self, order, payment):
        _process_successful_payment(payment, order, {
            'transaction_id': 'trx-001',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        order.refresh_from_db()
        payment.refresh_from_db()
        assert order.status == Order.Status.PAID
        assert payment.status == Payment.PaymentStatus.SUCCESS

    def test_process_successful_payment_paid_at(self, order, payment):
        _process_successful_payment(payment, order, {
            'transaction_id': 'trx-002',
            'payment_type': 'bank_transfer',
            'transaction_time': now().strftime('%Y-%m-%d %H:%M:%S'),
        })
        order.refresh_from_db()
        assert order.paid_at is not None


# ============================================================
# PAYMENT — MODEL
# ============================================================
@pytest.mark.django_db
class TestPaymentModel:
    def test_str_representation(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        assert str(payment) == f'Pembayaran #{order.order_number}'

    def test_default_status(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        assert payment.status == Payment.PaymentStatus.PENDING

    def test_status_history_created_on_new(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        assert payment.status_history.count() == 1
        assert payment.status_history.first().to_status == Payment.PaymentStatus.PENDING

    def test_status_history_on_status_change(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.save()
        assert payment.status_history.count() == 2
        statuses = list(payment.status_history.values_list('to_status', flat=True))
        assert statuses == ['success', 'pending']

    def test_status_history_not_duplicated(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        payment.save()
        assert payment.status_history.count() == 1

    def test_status_history_str(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        h = payment.status_history.first()
        assert '→' in str(h)


# ============================================================
# VERIFY SIGNATURE — UNIT
# ============================================================
@pytest.mark.django_db
class TestPaymentVerifySignature:
    def test_valid_signature(self):
        from apps.payments.midtrans import verify_signature
        order_id = 'ORDER-test'
        status_code = '200'
        gross_amount = '100000'
        data = f'{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}'
        valid_sig = hashlib.sha512(data.encode()).hexdigest()
        assert verify_signature(order_id, status_code, gross_amount, valid_sig) is True

    def test_invalid_signature(self):
        from apps.payments.midtrans import verify_signature
        assert verify_signature('ORDER-test', '200', '100000', 'invalid') is False

    def test_different_order_id_fails(self):
        from apps.payments.midtrans import verify_signature
        data = f'ORDER-real200100000{settings.MIDTRANS_SERVER_KEY}'
        sig = hashlib.sha512(data.encode()).hexdigest()
        assert verify_signature('ORDER-fake', '200', '100000', sig) is False


# ============================================================
# PARSE ORDER ID
# ============================================================
@pytest.mark.django_db
class TestPaymentParseOrderId:
    def test_with_prefix(self):
        from apps.payments.views import _parse_order_id
        result = _parse_order_id('ORDER-abc-123')
        assert result == 'abc-123'

    def test_without_prefix(self):
        from apps.payments.views import _parse_order_id
        result = _parse_order_id('abc-123')
        assert result == 'abc-123'

    def test_empty_string(self):
        from apps.payments.views import _parse_order_id
        assert _parse_order_id('') == ''

    def test_none(self):
        from apps.payments.views import _parse_order_id
        assert _parse_order_id(None) is None


# ============================================================
# EDGE CASES
# ============================================================
@pytest.mark.django_db
class TestPaymentEdgeCases:
    def test_payment_with_zero_amount(self, customer):
        order = Order.objects.create(user=customer, total_price=0)
        payment = Payment.objects.create(order=order, amount=0)
        assert payment.amount == 0
        assert payment.status == Payment.PaymentStatus.PENDING

    def test_multiple_payments_same_order_blocked(self, order):
        Payment.objects.create(order=order, amount=100000)
        with pytest.raises(Exception):
            Payment.objects.create(order=order, amount=200000)

    def test_payment_history_audit_trail(self, order):
        payment = Payment.objects.create(order=order, amount=100000)
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.save()
        payment.status = Payment.PaymentStatus.FAILED
        payment.save()
        assert payment.status_history.count() == 3
        statuses = list(payment.status_history.values_list('to_status', flat=True))
        assert statuses == ['failed', 'success', 'pending']

    def test_raw_response_stored(self, order):
        raw = {'key': 'value', 'nested': {'a': 1}}
        payment = Payment.objects.create(order=order, amount=100000, raw_response=raw)
        assert payment.raw_response == raw

import pytest
import json
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.products.models import Category, Product
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment


@pytest.mark.django_db
class TestPaymentModel:
    def test_payment_creation(self):
        user = User.objects.create_user(username='testuser', password='pass12345')
        order = Order.objects.create(user=user, total_price=100000)
        payment = Payment.objects.create(
            order=order,
            snap_token='snap-token-abc',
            transaction_id='trx-123',
            status='settlement',
            payment_method='credit_card',
            amount=100000,
            raw_response={'status_code': '200'},
        )
        assert str(payment) == f'Pembayaran #{order.order_number}'


@pytest.mark.django_db
class TestPaymentViews:
    def test_checkout_page_requires_login(self):
        client = Client()
        response = client.get(reverse('payments:checkout', args=[1]))
        assert response.status_code == 302

    def test_success_page(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        order = Order.objects.create(user=user, total_price=100000)
        Payment.objects.create(order=order)
        client.force_login(user)
        response = client.get(reverse('payments:finish', args=[order.id]))
        assert response.status_code == 200

    def test_unfinish_page(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        order = Order.objects.create(user=user, total_price=100000)
        client.force_login(user)
        response = client.get(reverse('payments:unfinish', args=[order.id]))
        assert response.status_code == 200

    def test_error_page(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        order = Order.objects.create(user=user, total_price=100000)
        client.force_login(user)
        response = client.get(reverse('payments:error', args=[order.id]))
        assert response.status_code == 200

    def test_notification_unauthenticated(self):
        client = Client()
        response = client.post(
            reverse('payments:notification'),
            data=json.dumps({'order_id': 'ORD-123', 'status_code': '200', 'gross_amount': '100000.00', 'signature_key': 'test'}),
            content_type='application/json',
        )
        assert response.status_code == 400

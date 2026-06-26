"""
Comprehensive Black-Box Tests — Order / Checkout Module
Tests: Address selection, Shipping, Voucher calculation, Total price,
      Checkout validation, Order creation, Order detail, Order history,
      Cancel order, Confirm received, Edge cases.
"""
import pytest
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from apps.accounts.models import Profile, MemberProfile, CustomerAddress
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.orders.forms import CheckoutForm
from apps.carts.models import Cart, CartItem
from apps.products.models import Category, Product, ProductVariant
from apps.regions.models import Province, City, District, PostalCode
from apps.promotions.models import Voucher, UserVoucher


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
def cheap_product(category):
    return Product.objects.create(
        name='Cheap Parfum', slug='cheap-parfum',
        category=category, price=25000, stock=50, is_available=True,
    )


@pytest.fixture
def variant_product(category):
    prod = Product.objects.create(
        name='Variant Parfum', slug='variant-parfum',
        category=category, price=0, stock=0, is_available=True,
    )
    ProductVariant.objects.create(
        product=prod, size_ml=50, price=75000, stock=30,
        sku='VRP-50', is_available=True,
    )
    ProductVariant.objects.create(
        product=prod, size_ml=100, price=120000, stock=20,
        sku='VRP-100', is_available=True,
    )
    return prod


@pytest.fixture
def customer():
    user = User.objects.create_user(
        username='pelanggan', password='pass123', email='cust@test.com',
    )
    profile = Profile.objects.get(user=user)
    profile.phone = '08123456789'
    profile.save()
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
def location():
    prov = Province.objects.create(code='11', name='Aceh')
    city = City.objects.create(code='1101', name='Kab. Simeulue', province=prov)
    dist = District.objects.create(code='110101', name='Alafan', city=city)
    pc = PostalCode.objects.create(code='12345', district=dist)
    return {'province': prov, 'city': city, 'district': dist, 'postal_code': pc}


@pytest.fixture
def cart_with_items(customer, product):
    cart = Cart.objects.create(user=customer)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.fixture
def cart_multi_items(customer, product, cheap_product):
    cart = Cart.objects.create(user=customer)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    CartItem.objects.create(cart=cart, product=cheap_product, quantity=3)
    return cart


@pytest.fixture
def address(customer, location):
    return CustomerAddress.objects.create(
        user=customer,
        recipient_name='Budi',
        phone='08123456789',
        address_line='Jl. Merdeka No. 10, Jakarta Pusat',
        province=location['province'],
        city=location['city'],
        district=location['district'],
        postal_code=location['postal_code'],
        label='Rumah',
        is_default=True,
    )


@pytest.fixture
def voucher_percent():
    return Voucher.objects.create(
        code='PCT20',
        description='20% off',
        discount_type=Voucher.DiscountType.PERCENTAGE,
        discount_amount=20,
        min_purchase=0,
        max_discount=50000,
        quota=0,
        start_date=now().date() - timedelta(days=1),
        expired_date=now().date() + timedelta(days=30),
        is_active=True,
        voucher_type=Voucher.Type.PUBLIC,
    )


@pytest.fixture
def voucher_fixed():
    return Voucher.objects.create(
        code='FIXED50',
        description='Rp 50.000 off',
        discount_type=Voucher.DiscountType.FIXED,
        discount_amount=50000,
        min_purchase=0,
        quota=0,
        start_date=now().date() - timedelta(days=1),
        expired_date=now().date() + timedelta(days=30),
        is_active=True,
        voucher_type=Voucher.Type.PUBLIC,
    )


# ============================================================
# CHECKOUT — ADDRESS SELECTION
# ============================================================
@pytest.mark.django_db
class TestCheckoutAddressSelection:
    def test_get_prefills_from_default_address(self, logged_client, customer, cart_with_items, address, location):
        resp = logged_client.get(reverse('orders:create'))
        assert resp.status_code == 200
        form = resp.context['form']
        assert form.initial['recipient_name'] == address.recipient_name
        assert form.initial['phone'] == address.phone
        assert form.initial['shipping_address'] == address.address_line
        assert form.initial['province'] == address.province_id
        assert form.initial['city'] == address.city_id
        assert form.initial['district'] == address.district_id
        assert form.initial['postal_code'] == address.postal_code_id

    def test_get_prefills_from_profile_when_no_address(self, logged_client, customer, cart_with_items):
        resp = logged_client.get(reverse('orders:create'))
        assert resp.status_code == 200
        form = resp.context['form']
        assert form.initial['recipient_name'] == customer.username
        assert form.initial['phone'] == '08123456789'

    def test_get_lists_addresses_in_context(self, logged_client, customer, cart_with_items, address):
        resp = logged_client.get(reverse('orders:create'))
        assert resp.status_code == 200
        assert 'addresses' in resp.context
        assert address in resp.context['addresses']

    def test_get_requires_login(self, customer, cart_with_items):
        resp = Client().get(reverse('orders:create'))
        assert resp.status_code == 302

    def test_get_redirects_when_cart_empty(self, logged_client, customer):
        resp = logged_client.get(reverse('orders:create'), follow=True)
        messages_list = list(resp.context['messages'])
        assert any('kosong' in str(m) for m in messages_list)


# ============================================================
# CHECKOUT — SHIPPING (FREE)
# ============================================================
@pytest.mark.django_db
class TestCheckoutShipping:
    def test_no_shipping_cost_field_on_order(self):
        """Order model has no shipping_cost field — shipping is free."""
        fields = [f.name for f in Order._meta.get_fields()]
        assert 'shipping_cost' not in fields
        assert 'shipping_fee' not in fields

    def test_total_equals_subtotal_minus_discount(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        assert order.total_price == order.subtotal - order.discount_amount


# ============================================================
# CHECKOUT — VOUCHER CALCULATION
# ============================================================
@pytest.mark.django_db
class TestCheckoutVoucherCalculation:
    def test_percentage_discount_applied(self, logged_client, customer, cart_with_items, location, voucher_percent):
        session = logged_client.session
        session['voucher_code'] = 'PCT20'
        session.save()
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        # subtotal = 2 x 100000 = 200000
        # discount = 20% of 200000 = 40000, capped at max_discount 50000 = 40000
        assert order.subtotal == 200000
        assert order.discount_amount == 40000
        assert order.total_price == 160000

    def test_percentage_discount_capped_by_max_discount(self, logged_client, customer, cart_with_items, location):
        Voucher.objects.create(
            code='PCT50', discount_type=Voucher.DiscountType.PERCENTAGE,
            discount_amount=50, max_discount=30000,
            min_purchase=0, quota=0,
            start_date=now().date() - timedelta(days=1),
            expired_date=now().date() + timedelta(days=30),
            is_active=True, voucher_type=Voucher.Type.PUBLIC,
        )
        session = logged_client.session
        session['voucher_code'] = 'PCT50'
        session.save()
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        # 50% of 200000 = 100000, but max_discount = 30000
        assert order.discount_amount == 30000
        assert order.total_price == 170000

    def test_fixed_discount_applied(self, logged_client, customer, cart_with_items, location, voucher_fixed):
        session = logged_client.session
        session['voucher_code'] = 'FIXED50'
        session.save()
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        # subtotal = 200000, fixed discount = 50000
        assert order.discount_amount == 50000
        assert order.total_price == 150000

    def test_discount_capped_at_subtotal(self, logged_client, customer, cart_with_items, location):
        Voucher.objects.create(
            code='BIGFIX', discount_type=Voucher.DiscountType.FIXED,
            discount_amount=999999,
            min_purchase=0, quota=0,
            start_date=now().date() - timedelta(days=1),
            expired_date=now().date() + timedelta(days=30),
            is_active=True, voucher_type=Voucher.Type.PUBLIC,
        )
        session = logged_client.session
        session['voucher_code'] = 'BIGFIX'
        session.save()
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        assert order.discount_amount == 200000
        assert order.total_price == 0

    def test_voucher_context_on_get(self, logged_client, customer, cart_with_items, voucher_percent):
        session = logged_client.session
        session['voucher_code'] = 'PCT20'
        session.save()
        resp = logged_client.get(reverse('orders:create'))
        assert resp.status_code == 200
        assert resp.context['voucher_code'] == 'PCT20'
        assert resp.context['discount_amount'] == 40000
        assert resp.context['final_total'] == 160000

    def test_invalid_voucher_cleared_on_get(self, logged_client, customer, cart_with_items):
        session = logged_client.session
        session['voucher_code'] = 'INVALID'
        session.save()
        resp = logged_client.get(reverse('orders:create'))
        assert resp.context['voucher_code'] == ''
        assert resp.context['discount_amount'] == 0

    def test_voucher_marked_used_via_uservoucher(self, logged_client, customer, cart_with_items, location, voucher_percent):
        uv = UserVoucher.objects.create(
            user=customer, voucher=voucher_percent,
            status=UserVoucher.Status.AVAILABLE,
            expires_at=now() + timedelta(days=30),
        )
        session = logged_client.session
        session['voucher_code'] = 'PCT20'
        session.save()
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        uv.refresh_from_db()
        assert uv.status == UserVoucher.Status.USED
        assert uv.used_at is not None

    def test_voucher_used_count_incremented_when_no_uservoucher(self, logged_client, customer, cart_with_items, location, voucher_percent):
        session = logged_client.session
        session['voucher_code'] = 'PCT20'
        session.save()
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        voucher_percent.refresh_from_db()
        assert voucher_percent.used_count == 1

    def test_session_voucher_cleared_after_order(self, logged_client, customer, cart_with_items, location, voucher_percent):
        session = logged_client.session
        session['voucher_code'] = 'PCT20'
        session.save()
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        session = logged_client.session
        assert 'voucher_code' not in session


# ============================================================
# CHECKOUT — TOTAL PRICE
# ============================================================
@pytest.mark.django_db
class TestCheckoutTotalPrice:
    def test_no_voucher_subtotal_equals_total(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        assert order.subtotal == 200000
        assert order.discount_amount == 0
        assert order.total_price == 200000

    def test_total_with_multiple_items(self, logged_client, customer, cart_multi_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        # 1x100000 + 3x25000 = 100000 + 75000 = 175000
        assert order.subtotal == 175000
        assert order.total_price == 175000

    def test_total_voucher_and_multiple_items(self, logged_client, customer, cart_multi_items, location):
        Voucher.objects.create(
            code='FIXED30', discount_type=Voucher.DiscountType.FIXED,
            discount_amount=30000, min_purchase=0, quota=0,
            start_date=now().date() - timedelta(days=1),
            expired_date=now().date() + timedelta(days=30),
            is_active=True, voucher_type=Voucher.Type.PUBLIC,
        )
        session = logged_client.session
        session['voucher_code'] = 'FIXED30'
        session.save()
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.get(user=customer)
        assert order.subtotal == 175000
        assert order.discount_amount == 30000
        assert order.total_price == 145000


# ============================================================
# CHECKOUT — FORM VALIDATION
# ============================================================
@pytest.mark.django_db
class TestCheckoutFormValidation:
    def test_valid_form(self, location):
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123456789',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert form.is_valid(), form.errors

    def test_phone_not_starting_with_08(self, location):
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '1234567890',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_phone_too_short(self, location):
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert not form.is_valid()
        assert 'phone' in form.errors

    def test_shipping_address_too_short(self, location):
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123456789',
            'shipping_address': 'Short',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert not form.is_valid()
        assert 'shipping_address' in form.errors

    def test_missing_required_fields(self):
        form = CheckoutForm(data={})
        assert not form.is_valid()
        assert 'recipient_name' in form.errors
        assert 'phone' in form.errors
        assert 'shipping_address' in form.errors
        assert 'province' in form.errors
        assert 'city' in form.errors
        assert 'district' in form.errors
        assert 'postal_code' in form.errors

    def test_city_not_in_province_rejected(self, location):
        other_prov = Province.objects.create(code='12', name='Sumatera Utara')
        orphan_city = City.objects.create(code='1201', name='Orphan', province=other_prov)
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123456789',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': orphan_city.id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert not form.is_valid()
        assert 'city' in form.errors

    def test_district_not_in_city_rejected(self, location):
        other_city = City.objects.create(code='1199', name='Other', province=location['province'])
        orphan_dist = District.objects.create(code='119901', name='Orphan', city=other_city)
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123456789',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': orphan_dist.id,
            'postal_code': location['postal_code'].id,
        })
        assert not form.is_valid()
        assert 'district' in form.errors

    def test_postal_code_not_in_district_rejected(self, location):
        other_dist = District.objects.create(code='110102', name='Other', city=location['city'])
        orphan_pc = PostalCode.objects.create(code='99999', district=other_dist)
        form = CheckoutForm(data={
            'recipient_name': 'Test', 'phone': '08123456789',
            'shipping_address': 'Jl. Test No. 10 Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': orphan_pc.id,
        })
        assert not form.is_valid()
        assert 'postal_code' in form.errors

    def test_form_errors_rendered_on_post(self, logged_client, customer, cart_with_items):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': '', 'phone': '123', 'shipping_address': 'S',
        })
        assert resp.status_code == 200
        assert 'form' in resp.context
        assert resp.context['form'].errors


# ============================================================
# ORDER — CREATION
# ============================================================
@pytest.mark.django_db
class TestOrderCreation:
    def test_order_created_successfully(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        assert Order.objects.count() == 1
        order = Order.objects.first()
        assert order.user == customer
        assert order.order_number.startswith('ORD-')

    def test_order_items_created(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.items.count() == 1
        item = order.items.first()
        assert item.product_name == 'Test Parfum'
        assert item.price == 100000
        assert item.quantity == 2
        assert item.total_price() == 200000

    def test_cart_cleared_after_order(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        cart = Cart.objects.get(user=customer)
        assert cart.items.count() == 0

    def test_redirects_to_payment_checkout(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert resp.url.startswith(reverse('payments:checkout', args=[order.id]))

    def test_order_address_saved_as_text(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.recipient_name == 'Budi'
        assert order.phone == '08123456789'
        assert order.shipping_address == 'Jl. Merdeka No. 10, Jakarta'
        assert order.province == 'Aceh'
        assert order.city == 'Kab. Simeulue'
        assert order.district == 'Alafan'
        assert order.postal_code == '12345'

    def test_order_default_status(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.status == Order.Status.PENDING_PAYMENT

    def test_status_history_created(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.status_history.count() == 1
        assert order.status_history.first().status == Order.Status.PENDING_PAYMENT

    def test_insufficient_stock_rejected(self, logged_client, customer, product, location):
        product.stock = 1
        product.save()
        cart = Cart.objects.create(user=customer)
        CartItem.objects.create(cart=cart, product=product, quantity=3)
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        assert Order.objects.count() == 0

    def test_variant_product_order_items(self, logged_client, customer, variant_product, location):
        cart = Cart.objects.create(user=customer)
        variant = ProductVariant.objects.get(product=variant_product, size_ml=100)
        CartItem.objects.create(cart=cart, product=variant_product, variant=variant, quantity=2)
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.items.count() == 1
        item = order.items.first()
        assert item.product_name == 'Variant Parfum'
        assert item.variant_name == '100ml'
        assert item.price == 120000
        assert item.quantity == 2

    def test_empty_cart_on_post_redirects(self, logged_client, customer):
        Cart.objects.create(user=customer)
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
        })
        assert resp.status_code == 302
        assert Order.objects.count() == 0

    def test_success_message_on_creation(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        }, follow=True)
        messages_list = list(resp.context['messages'])
        assert any('berhasil' in str(m) for m in messages_list)

    def test_notes_saved(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
            'notes': 'Tolong dibungkus kado',
        })
        assert resp.status_code == 302
        order = Order.objects.first()
        assert order.notes == 'Tolong dibungkus kado'


# ============================================================
# ORDER — DETAIL
# ============================================================
@pytest.mark.django_db
class TestOrderDetail:
    def test_detail_shows_order_info(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.get(reverse('orders:detail', args=[order.id]))
        assert resp.status_code == 200
        assert order.order_number in resp.content.decode()

    def test_detail_shows_items(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.get(reverse('orders:detail', args=[order.id]))
        content = resp.content.decode()
        assert 'Test Parfum' in content
        assert '2' in content

    def test_detail_other_user_404(self, logged_client, customer, other_user, product, location):
        other_cart = Cart.objects.create(user=other_user)
        CartItem.objects.create(cart=other_cart, product=product, quantity=1)
        other_client = Client()
        other_client.login(username='orang_lain', password='pass123')
        other_client.post(reverse('orders:create'), {
            'recipient_name': 'Other', 'phone': '08123456789',
            'shipping_address': 'Jl. Other No. 1, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        other_order = Order.objects.get(user=other_user)
        resp = logged_client.get(reverse('orders:detail', args=[other_order.id]))
        assert resp.status_code == 404

    def test_detail_requires_login(self, customer, cart_with_items, location):
        logged_client = Client()
        logged_client.login(username='pelanggan', password='pass123')
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = Client().get(reverse('orders:detail', args=[order.id]))
        assert resp.status_code == 302

    def test_detail_shows_status_badge(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.get(reverse('orders:detail', args=[order.id]))
        content = resp.content.decode()
        assert 'Pending' in content or 'pending' in content.lower()


# ============================================================
# ORDER — HISTORY
# ============================================================
@pytest.mark.django_db
class TestOrderHistory:
    def test_list_shows_all_orders(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        resp = logged_client.get(reverse('orders:list'))
        assert resp.status_code == 200
        order = Order.objects.first()
        assert order.order_number in resp.content.decode()

    def test_list_orders_newest_first(self, logged_client, customer, product, cheap_product, location):
        """Multiple orders should be sorted newest first."""
        Cart.objects.filter(user=customer).delete()
        for i in range(3):
            cart, _ = Cart.objects.get_or_create(user=customer)
            cart.items.all().delete()
            CartItem.objects.create(cart=cart, product=product, quantity=1)
            logged_client.post(reverse('orders:create'), {
                'recipient_name': f'Budi {i}', 'phone': '08123456789',
                'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
                'province': location['province'].id,
                'city': location['city'].id,
                'district': location['district'].id,
                'postal_code': location['postal_code'].id,
            })
        orders = Order.objects.filter(user=customer)
        dates = [o.created_at for o in orders]
        assert dates == sorted(dates, reverse=True)

    def test_list_only_own_orders(self, logged_client, customer, other_user, product, location):
        other_cart = Cart.objects.create(user=other_user)
        CartItem.objects.create(cart=other_cart, product=product, quantity=1)
        other_client = Client()
        other_client.login(username='orang_lain', password='pass123')
        other_client.post(reverse('orders:create'), {
            'recipient_name': 'Other', 'phone': '08123456789',
            'shipping_address': 'Jl. Other No. 1, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        resp = logged_client.get(reverse('orders:list'))
        content = resp.content.decode()
        assert 'Other' not in content

    def test_list_empty(self, logged_client, customer):
        resp = logged_client.get(reverse('orders:list'))
        assert resp.status_code == 200

    def test_list_requires_login(self):
        resp = Client().get(reverse('orders:list'))
        assert resp.status_code == 302


# ============================================================
# ORDER — CANCEL
# ============================================================
@pytest.mark.django_db
class TestOrderCancel:
    def test_cancel_pending_order(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.status == Order.Status.PENDING_PAYMENT
        resp = logged_client.post(reverse('orders:cancel', args=[order.id]))
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == Order.Status.CANCELLED

    def test_cancel_non_pending_redirects(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.PAID
        order.save()
        resp = logged_client.post(reverse('orders:cancel', args=[order.id]))
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == Order.Status.PAID

    def test_cancel_non_pending_shows_error(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.PROCESSING
        order.save()
        resp = logged_client.post(reverse('orders:cancel', args=[order.id]), follow=True)
        messages_list = list(resp.context['messages'])
        assert any('tidak dapat dibatalkan' in str(m) for m in messages_list)

    def test_cancel_success_message(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.post(reverse('orders:cancel', args=[order.id]), follow=True)
        messages_list = list(resp.context['messages'])
        assert any('berhasil dibatalkan' in str(m) for m in messages_list)

    def test_cancel_other_user_404(self, logged_client, customer, other_user, product, location):
        other_cart = Cart.objects.create(user=other_user)
        CartItem.objects.create(cart=other_cart, product=product, quantity=1)
        other_client = Client()
        other_client.login(username='orang_lain', password='pass123')
        other_client.post(reverse('orders:create'), {
            'recipient_name': 'Other', 'phone': '08123456789',
            'shipping_address': 'Jl. Other No. 1, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        other_order = Order.objects.get(user=other_user)
        resp = logged_client.post(reverse('orders:cancel', args=[other_order.id]))
        assert resp.status_code == 404

    def test_cancel_requires_login(self, cart_with_items, location):
        user = User.objects.create_user(username='temp', password='pass')
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=Product.objects.first(), quantity=1)
        c = Client()
        c.login(username='temp', password='pass')
        order = Order.objects.create(user=user, total_price=100000)
        resp = Client().post(reverse('orders:cancel', args=[order.id]))
        assert resp.status_code == 302

    def test_cancel_updates_status_history(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        logged_client.post(reverse('orders:cancel', args=[order.id]))
        history = order.status_history.all()
        statuses = [h.status for h in history]
        assert Order.Status.PENDING_PAYMENT in statuses
        assert Order.Status.CANCELLED in statuses

    def test_cancel_pending_payment_to_shipped(self, logged_client, customer, cart_with_items, location):
        """Cannot cancel if status is shipped"""
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.SHIPPED
        order.save()
        resp = logged_client.post(reverse('orders:cancel', args=[order.id]))
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == Order.Status.SHIPPED


# ============================================================
# ORDER — CONFIRM RECEIVED
# ============================================================
@pytest.mark.django_db
class TestOrderConfirmReceived:
    def test_confirm_delivered_order(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.DELIVERED
        order.save()
        resp = logged_client.post(reverse('orders:confirm_received', args=[order.id]))
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == Order.Status.COMPLETED

    def test_confirm_non_delivered_rejected(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.post(reverse('orders:confirm_received', args=[order.id]))
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == Order.Status.PENDING_PAYMENT

    def test_confirm_other_user_404(self, logged_client, customer, other_user, product, location):
        other_cart = Cart.objects.create(user=other_user)
        CartItem.objects.create(cart=other_cart, product=product, quantity=1)
        other_client = Client()
        other_client.login(username='orang_lain', password='pass123')
        other_client.post(reverse('orders:create'), {
            'recipient_name': 'Other', 'phone': '08123456789',
            'shipping_address': 'Jl. Other No. 1, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        other_order = Order.objects.get(user=other_user)
        other_order.status = Order.Status.DELIVERED
        other_order.save()
        resp = logged_client.post(reverse('orders:confirm_received', args=[other_order.id]))
        assert resp.status_code == 404

    def test_confirm_success_message(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.DELIVERED
        order.save()
        resp = logged_client.post(reverse('orders:confirm_received', args=[order.id]), follow=True)
        messages_list = list(resp.context['messages'])
        assert any('berhasil' in str(m) for m in messages_list)


# ============================================================
# ORDER — TRACKING
# ============================================================
@pytest.mark.django_db
class TestOrderTracking:
    def test_track_shows_pending_status(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        resp = logged_client.get(reverse('orders:track', args=[order.id]))
        assert resp.status_code == 200

    def test_track_shows_paid_status(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        order.status = Order.Status.PAID
        order.save()
        resp = logged_client.get(reverse('orders:track', args=[order.id]))
        assert resp.status_code == 200
        content = resp.content.decode()
        assert 'Pembayaran Dikonfirmasi' in content


# ============================================================
# EDGE CASES
# ============================================================
@pytest.mark.django_db
class TestCheckoutEdgeCases:
    def test_very_long_recipient_name(self, logged_client, customer, cart_with_items, location):
        long_name = 'A' * 100
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': long_name, 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.first()
        assert order.recipient_name == long_name

    def test_phone_with_formatting(self, logged_client, customer, cart_with_items, location):
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '(0812) 3456-7890',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.first()
        assert order.phone == '(0812) 3456-7890'

    def test_shipping_address_saved_with_newlines(self, logged_client, customer, cart_with_items, location):
        addr = 'Jl. Merdeka No. 10\nRT 01 RW 02\nJakarta Pusat'
        resp = logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': addr,
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        assert resp.status_code == 302
        order = Order.objects.first()
        assert order.shipping_address == addr

    def test_order_number_format(self, logged_client, customer, cart_with_items, location):
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.order_number.startswith('ORD-')
        parts = order.order_number.split('-')
        assert len(parts) == 3
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 6  # hex

    def test_multiple_variant_same_product(self, logged_client, customer, variant_product, location):
        cart = Cart.objects.create(user=customer)
        v50 = ProductVariant.objects.get(product=variant_product, size_ml=50)
        v100 = ProductVariant.objects.get(product=variant_product, size_ml=100)
        CartItem.objects.create(cart=cart, product=variant_product, variant=v50, quantity=1)
        CartItem.objects.create(cart=cart, product=variant_product, variant=v100, quantity=2)
        logged_client.post(reverse('orders:create'), {
            'recipient_name': 'Budi', 'phone': '08123456789',
            'shipping_address': 'Jl. Merdeka No. 10, Jakarta',
            'province': location['province'].id,
            'city': location['city'].id,
            'district': location['district'].id,
            'postal_code': location['postal_code'].id,
        })
        order = Order.objects.first()
        assert order.items.count() == 2
        totals = {item.variant_name: item.total_price() for item in order.items.all()}
        assert totals['50ml'] == 75000
        assert totals['100ml'] == 240000

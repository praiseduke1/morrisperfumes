import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.products.models import Category, Product
from apps.carts.models import Cart, CartItem


@pytest.mark.django_db
class TestCartViews:
    def test_cart_detail_requires_login(self):
        client = Client()
        response = client.get(reverse('carts:detail'))
        assert response.status_code == 302

    def test_cart_detail_empty(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        Cart.objects.create(user=user)
        client.force_login(user)
        response = client.get(reverse('carts:detail'))
        assert response.status_code == 200

    def test_cart_add(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=10)
        client.force_login(user)
        response = client.post(reverse('carts:add', args=[prod.id]), {'quantity': 2})
        assert response.status_code == 302
        cart = Cart.objects.get(user=user)
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 2

    def test_cart_add_exceeds_stock(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=2)
        client.force_login(user)
        response = client.post(reverse('carts:add', args=[prod.id]), {'quantity': 5})
        assert response.status_code == 302
        cart = Cart.objects.get(user=user)
        assert cart.items.count() == 0

    def test_cart_update_increase(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=10)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=prod, quantity=2)
        client.force_login(user)
        client.post(reverse('carts:update', args=[item.id]), {'action': 'increase'})
        item.refresh_from_db()
        assert item.quantity == 3

    def test_cart_update_decrease_removes(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=10)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=prod, quantity=1)
        client.force_login(user)
        client.post(reverse('carts:update', args=[item.id]), {'action': 'decrease'})
        assert CartItem.objects.filter(id=item.id).count() == 0

    def test_cart_remove(self):
        client = Client()
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=10)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=prod, quantity=1)
        client.force_login(user)
        client.post(reverse('carts:remove', args=[item.id]))
        assert CartItem.objects.filter(id=item.id).count() == 0

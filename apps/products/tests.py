import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from apps.products.models import Category, Product, Review
from apps.carts.models import Cart, CartItem


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = Category.objects.create(name='Eau de Parfum', slug='eau-de-parfum')
        assert cat.name == 'Eau de Parfum'
        assert str(cat) == 'Eau de Parfum'

    def test_category_ordering(self):
        cat1 = Category.objects.create(name='B', slug='b')
        cat2 = Category.objects.create(name='A', slug='a')
        qs = Category.objects.all()
        assert qs[0] == cat2
        assert qs[1] == cat1


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self):
        cat = Category.objects.create(name='Test Cat', slug='test-cat')
        prod = Product.objects.create(
            name='Test Perfume',
            slug='test-perfume',
            category=cat,
            price=150000,
            stock=10,
        )
        assert prod.name == 'Test Perfume'
        assert prod.is_available is True
        assert str(prod) == 'Test Perfume'

    def test_product_availability_scope(self):
        cat = Category.objects.create(name='Test Cat', slug='test-cat')
        avail = Product.objects.create(name='Avail', slug='avail', category=cat, price=100, stock=5)
        not_avail = Product.objects.create(name='Not Avail', slug='not-avail', category=cat, price=100, stock=0, is_available=False)
        qs = Product.objects.filter(is_available=True)
        assert avail in qs
        assert not_avail not in qs

    def test_stock_sufficient(self):
        cat = Category.objects.create(name='Test Cat', slug='test-cat')
        prod = Product.objects.create(name='Test', slug='test', category=cat, price=100, stock=5)
        assert prod.stock >= 3
        assert not (prod.stock >= 6)


@pytest.mark.django_db
class TestCartModel:
    def test_cart_creation(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        cart = Cart.objects.create(user=user)
        assert cart.total_items() == 0
        assert cart.total_price() == 0

    def test_cart_with_items(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=50000, stock=10)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=prod, quantity=3)
        assert cart.total_items() == 3
        assert cart.total_price() == 150000

    def test_cart_item_unique_with_variant(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        from apps.products.models import ProductVariant
        var = ProductVariant.objects.create(product=prod, size_ml=50, price=100, stock=5)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=prod, variant=var, quantity=1)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            CartItem.objects.create(cart=cart, product=prod, variant=var, quantity=2)


@pytest.mark.django_db
class TestReviewModel:
    def test_create_review(self):
        user = User.objects.create_user(username='reviewer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        review = Review.objects.create(user=user, product=prod, rating=4, comment='Great!')
        assert review.rating == 4
        assert review.comment == 'Great!'
        assert str(review) == f'reviewer - P (4/5)'

    def test_unique_user_product_constraint(self):
        user = User.objects.create_user(username='reviewer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        Review.objects.create(user=user, product=prod, rating=5)
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Review.objects.create(user=user, product=prod, rating=3)

    def test_has_purchased_product_true(self):
        user = User.objects.create_user(username='buyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        from apps.orders.models import Order, OrderItem
        order = Order.objects.create(
            user=user, status='completed', total_price=100,
            recipient_name='Test', phone='123', shipping_address='Addr',
            city='City', postal_code='12345',
        )
        OrderItem.objects.create(order=order, product=prod, product_name='P', price=100, quantity=1)
        review = Review.objects.create(user=user, product=prod, rating=5)
        assert review.has_purchased_product() is True

    def test_has_purchased_product_false(self):
        user = User.objects.create_user(username='nonbuyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        review = Review.objects.create(user=user, product=prod, rating=5)
        assert review.has_purchased_product() is False


@pytest.mark.django_db
class TestReviewViews:
    def test_forbidden_without_purchase(self):
        client = Client()
        user = User.objects.create_user(username='nonbuyer', password='testpass')
        client.login(username='nonbuyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        url = reverse('products:review_form', kwargs={'slug': 'p'})
        resp = client.get(url)
        assert resp.status_code == 403

    def test_create_review_success(self):
        client = Client()
        user = User.objects.create_user(username='buyer', password='testpass')
        client.login(username='buyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        from apps.orders.models import Order, OrderItem
        Order.objects.create(
            user=user, status='completed', total_price=100,
            recipient_name='T', phone='123', shipping_address='A',
            city='C', postal_code='12345',
        )
        OrderItem.objects.create(order=Order.objects.first(), product=prod, product_name='P', price=100, quantity=1)
        url = reverse('products:review_form', kwargs={'slug': 'p'})
        resp = client.get(url)
        assert resp.status_code == 200
        assert 'Ulasan' in resp.content.decode()
        resp2 = client.post(url, {'rating': '5', 'comment': 'Amazing!'})
        assert resp2.status_code == 302
        review = Review.objects.get(user=user, product=prod)
        assert review.rating == 5
        assert review.comment == 'Amazing!'

    def test_update_review(self):
        client = Client()
        user = User.objects.create_user(username='buyer', password='testpass')
        client.login(username='buyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        from apps.orders.models import Order, OrderItem
        order = Order.objects.create(
            user=user, status='completed', total_price=100,
            recipient_name='T', phone='123', shipping_address='A',
            city='C', postal_code='12345',
        )
        OrderItem.objects.create(order=order, product=prod, product_name='P', price=100, quantity=1)
        Review.objects.create(user=user, product=prod, rating=3, comment='OK')
        url = reverse('products:review_form', kwargs={'slug': 'p'})
        resp = client.post(url, {'rating': '4', 'comment': 'Better!'})
        assert resp.status_code == 302
        review = Review.objects.get(user=user, product=prod)
        assert review.rating == 4
        assert review.comment == 'Better!'

    def test_detail_shows_avg_rating(self):
        client = Client()
        user = User.objects.create_user(username='rater', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        from apps.orders.models import Order, OrderItem
        order = Order.objects.create(
            user=user, status='completed', total_price=100,
            recipient_name='T', phone='123', shipping_address='A',
            city='C', postal_code='12345',
        )
        OrderItem.objects.create(order=order, product=prod, product_name='P', price=100, quantity=1)
        user2 = User.objects.create_user(username='rater2', password='testpass')
        order2 = Order.objects.create(
            user=user2, status='completed', total_price=100,
            recipient_name='T', phone='123', shipping_address='A',
            city='C', postal_code='12345',
        )
        OrderItem.objects.create(order=order2, product=prod, product_name='P', price=100, quantity=1)
        Review.objects.create(user=user, product=prod, rating=5, comment='Great')
        Review.objects.create(user=user2, product=prod, rating=3, comment='Meh')
        url = reverse('products:detail', kwargs={'slug': 'p'})
        resp = client.get(url)
        content = resp.content.decode()
        assert '4.0' in content
        assert '2 ulasan' in content
        assert 'Great' in content
        assert 'Meh' in content

    def test_delete_review(self):
        client = Client()
        user = User.objects.create_user(username='buyer', password='testpass')
        client.login(username='buyer', password='testpass')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='P', slug='p', category=cat, price=100, stock=5)
        review = Review.objects.create(user=user, product=prod, rating=5)
        url = reverse('products:review_delete', kwargs={'pk': review.pk})
        resp = client.post(url)
        assert resp.status_code == 302
        assert Review.objects.filter(pk=review.pk).count() == 0


@pytest.mark.django_db
class TestProductDeletion:
    def test_deleted_product_returns_404(self):
        client = Client()
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test Perfume', slug='test-perfume', category=cat, price=100, stock=5)
        prod.delete()
        url = reverse('products:detail', kwargs={'slug': 'test-perfume'})
        resp = client.get(url)
        assert resp.status_code == 404

    def test_deleted_product_not_in_list(self):
        client = Client()
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test Perfume', slug='test-perfume', category=cat, price=100, stock=5)
        prod.delete()
        url = reverse('products:list')
        resp = client.get(url)
        content = resp.content.decode('utf-8')
        assert 'Test Perfume' not in content

    def test_deleted_product_not_in_home(self):
        client = Client()
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Test Perfume', slug='test-perfume', category=cat, price=100, stock=5)
        prod.delete()
        url = reverse('products:home')
        resp = client.get(url)
        content = resp.content.decode('utf-8')
        assert 'Test Perfume' not in content

    def test_unavailable_product_not_in_list(self):
        client = Client()
        cat = Category.objects.create(name='Cat', slug='cat')
        Product.objects.create(name='Unavail', slug='unavail', category=cat, price=100, stock=5, is_available=False)
        url = reverse('products:list')
        resp = client.get(url)
        content = resp.content.decode('utf-8')
        assert 'Unavail' not in content

    def test_unavailable_product_detail_returns_404(self):
        client = Client()
        cat = Category.objects.create(name='Cat', slug='cat')
        Product.objects.create(name='Unavail', slug='unavail', category=cat, price=100, stock=5, is_available=False)
        url = reverse('products:detail', kwargs={'slug': 'unavail'})
        resp = client.get(url)
        assert resp.status_code == 404

    def test_404_page_uses_custom_template(self):
        client = Client()
        resp = client.get('/nonexistent-path/')
        assert resp.status_code == 404
        content = resp.content.decode('utf-8')
        assert 'Produk Tidak Tersedia' in content
        assert 'Kembali ke Katalog' in content

    def test_wishlist_cleaned_on_delete(self):
        from apps.accounts.models import Wishlist
        user = User.objects.create_user(username='testuser', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Wish', slug='wish', category=cat, price=100, stock=5)
        pk = prod.pk
        Wishlist.objects.create(user=user, product=prod)
        assert Wishlist.objects.filter(product_id=pk).count() == 1
        prod.delete()
        assert Wishlist.objects.filter(product_id=pk).count() == 0

    def test_cart_item_cleaned_on_delete(self):
        from apps.carts.models import Cart, CartItem
        user = User.objects.create_user(username='testuser2', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Cart', slug='cart', category=cat, price=100, stock=5)
        pk = prod.pk
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=prod, quantity=1)
        assert CartItem.objects.filter(product_id=pk).count() == 1
        prod.delete()
        assert CartItem.objects.filter(product_id=pk).count() == 0

    def test_order_item_preserved_on_delete(self):
        from apps.orders.models import Order, OrderItem
        user = User.objects.create_user(username='buyer', password='pass12345')
        cat = Category.objects.create(name='Cat', slug='cat')
        prod = Product.objects.create(name='Order', slug='order', category=cat, price=100, stock=5)
        pk = prod.pk
        order = Order.objects.create(
            user=user, status='completed', total_price=100,
            recipient_name='Test', phone='123', shipping_address='Addr',
            city='City', postal_code='12345',
        )
        OrderItem.objects.create(order=order, product=prod, product_name='Order', price=100, quantity=1)
        assert OrderItem.objects.filter(product_id=pk).count() == 1
        prod.delete()
        assert OrderItem.objects.filter(product_id=pk).count() == 0
        assert OrderItem.objects.filter(product_name='Order').count() == 1


@pytest.mark.django_db
class TestUserIdentity:
    def test_customer_stays_customer_after_refresh(self):
        client = Client()
        User.objects.create_user(username='cust', password='pass12345')
        client.login(username='cust', password='pass12345')
        response1 = client.get(reverse('products:home'))
        response2 = client.get(reverse('products:list'))
        response3 = client.get(reverse('products:home'))
        for resp in [response1, response2, response3]:
            content = resp.content.decode('utf-8')
            assert 'Administrator' not in content
            assert 'Admin Panel' not in content
            assert 'Dashboard' in content

    def test_admin_stays_admin_after_refresh(self):
        client = Client()
        User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        client.login(username='admin', password='admin123')
        response1 = client.get(reverse('products:home'))
        response2 = client.get(reverse('products:list'))
        response3 = client.get(reverse('products:home'))
        for resp in [response1, response2, response3]:
            content = resp.content.decode('utf-8')
            assert 'Administrator' in content

    def test_guest_never_sees_admin_banner(self):
        client = Client()
        response1 = client.get(reverse('products:home'))
        response2 = client.get(reverse('products:list'))
        response3 = client.get(reverse('products:home'))
        for resp in [response1, response2, response3]:
            content = resp.content.decode('utf-8')
            assert 'Administrator' not in content
            assert 'Daftar' in content

    def test_customer_and_admin_see_correct_content(self):
        cat = Category.objects.create(name='Cat', slug='cat')
        Product.objects.create(name='Test P', slug='test-p', category=cat, price=100, stock=5)
        admin_client = Client()
        User.objects.create_superuser(username='adm', password='adm123', email='adm@test.com')
        admin_client.login(username='adm', password='adm123')
        cust_client = Client()
        User.objects.create_user(username='cust2', password='pass12345')
        cust_client.login(username='cust2', password='pass12345')
        admin_resp = admin_client.get(reverse('products:list'))
        cust_resp = cust_client.get(reverse('products:list'))
        assert 'Administrator' in admin_resp.content.decode('utf-8')
        assert 'Administrator' not in cust_resp.content.decode('utf-8')

    def test_session_user_id_does_not_change(self):
        client = Client()
        user = User.objects.create_user(username='stable', password='pass12345')
        client.login(username='stable', password='pass12345')
        for _ in range(5):
            client.get(reverse('products:home'))
            client.get(reverse('products:list'))
        session = client.session
        assert session['_auth_user_id'] == str(user.pk)

    def test_admin_panel_does_not_affect_customer_session(self):
        cust_client = Client()
        cust_user = User.objects.create_user(username='cust_only', password='pass12345')
        cust_client.login(username='cust_only', password='pass12345')
        admin_client = Client()
        User.objects.create_superuser(username='adm_only', password='adm123', email='adm@test.com')
        admin_client.login(username='adm_only', password='adm123')
        admin_client.get(reverse('admin:index'))
        cust_resp = cust_client.get(reverse('products:home'))
        content = cust_resp.content.decode('utf-8')
        assert 'Administrator' not in content
        assert 'Administrator — Gunakan panel admin' not in content

    def test_separate_browsers_have_independent_sessions(self):
        client_a = Client()
        User.objects.create_user(username='browser_a', password='pass12345')
        client_a.login(username='browser_a', password='pass12345')
        client_b = Client()
        User.objects.create_user(username='browser_b', password='pass12345')
        client_b.login(username='browser_b', password='pass12345')
        resp_a = client_a.get(reverse('products:home'))
        resp_b = client_b.get(reverse('products:home'))
        session_a = client_a.session
        session_b = client_b.session
        assert session_a['_auth_user_id'] != session_b['_auth_user_id']
        assert session_a['_auth_user_id'] == str(User.objects.get(username='browser_a').pk)
        assert session_b['_auth_user_id'] == str(User.objects.get(username='browser_b').pk)

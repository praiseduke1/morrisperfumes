from django.db import models
from django.contrib.auth.models import User

from apps.products.models import Product, ProductVariant


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='cart',
        verbose_name='Pengguna'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Keranjang'
        verbose_name_plural = 'Keranjang'

    def __str__(self):
        return f'Keranjang {self.user.username}'

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items',
        verbose_name='Keranjang'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='cart_items',
        verbose_name='Produk'
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, related_name='cart_items',
        verbose_name='Varian', null=True, blank=True
    )
    quantity = models.PositiveIntegerField('Jumlah', default=1)

    class Meta:
        verbose_name = 'Item Keranjang'
        verbose_name_plural = 'Item Keranjang'
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        label = f'{self.product.name}'
        if self.variant:
            label += f' ({self.variant.size_ml}ml)'
        return f'{self.quantity}x {label}'

    def unit_price(self):
        return self.variant.price if self.variant else self.product.price

    def total_price(self):
        return self.unit_price() * self.quantity

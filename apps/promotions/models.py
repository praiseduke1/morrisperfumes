from django.db import models
from django.contrib.auth.models import User


class Voucher(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Persen (%)'
        FIXED = 'fixed', 'Nominal (Rp)'

    code = models.CharField('Kode Voucher', max_length=50, unique=True)
    description = models.TextField('Deskripsi', blank=True)
    discount_type = models.CharField(
        'Tipe Diskon', max_length=20,
        choices=DiscountType.choices, default=DiscountType.PERCENTAGE
    )
    discount_amount = models.DecimalField('Nilai Diskon', max_digits=12, decimal_places=0)
    min_purchase = models.DecimalField(
        'Min. Belanja', max_digits=12, decimal_places=0, default=0,
        help_text='Total belanja minimum sebelum diskon'
    )
    max_discount = models.DecimalField(
        'Maks. Diskon', max_digits=12, decimal_places=0,
        null=True, blank=True,
        help_text='Maksimal nominal diskon (khusus persen)'
    )
    expired_date = models.DateField(
        'Tanggal Kedaluwarsa', null=True, blank=True,
        help_text='Setelah tanggal ini, voucher tidak bisa digunakan'
    )
    is_active = models.BooleanField('Aktif', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voucher Promosi'
        verbose_name_plural = 'Voucher Promosi'
        ordering = ['-created_at']

    def __str__(self):
        return self.code


class UserVoucher(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Tersedia'
        USED = 'used', 'Terpakai'
        EXPIRED = 'expired', 'Kedaluwarsa'

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_vouchers',
        verbose_name='Pengguna'
    )
    voucher = models.ForeignKey(
        Voucher, on_delete=models.CASCADE, related_name='user_vouchers',
        verbose_name='Voucher'
    )
    status = models.CharField(
        'Status', max_length=20, choices=Status.choices, default=Status.AVAILABLE
    )
    assigned_at = models.DateTimeField('Ditugaskan Pada', auto_now_add=True)
    used_at = models.DateTimeField('Digunakan Pada', null=True, blank=True)
    expires_at = models.DateTimeField('Kedaluwarsa Pada')

    class Meta:
        verbose_name = 'Voucher Pengguna'
        verbose_name_plural = 'Voucher Pengguna'
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.user.username} - {self.voucher.code}'

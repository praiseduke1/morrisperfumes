from django.db import models

from apps.orders.models import Order


class PaymentStatusHistory(models.Model):
    payment = models.ForeignKey(
        'Payment', on_delete=models.CASCADE, related_name='status_history',
        verbose_name='Pembayaran'
    )
    from_status = models.CharField('Status Sebelumnya', max_length=20, null=True, blank=True)
    to_status = models.CharField('Status Baru', max_length=20)
    raw_response = models.JSONField('Response Midtrans', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Riwayat Status Pembayaran'
        verbose_name_plural = 'Riwayat Status Pembayaran'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.payment}: {self.from_status or "-"} → {self.to_status}'


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'
        EXPIRED = 'expired', 'Expired'

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name='payment',
        verbose_name='Pesanan'
    )
    transaction_id = models.CharField('ID Transaksi Midtrans', max_length=255, blank=True)
    snap_token = models.CharField('Snap Token', max_length=255, blank=True)
    snap_redirect_url = models.URLField('Snap Redirect URL', blank=True)
    payment_method = models.CharField('Metode Pembayaran', max_length=50, blank=True)
    amount = models.DecimalField('Jumlah', max_digits=12, decimal_places=0, default=0)
    status = models.CharField(
        'Status', max_length=20,
        choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    fraud_status = models.CharField('Fraud Status', max_length=50, blank=True)
    payment_time = models.DateTimeField('Waktu Pembayaran', blank=True, null=True)
    raw_response = models.JSONField('Response Midtrans', default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pembayaran'
        verbose_name_plural = 'Pembayaran'
        indexes = [models.Index(fields=['status'])]

    def __str__(self):
        return f'Pembayaran #{self.order.order_number}'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new:
            super().save(*args, **kwargs)
            PaymentStatusHistory.objects.create(
                payment=self,
                from_status=None,
                to_status=self.status,
                raw_response=self.raw_response if self.raw_response else None,
            )
        else:
            try:
                old = Payment.objects.get(pk=self.pk)
                status_changed = old.status != self.status
            except Payment.DoesNotExist:
                status_changed = False
            super().save(*args, **kwargs)
            if status_changed:
                PaymentStatusHistory.objects.create(
                    payment=self,
                    from_status=old.status,
                    to_status=self.status,
                    raw_response=self.raw_response if self.raw_response else None,
                )

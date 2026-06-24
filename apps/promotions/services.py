from datetime import timedelta

from django.utils.timezone import now

from .models import Voucher, UserVoucher


WELCOME_VOUCHER_CODE = 'WELCOME10'


def assign_welcome_voucher(user):
    try:
        voucher = Voucher.objects.get(code=WELCOME_VOUCHER_CODE, is_active=True)
    except Voucher.DoesNotExist:
        return None

    if UserVoucher.objects.filter(user=user, voucher=voucher).exists():
        return None

    expires_at = now() + timedelta(days=30)
    return UserVoucher.objects.create(
        user=user,
        voucher=voucher,
        expires_at=expires_at,
    )


def get_available_vouchers(user, subtotal=0):
    qs = UserVoucher.objects.filter(
        user=user,
        status=UserVoucher.Status.AVAILABLE,
        expires_at__gt=now(),
    ).select_related('voucher')

    if subtotal > 0:
        qs = qs.filter(voucher__min_purchase__lte=subtotal)

    return qs

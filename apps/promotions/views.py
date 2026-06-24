from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.core.decorators import customer_required

from .models import UserVoucher


@login_required
@customer_required
def voucher_list(request):
    vouchers = UserVoucher.objects.filter(
        user=request.user,
    ).select_related('voucher').order_by('-assigned_at')

    context = {
        'vouchers': vouchers,
    }
    return render(request, 'promotions/voucher_list.html', context)

from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            messages.warning(
                request,
                'Administrator tidak diperbolehkan melakukan transaksi.'
            )
            return redirect('products:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

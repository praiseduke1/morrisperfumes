from django.contrib import messages
from django.shortcuts import redirect


class CustomerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            messages.warning(
                request,
                'Administrator tidak diperbolehkan melakukan transaksi.'
            )
            return redirect('products:home')
        return super().dispatch(request, *args, **kwargs)

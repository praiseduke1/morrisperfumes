from apps.accounts.models import Wishlist
from apps.carts.models import Cart


def cart_count(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.total_items()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_count': count}


def wishlist_ids(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        ids = set(
            Wishlist.objects.filter(user=request.user)
            .values_list('product_id', flat=True)
        )
    else:
        ids = set()
    return {'wishlist_product_ids': ids}

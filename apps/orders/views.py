from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from apps.accounts.models import CustomerAddress
from apps.core.decorators import customer_required
from .forms import CheckoutForm
from .models import Order, OrderItem, Voucher
from apps.carts.models import Cart
from apps.promotions.models import UserVoucher
from apps.promotions.services import get_available_vouchers


@customer_required
def order_create(request):
    if not request.user.is_authenticated:
        return redirect('accounts:member_benefits')

    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Keranjang belanja kosong')
        return redirect('carts:detail')

    cart_items = cart.items.select_related('product', 'variant').all()
    subtotal = cart.total_price()
    total_items = cart.total_items()

    user_voucher = None
    discount_amount = 0

    if request.method == 'POST':
        user_voucher_id = request.POST.get('user_voucher_id')
        if user_voucher_id:
            try:
                uv = UserVoucher.objects.select_related('voucher').get(
                    id=user_voucher_id, user=request.user,
                    status=UserVoucher.Status.AVAILABLE,
                    expires_at__gt=now(),
                )
                if uv.voucher.min_purchase <= subtotal:
                    user_voucher = uv
                    if uv.voucher.discount_type == Voucher.DiscountType.FIXED:
                        discount_amount = min(uv.voucher.discount_amount, subtotal)
                    else:
                        amount = subtotal * uv.voucher.discount_amount / 100
                        if uv.voucher.max_discount:
                            amount = min(amount, uv.voucher.max_discount)
                        discount_amount = min(int(amount), subtotal)
                else:
                    messages.error(request, f'Minimal belanja {uv.voucher.min_purchase} untuk menggunakan voucher ini.')
            except UserVoucher.DoesNotExist:
                messages.error(request, 'Voucher tidak tersedia atau sudah kedaluwarsa.')
        else:
            voucher_code = request.session.get('voucher_code', '')
            if voucher_code:
                try:
                    v = Voucher.objects.get(code=voucher_code)
                    if v.is_valid(subtotal):
                        discount_amount = v.calculate_discount(subtotal)
                    else:
                        del request.session['voucher_code']
                except Voucher.DoesNotExist:
                    del request.session['voucher_code']

        form = CheckoutForm(request.POST)
        if form.is_valid():
            for cart_item in cart_items:
                max_stock = cart_item.variant.stock if cart_item.variant else cart_item.product.stock
                if cart_item.quantity > max_stock:
                    label = f'{cart_item.product.name} ({cart_item.variant.size_ml}ml)' if cart_item.variant else cart_item.product.name
                    messages.error(
                        request,
                        f'Stok {label} tidak mencukupi. '
                        f'Tersedia: {max_stock}'
                    )
                    return redirect('carts:detail')

            order = form.save(commit=False)
            order.user = request.user
            order.subtotal = subtotal
            order.discount_amount = discount_amount
            order.total_price = subtotal - discount_amount
            if user_voucher:
                try:
                    order.voucher = Voucher.objects.get(code=user_voucher.voucher.code)
                except Voucher.DoesNotExist:
                    order.voucher = None
            else:
                order.voucher = None
            order.save()

            for cart_item in cart_items:
                unit_price = cart_item.variant.price if cart_item.variant else cart_item.product.price
                variant_name = f'{cart_item.variant.size_ml}ml' if cart_item.variant else ''
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    variant_name=variant_name,
                    price=unit_price,
                    quantity=cart_item.quantity,
                )

            cart.items.all().delete()

            if user_voucher:
                user_voucher.status = UserVoucher.Status.USED
                user_voucher.used_at = now()
                user_voucher.save()
            elif order.voucher:
                Voucher.objects.filter(pk=order.voucher.pk).update(used_count=F('used_count') + 1)

            if 'voucher_code' in request.session:
                del request.session['voucher_code']

            messages.success(request, 'Pesanan berhasil dibuat!')
            return redirect('payments:checkout', order_id=order.id)

        final_total = subtotal - discount_amount
    else:
        addresses = CustomerAddress.objects.filter(user=request.user)
        default_addr = addresses.filter(is_default=True).first()
        initial = {}
        if default_addr:
            initial = {
                'recipient_name': default_addr.recipient_name,
                'phone': default_addr.phone,
                'shipping_address': default_addr.address_line,
                'province': default_addr.province_id,
                'city': default_addr.city_id,
                'district': default_addr.district_id,
                'postal_code': default_addr.postal_code_id,
            }
        elif not default_addr:
            try:
                profile = request.user.profile
                initial = {
                    'recipient_name': request.user.get_full_name() or request.user.username,
                    'phone': profile.phone,
                }
            except AttributeError:
                initial = {
                    'recipient_name': request.user.get_full_name() or request.user.username,
                }
        form = CheckoutForm(initial=initial)

        voucher_code = request.session.get('voucher_code', '')
        if voucher_code:
            try:
                v = Voucher.objects.get(code=voucher_code)
                if v.is_valid(subtotal):
                    discount_amount = v.calculate_discount(subtotal)
                else:
                    del request.session['voucher_code']
            except Voucher.DoesNotExist:
                del request.session['voucher_code']

        final_total = subtotal - discount_amount

    user_vouchers = get_available_vouchers(request.user, subtotal)
    addresses = CustomerAddress.objects.filter(user=request.user)

    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total_items': total_items,
        'user_vouchers': user_vouchers,
        'selected_user_voucher': user_voucher,
        'discount_amount': discount_amount,
        'final_total': final_total,
        'addresses': addresses,
    }
    return render(request, 'orders/order_create.html', context)


@login_required
@customer_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'order_items': order.items.all(),
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@customer_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    context = {'orders': orders}
    return render(request, 'orders/order_list.html', context)


@login_required
@customer_required
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != Order.Status.PENDING_PAYMENT:
        messages.error(request, 'Pesanan tidak dapat dibatalkan karena sudah diproses.')
        return redirect('orders:detail', order_id=order.id)

    order.status = Order.Status.CANCELLED
    order.save()
    messages.success(request, f'Pesanan {order.order_number} berhasil dibatalkan.')
    return redirect('orders:detail', order_id=order.id)


@login_required
@customer_required
def order_confirm_received(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status != Order.Status.DELIVERED:
        messages.error(request, 'Pesanan hanya dapat dikonfirmasi saat status "Pesanan Sampai".')
        return redirect('orders:detail', order_id=order.id)

    order.status = Order.Status.COMPLETED
    order.save()
    messages.success(request, 'Pesanan berhasil diselesaikan. Terima kasih telah berbelanja di Morris Parfum.')
    return redirect('orders:detail', order_id=order.id)


@login_required
@customer_required
def order_track(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    history = {h.status: h for h in order.status_history.all()}

    ALL_STATUSES = ['pending_payment', 'paid', 'processing', 'shipped', 'delivered', 'completed']

    if order.status == Order.Status.CANCELLED:
        non_cancel = [h for h in order.status_history.all() if h.status != Order.Status.CANCELLED]
        if non_cancel:
            last_active = non_cancel[-1].status
            try:
                status_order = ALL_STATUSES[:ALL_STATUSES.index(last_active) + 1]
            except ValueError:
                status_order = ALL_STATUSES[:4]
        else:
            status_order = ['pending_payment']
    else:
        status_order = ALL_STATUSES[:]

    current_idx = None
    for i, s in enumerate(status_order):
        if s == order.status:
            current_idx = i
            break

    if order.status == Order.Status.CANCELLED and current_idx is None and status_order:
        current_idx = len(status_order) - 1

    timeline = []
    for i, s in enumerate(status_order):
        entry = history.get(s)
        is_current = s == order.status and order.status != 'cancelled'
        is_future = current_idx is not None and i > current_idx
        is_active = current_idx is not None and i <= current_idx
        timeline.append({
            'status': s,
            'entry': entry,
            'is_active': is_active,
            'is_current': is_current,
            'is_future': is_future,
        })

    context = {
        'order': order,
        'timeline': timeline,
    }
    return render(request, 'orders/order_track.html', context)

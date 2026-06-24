from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from apps.core.admin_utils import format_rupiah

from .models import Voucher, UserVoucher


@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_amount_formatted', 'min_purchase_formatted',
                    'is_active_badge', 'expired_date', 'created_at']
    list_filter = ['discount_type', 'is_active', 'created_at']
    search_fields = ['code', 'description']
    ordering = ['-created_at']

    fieldsets = (
        ('Informasi Voucher', {
            'fields': ('code', 'description', 'discount_type', 'discount_amount', 'is_active')
        }),
        ('Ketentuan', {
            'fields': ('min_purchase', 'max_discount')
        }),
        ('Periode', {
            'fields': ('expired_date',)
        }),
    )

    def discount_amount_formatted(self, obj):
        if obj.discount_type == Voucher.DiscountType.PERCENTAGE:
            return f'{obj.discount_amount}%'
        return format_rupiah(obj.discount_amount)
    discount_amount_formatted.short_description = 'Diskon'

    def min_purchase_formatted(self, obj):
        return format_rupiah(obj.min_purchase) if obj.min_purchase else 'Rp 0'
    min_purchase_formatted.short_description = 'Min. Belanja'

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span class="badge badge-success">Aktif</span>')
        return mark_safe('<span class="badge badge-danger">Nonaktif</span>')
    is_active_badge.short_description = 'Status'
    is_active_badge.admin_order_field = 'is_active'


@admin.register(UserVoucher)
class UserVoucherAdmin(admin.ModelAdmin):
    list_display = ['user', 'voucher', 'status_badge', 'assigned_at', 'expires_at', 'used_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['user__username', 'user__email', 'voucher__code']
    autocomplete_fields = ['user', 'voucher']
    readonly_fields = ['assigned_at', 'used_at']
    ordering = ['-assigned_at']

    fieldsets = (
        ('Informasi', {
            'fields': ('user', 'voucher', 'status')
        }),
        ('Waktu', {
            'fields': ('assigned_at', 'used_at', 'expires_at'),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'available': 'badge badge-success',
            'used': 'badge badge-secondary',
            'expired': 'badge badge-danger',
        }
        cls = colors.get(obj.status, 'badge badge-secondary')
        return format_html('<span class="{}">{}</span>', cls, obj.get_status_display())
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

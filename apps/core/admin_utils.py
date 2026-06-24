from django.utils.html import format_html


def format_rupiah(value):
    try:
        amount = int(value)
        return f'Rp {amount:,.0f}'.replace(',', '.')
    except (ValueError, TypeError):
        return 'Rp 0'


def status_badge_html(status, colors):
    cls, label = colors.get(status, ('badge badge-secondary', status))
    return format_html('<span class="{}">{}</span>', cls, label)

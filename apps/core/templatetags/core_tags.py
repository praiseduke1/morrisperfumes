import re

from django import template
from django.conf import settings
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def rupiah(value):
    try:
        value = int(value)
        return f'Rp {value:,.0f}'.replace(',', '.')
    except (ValueError, TypeError):
        return 'Rp 0'


@register.filter
def dict_key(d, key):
    return d.get(key)


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()


@register.filter
def webp(url):
    if not url:
        return url
    url_str = str(url)
    if url_str.lower().endswith(('.png', '.jpg', '.jpeg')):
        url_str = re.sub(r'\.(png|jpg|jpeg)$', '.webp', url_str, flags=re.IGNORECASE)
    return url_str


@register.filter
def cache_key(*args):
    return ':'.join(str(a) for a in args if a)


@register.filter
def status_color(value):
    colors = {
        'pending_payment': '#f59e0b',
        'paid': '#3b82f6',
        'processing': '#8b5cf6',
        'shipped': '#1e293b',
        'delivered': '#10b981',
        'completed': '#059669',
        'cancelled': '#ef4444',
    }
    return colors.get(str(value), '#6b7280')

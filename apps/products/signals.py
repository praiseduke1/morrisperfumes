from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Product

PRODUCT_CACHE_PREFIX = 'products:'


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    keys_to_delete = [
        f'{PRODUCT_CACHE_PREFIX}detail:{instance.slug}',
        f'{PRODUCT_CACHE_PREFIX}list',
    ]
    cache.delete_many(keys_to_delete)

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils.timezone import now

from apps.products.models import Category, FragranceFamily, Product
from apps.orders.models import Voucher as OrderVoucher
from apps.promotions.models import Voucher as PromoVoucher, UserVoucher


categories_data = [
    {
        'name': 'Eau de Parfum',
        'description': 'Konsentrasi tinggi 15-20%, aroma tahan lama hingga 8 jam. Cocok untuk acara formal dan malam hari.',
    },
    {
        'name': 'Eau de Toilette',
        'description': 'Konsentrasi 5-15%, aroma ringan dan segar. Cocok untuk penggunaan sehari-hari.',
    },
    {
        'name': 'Eau de Cologne',
        'description': 'Konsentrasi 2-5%, aroma segar dan ringan. Cocok untuk cuaca tropis.',
    },
    {
        'name': 'Attar',
        'description': 'Parfum minyak tanpa alkohol, aroma intens dan tahan lama. Berbahan dasar minyak.',
    },
    {
        'name': 'Roll-On',
        'description': 'Parfum praktis dalam kemasan roll-on, mudah dibawa kemana saja.',
    },
]

products_data = [
    {
        'category': 'Eau de Parfum',
        'name': 'Morris Noir',
        'description': 'A refined blend of black oud, Bulgarian rose, and warm amber. An elegant and mysterious masculine scent for formal evenings.',
        'price': 375000,
        'stock': 25,
        'gender_target': 'men',
        'occasion': 'evening',
        'season': 'winter',
        'sillage': 'heavy',
        'longevity': 'very_long',
    },
    {
        'category': 'Eau de Parfum',
        'name': 'Jasmine Royale',
        'description': 'Premium jasmine absolute fused with Madagascar vanilla and creamy sandalwood. A luxurious floral that lingers all day.',
        'price': 425000,
        'stock': 18,
        'gender_target': 'women',
        'occasion': 'formal',
        'season': 'spring',
        'sillage': 'moderate',
        'longevity': 'long',
    },
    {
        'category': 'Eau de Parfum',
        'name': 'Amber Dusk',
        'description': 'Warm amber entwined with patchouli and white musk. Creates an unforgettable elegant and mysterious impression.',
        'price': 385000,
        'stock': 30,
        'gender_target': 'unisex',
        'occasion': 'evening',
        'season': 'fall',
        'sillage': 'moderate',
        'longevity': 'long',
    },
    {
        'category': 'Eau de Toilette',
        'name': 'Citrus Morning',
        'description': 'A burst of Mediterranean citrus, Italian lemon, and pink grapefruit. A light, invigorating scent perfect for daily wear.',
        'price': 195000,
        'stock': 45,
        'gender_target': 'unisex',
        'occasion': 'daily',
        'season': 'summer',
        'sillage': 'intimate',
        'longevity': 'short',
    },
    {
        'category': 'Eau de Toilette',
        'name': 'Ocean Whisper',
        'description': 'Fresh marine accord with green melon and soft musk. Delivers a clean, crisp sensation all day long.',
        'price': 205000,
        'stock': 38,
        'gender_target': 'men',
        'occasion': 'casual',
        'season': 'summer',
        'sillage': 'moderate',
        'longevity': 'moderate',
    },
    {
        'category': 'Eau de Toilette',
        'name': 'Green Tea & Mint',
        'description': 'Japanese green tea blended with fresh mint and lemon zest. A calming and refreshing scent.',
        'price': 175000,
        'stock': 50,
        'gender_target': 'unisex',
        'occasion': 'daily',
        'season': 'spring',
        'sillage': 'intimate',
        'longevity': 'short',
    },
    {
        'category': 'Eau de Cologne',
        'name': 'Morris Lavender',
        'description': 'French lavender with a touch of rosemary and bergamot. A timeless and elegant classic.',
        'price': 135000,
        'stock': 60,
        'gender_target': 'unisex',
        'occasion': 'office',
        'season': 'all',
        'sillage': 'moderate',
        'longevity': 'moderate',
    },
    {
        'category': 'Eau de Cologne',
        'name': 'Sport Pulse',
        'description': 'Zesty mandarin, peppermint, and grapefruit. Perfect for active lifestyles and tropical heat.',
        'price': 125000,
        'stock': 55,
        'gender_target': 'men',
        'occasion': 'casual',
        'season': 'summer',
        'sillage': 'intimate',
        'longevity': 'short',
    },
    {
        'category': 'Attar',
        'name': 'Sandalwood Mystique',
        'description': 'Pure Indian sandalwood attar with saffron and rose. An intense oil-based fragrance lasting 12+ hours.',
        'price': 285000,
        'stock': 15,
        'gender_target': 'unisex',
        'occasion': 'evening',
        'season': 'winter',
        'sillage': 'heavy',
        'longevity': 'very_long',
    },
    {
        'category': 'Attar',
        'name': 'Oud Prestige',
        'description': 'Premium Assam oud blended with musk and amber. An authentic and luxurious Middle Eastern scent.',
        'price': 450000,
        'stock': 10,
        'gender_target': 'men',
        'occasion': 'formal',
        'season': 'winter',
        'sillage': 'heavy',
        'longevity': 'very_long',
    },
    {
        'category': 'Roll-On',
        'name': 'Vanilla Cashmere',
        'description': 'Madagascar vanilla with caramel and white chocolate. A sweet, comforting, and cozy fragrance.',
        'price': 95000,
        'stock': 75,
        'gender_target': 'women',
        'occasion': 'daily',
        'season': 'all',
        'sillage': 'intimate',
        'longevity': 'moderate',
    },
    {
        'category': 'Roll-On',
        'name': 'White Musk',
        'description': 'Clean white musk with lily of the valley. A soft, delicate scent perfect for everyday wear.',
        'price': 85000,
        'stock': 80,
        'gender_target': 'women',
        'occasion': 'office',
        'season': 'all',
        'sillage': 'intimate',
        'longevity': 'moderate',
    },
]


class Command(BaseCommand):
    help = 'Seed sample categories and products'

    def handle(self, *args, **options):
        fragrance_families = ['Citrus', 'Floral', 'Woody', 'Oriental', 'Fresh']
        created_families = 0
        for name in fragrance_families:
            _, created = FragranceFamily.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name), 'description': f'Keluarga aroma {name.lower()}'}
            )
            if created:
                created_families += 1
                self.stdout.write(f'  + FragranceFamily: {name}')

        created_categories = 0
        for cat_data in categories_data:
            _, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                }
            )
            if created:
                created_categories += 1
                self.stdout.write(f'  + Category: {cat_data["name"]}')

        created_products = 0
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            _, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'slug': slugify(prod_data['name']),
                    'category': category,
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'stock': prod_data['stock'],
                    'is_available': True,
                    'gender_target': prod_data.get('gender_target', 'unisex'),
                    'occasion': prod_data.get('occasion', 'daily'),
                    'season': prod_data.get('season', 'all'),
                    'sillage': prod_data.get('sillage', 'moderate'),
                    'longevity': prod_data.get('longevity', 'moderate'),
                }
            )
            if created:
                created_products += 1
                self.stdout.write(f'  + Product: {prod_data["name"]}')

        vouchers_data = [
            {'code': 'WELCOME10', 'discount_type': 'percentage', 'discount_amount': 10,
             'min_purchase': 100000, 'max_discount': 50000, 'max_uses': 100,
             'valid_from': now(), 'valid_until': now() + timedelta(days=30)},
            {'code': 'FLAT50', 'discount_type': 'fixed', 'discount_amount': 50000,
             'min_purchase': 200000, 'max_uses': 50,
             'valid_from': now(), 'valid_until': now() + timedelta(days=14)},
            {'code': 'MERDEKA25', 'discount_type': 'percentage', 'discount_amount': 25,
             'min_purchase': 150000, 'max_discount': 75000, 'max_uses': 200,
             'valid_from': now(), 'valid_until': now() + timedelta(days=60)},
            {'code': 'GRATISONGIR', 'discount_type': 'fixed', 'discount_amount': 25000,
             'min_purchase': 100000, 'max_uses': 100,
             'valid_from': now(), 'valid_until': now() + timedelta(days=7)},
        ]
        created_vouchers = 0
        for v_data in vouchers_data:
            _, created = OrderVoucher.objects.get_or_create(
                code=v_data['code'],
                defaults=v_data
            )
            if created:
                created_vouchers += 1
                self.stdout.write(f'  + Order Voucher: {v_data["code"]}')

            promo_defaults = v_data.copy()
            promo_defaults.pop('valid_from', None)
            promo_defaults.pop('valid_until', None)
            promo_defaults.pop('max_uses', None)
            promo_defaults.pop('used_count', None)
            promo_defaults['description'] = f'Diskon {v_data["discount_amount"]}{"%" if v_data["discount_type"] == "percentage" else ""}'
            _, promo_created = PromoVoucher.objects.get_or_create(
                code=v_data['code'],
                defaults=promo_defaults
            )
            if promo_created:
                self.stdout.write(f'  + Promo Voucher: {v_data["code"]}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created {created_families} fragrance families, {created_categories} categories, '
            f'{created_products} products, and {created_vouchers} vouchers.'
        ))

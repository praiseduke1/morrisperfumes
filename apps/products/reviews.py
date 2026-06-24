from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from apps.orders.models import Order, OrderItem
from .models import Product, ProductSlugRedirect, Review


class ReviewFormView(LoginRequiredMixin, View):
    template_name = 'products/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            self.product = get_object_or_404(
                Product.objects.only('id', 'name', 'slug', 'image'),
                slug=kwargs['slug'], is_available=True
            )
        except Http404:
            redirect_entry = get_object_or_404(
                ProductSlugRedirect, old_slug=kwargs['slug']
            )
            return redirect(reverse('products:review_form', args=[redirect_entry.product.slug]))
        user = request.user

        has_purchased = OrderItem.objects.filter(
            product=self.product,
            order__user=user,
            order__status__in=['completed', 'paid'],
        ).exists()

        if not has_purchased:
            return render(request, 'products/review_forbidden.html', {
                'product': self.product,
            }, status=403)

        try:
            self.existing_review = Review.objects.get(product=self.product, user=user)
            self.is_update = True
        except Review.DoesNotExist:
            self.existing_review = None
            self.is_update = False

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        review = self.existing_review
        return render(request, self.template_name, {
            'product': self.product,
            'review': review,
            'is_update': self.is_update,
        })

    def post(self, request, *args, **kwargs):
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        if not rating or rating not in ('1', '2', '3', '4', '5'):
            return render(request, self.template_name, {
                'product': self.product,
                'review': self.existing_review,
                'is_update': self.is_update,
                'error': 'Pilih rating 1-5.',
            }, status=400)

        review, created = Review.objects.update_or_create(
            product=self.product,
            user=request.user,
            defaults={
                'rating': int(rating),
                'comment': comment,
            },
        )

        return redirect(reverse('products:detail', kwargs={'slug': self.product.slug}))


class ReviewDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        review = get_object_or_404(Review, id=kwargs['pk'], user=request.user)
        product_slug = review.product.slug
        review.delete()
        return redirect(reverse('products:detail', kwargs={'slug': product_slug}))

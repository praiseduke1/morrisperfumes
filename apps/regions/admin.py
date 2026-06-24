from django.contrib import admin

from .models import Province, City, District, PostalCode


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'province']
    list_filter = ['province']
    search_fields = ['name', 'code']
    autocomplete_fields = ['province']
    ordering = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'city']
    list_filter = ['city__province']
    search_fields = ['name', 'code']
    autocomplete_fields = ['city']
    ordering = ['name']


@admin.register(PostalCode)
class PostalCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'district']
    list_filter = ['district__city__province']
    search_fields = ['code']
    autocomplete_fields = ['district']
    ordering = ['code']

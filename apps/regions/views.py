from django.http import JsonResponse

from .models import get_cached_provinces, get_cached_cities, get_cached_districts, get_cached_postal_codes


def api_provinces(request):
    provinces = get_cached_provinces()
    return JsonResponse(provinces, safe=False)


def api_cities(request):
    province_id = request.GET.get('province_id')
    if not province_id:
        return JsonResponse({'error': 'province_id required'}, status=400)
    cities = get_cached_cities(province_id)
    return JsonResponse(cities, safe=False)


def api_districts(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse({'error': 'city_id required'}, status=400)
    districts = get_cached_districts(city_id)
    return JsonResponse(districts, safe=False)


def api_postal_code(request):
    district_id = request.GET.get('district_id')
    if not district_id:
        return JsonResponse({'error': 'district_id required'}, status=400)
    codes = get_cached_postal_codes(district_id)
    return JsonResponse(codes, safe=False)

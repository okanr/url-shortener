import datetime
import json

from django.http import HttpResponseRedirect, JsonResponse
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from .models import URLShortener
from .tasks import task_sync_cache_and_db

BASE_URL = getattr(settings, 'BASE_URL', 'http://localhost:8000')


def report_view(request):
    data = URLShortener.objects.all()
    if data:
        response = []
        for item in data:
            response.append({
                'url': item.url,
                'short': item.short,
                'count': item.count
            })
        return JsonResponse({
            'status': 'success',
            'data': response
        })
    else:
        return JsonResponse({
            'status': 'info',
            'message': 'No data' 
        })


@csrf_exempt  # added to use postman requests
@require_POST
def shorten(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    url = body['url']
    obj, created = URLShortener.objects.get_or_create(url=url)
    if created:
        cache.set(obj.short, url)
        # added expire date to eliminate old invalid urls
        cache.expire_at(obj.short, datetime.datetime.now() +
                        datetime.timedelta(days=7))
        return JsonResponse({
            'status': 'success',
            'data': f'{BASE_URL}/{obj.short}'
        })

    else:
        return JsonResponse({
            'status': 'info',
            'message': 'Shortened URL already exists'
        })


def get_long_url(request, url):
    if cache.get(url):
        long_url = cache.get(url)
    else:
        obj = get_object_or_404(URLShortener.objects.get(short=url, expire_date__lt=datetime.datetime.now()))
        long_url = obj.url
    task_sync_cache_and_db.delay(url)
    return HttpResponseRedirect(long_url)

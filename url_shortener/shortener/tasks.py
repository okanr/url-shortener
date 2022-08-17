from celery import shared_task

from .models import URLShortener


@shared_task
def task_sync_cache_and_db(url):
    obj = URLShortener.objects.get(short=url)
    obj.count += 1
    obj.save()
    return 'Successfully synced'

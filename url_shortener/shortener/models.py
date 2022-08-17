import datetime

from django.core.cache import cache
from django.conf import settings
from django.db import models
from django.urls import reverse

from .validators import valid_URL

BASE_URL = getattr(settings, 'BASE_URL', 'http://localhost:8000')


def encode_url(_id):
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    short_url = ""
    while _id > 0:
        short_url += charset[_id % 62]
        _id //= 62
    return short_url[len(short_url):: -1]


class URLShortener(models.Model):
    url = models.CharField(max_length=300, validators=[valid_URL])
    short = models.CharField(max_length=100, unique=True, blank=True)
    count = models.IntegerField(default=0)
    expire_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if cache.get('counter'):
            counter = cache.get('counter')
            cache.set('counter', counter + 1)
        else:
            cache.set('counter', 1)
            counter = 1
        if self.short is None or self.short == '':
            self.short = encode_url(counter)
            self.expire_date = datetime.datetime.now() + datetime.timedelta(days=7)
        super(URLShortener, self).save(*args, **kwargs)

    def get_short_url(self):
        url_path = reverse("get-long-url", kwargs={'url': self.short})
        url_path = BASE_URL + url_path
        return url_path

    def __str__(self) -> str:
        return self.url

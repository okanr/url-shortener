from django.urls import path
from . import views

urlpatterns = [
    path('', views.shorten, name='shorten'),
    path('<str:url>', views.get_long_url, name='get-long-url'),
    path('internal/report', views.report_view, name='report'),
]
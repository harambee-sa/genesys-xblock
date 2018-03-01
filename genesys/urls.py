from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^genesis_webhook$', views.GenesysView, name='genesys_webhook'),
]
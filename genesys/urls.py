from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard$', views.GenesysView, name='genesys_view'),
]
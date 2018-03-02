from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^genesys/student-result-receiver$', views.GenesysView, name='genesys_result_receiver'),
]
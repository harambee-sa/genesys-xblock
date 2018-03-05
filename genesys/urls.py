from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^genesys/student_result_receiver$', views.genesys_result_receiver, name='genesys_result_receiver'),
]
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path
from django.conf.urls import include
from web.views import account

from app01 import views

urlpatterns = [
    url(r'^register/$', account.register, name='register'),
]
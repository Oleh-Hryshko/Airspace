from django.urls import path
from . import views
from . import base

urlpatterns = [
    path('', views.index, name='home'),
    path('', base.convert, name="convert"),
    path('', base.countries_list, name="countries_list"),
]

from django.urls import path, include
from django.conf.urls import url

from django.views.generic.base import TemplateView
from django.contrib import admin


from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    path("", views.index, name="index"),
    path("signup", views.signup, name='signup'),
    path("add_place", views.add_place, name='add_place'),
    path("add_folder", views.add_folder, name='add_folder'),
    path("<int:place_id>/delete", views.delete, name='delete'),
    path("<int:folder_id>/delete_folder", views.delete_folder, name='delete_folder'),
    path("<int:place_id>/edit_place", views.edit_place, name='edit_place'),
    path("<int:place_id>/view_place", views.view_place, name='view_place'),
    path("<str:message>/error", views.error, name='error'),
    path("<str:f_type>/filter", views.filter, name='filter'),
    path('accounts/', include('django.contrib.auth.urls')),
]

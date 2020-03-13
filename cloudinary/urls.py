from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('api/user/register',views.register),
    path('api/user/login',views.login),
    path('api/file/sendImageDetails',views.sendImageDetails),
    path('api/file',views.file),
    path('api/file/deleteImage',views.deleteImage),
    path('api/file/search',views.search)

]

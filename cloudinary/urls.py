from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('user/register',views.register),
    path('user/login',views.login),
    path('file/sendImageDetails',views.sendImageDetails),
    path('file',views.file),
    path('file/deleteImage',views.deleteImage),
    path('file/search',views.search)

]

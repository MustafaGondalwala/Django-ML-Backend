from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('check-for-faces',views.checkForFace),
    path('add-new-face',views.add_new_face),
    path('login',views.login)
]

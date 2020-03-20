from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('scrape/<slug:type>',views.scrape,name="scrape"),
    path('scrape/s/autosuggestion',views.autosuggestion,name="autosuggestion"),
]

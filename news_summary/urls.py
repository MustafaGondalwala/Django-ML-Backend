from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('scrape/<slug:type>',views.scrape),
    path('scrape',views.scrapeAll),
    path('get/<slug:type>',views.get),
    path('get',views.getAll)
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('scrape/<slug:type>',views.scrape,name="scrape"),
    path('s/autosuggestion',views.autosuggestion,name="autosuggestion"),
    path('scrape/d/description',views.getDescription,name="getDescription")
]
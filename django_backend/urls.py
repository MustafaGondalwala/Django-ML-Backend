from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/face-identification/',include('face_identification.urls')),
    path('api/cloudinary/',include('cloudinary.urls')),
    path('api/scrapper/',include('scraper.urls')),
    path('api/news-summary/',include('news_summary.urls')),

]

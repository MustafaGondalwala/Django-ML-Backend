from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/face-identification/',include('face_identification.urls')),
#    path('api/cloudinary/',include('cloudinary.urls')),
    path('api/product_scrapper/',include('product_scrapper.urls')),
    path('api/news-summary/',include('news_summary.urls')),
    path('api/timetracker/',include('timetracker.urls'))
]

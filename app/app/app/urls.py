from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('evals/', include('playerevals.urls')),
    path('admin/', admin.site.urls),
]
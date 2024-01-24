from django.contrib import admin
from django.urls import path

from topt import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', views.api, name='api'),
]

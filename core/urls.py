from django.urls import path
from . import views

urlpatterns = [
    path('banner/<slug:slug>/', views.banner_api, name='api_banner'),
]

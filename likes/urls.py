from django.urls import path
from .views import like, favourite

urlpatterns = [
    path('like', like, name='like'),
    path('fav', favourite, name='favourite'),
]

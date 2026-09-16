from django.urls import include, path
from rest_framework import routers
from reviews.views import ReviewViewSet

router = routers.DefaultRouter()

router.register('reviews', ReviewViewSet, basename='reviews')

urlpatterns = [path('', include(router.urls)),]
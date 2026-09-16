from django.urls import include, path
from rest_framework import routers
from listings.views import ListingViewSet

router = routers.DefaultRouter()

router.register('listings', ListingViewSet, basename='listings')

urlpatterns = [path('', include(router.urls)),]
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from listings.views import ListingViewSet
from reviews.views import ReviewViewSet
from bookings.views import BookingViewSet
from history.views import SearchHistoryViewSet, ViewHistoryViewSet
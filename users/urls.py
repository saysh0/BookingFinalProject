from django.urls import path, include
from rest_framework import routers
from users.views import UserViewSet

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='user')

urlpatterns = [path('', include(router.urls)),]
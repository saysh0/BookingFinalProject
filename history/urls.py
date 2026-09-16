from django.urls import path, include
from rest_framework import routers
from history.views import ViewHistoryViewSet, SearchHistoryViewSet

router = routers.DefaultRouter()

router.register('view_history', ViewHistoryViewSet, basename='view_history')
router.register('search_history', SearchHistoryViewSet, basename='search_history')

urlpatterns = [path('', include(router.urls)),]
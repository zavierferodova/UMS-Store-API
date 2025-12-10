


from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet

urlpatterns = [
    path('', StoreViewSet.as_view({'get': 'list', 'patch': 'partial_update'}), name='store-detail'),
]

from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('', UserViewSet.as_view({'get': 'list'}), name='user-list'),
    path('/<pk>', UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='user-detail'),
]

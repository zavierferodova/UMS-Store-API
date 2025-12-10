from django.urls import path

from .views import TransactionViewSet

urlpatterns = [
    path('', TransactionViewSet.as_view({'get': 'list', 'post': 'create'}), name='transaction-list-create'),
    path('/<uuid:pk>', TransactionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='transaction-detail'),
]

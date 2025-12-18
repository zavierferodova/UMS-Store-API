from django.urls import path

from suppliers.views.payment import SupplierPaymentViewSet
from suppliers.views.supplier import SupplierViewSet

urlpatterns = [
    path('', SupplierViewSet.as_view({'get': 'list', 'post': 'create'}), name='supplier-list'),
    path('/payments', SupplierPaymentViewSet.as_view({'get': 'list', 'post': 'create'}), name='supplier-payment-list'),
    path('/payments/<pk>', SupplierPaymentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='supplier-payment-detail'),
    path('/<pk>', SupplierViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='supplier-detail'),
]

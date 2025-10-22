from django.urls import path

from purchase_orders.views import PurchaseOrderViewSet

urlpatterns = [
    path('', PurchaseOrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='purchase-order-list'),
    path('/<pk>', PurchaseOrderViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='purchase-order-detail'),
]

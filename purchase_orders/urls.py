from django.urls import path

from purchase_orders.views.po_item import PoItemViewSet
from purchase_orders.views.purchase_order import PurchaseOrderViewSet

urlpatterns = [
    path('', PurchaseOrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='purchase-order-list'),
    path('/<pk>', PurchaseOrderViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='purchase-order-detail'),
    path('/<purchase_order_pk>/items', PoItemViewSet.as_view({'get': 'list', 'post': 'create'}), name='po-item-list'),
    path('/<purchase_order_pk>/items/<pk>', PoItemViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='po-item-detail'),
]

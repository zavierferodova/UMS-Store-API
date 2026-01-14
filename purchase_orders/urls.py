from django.urls import path

from purchase_orders.views.purchase_order import PurchaseOrderViewSet

urlpatterns = [
    path('', PurchaseOrderViewSet.as_view({'get': 'list', 'post': 'create'}), name='purchase-order-list'),
    path('/<pk>', PurchaseOrderViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update' }), name='purchase-order-detail')
]

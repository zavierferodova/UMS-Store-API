from django.urls import path

from .views import TransactionViewSet

urlpatterns = [
    path('', TransactionViewSet.as_view({'get': 'list', 'post': 'create'}), name='transaction-list-create'),
    path('/supplier/<uuid:supplier_id>/products', TransactionViewSet.as_view({'get': 'supplier_products'}), name='transaction-supplier-products'),
    path('/supplier/<uuid:supplier_id>/products/export', TransactionViewSet.as_view({'post': 'export_supplier_products'}), name='transaction-supplier-products-export'),
    path('/<uuid:pk>', TransactionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='transaction-detail'),
]

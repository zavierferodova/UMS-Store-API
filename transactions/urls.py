from django.urls import path

from .views import TransactionViewSet

urlpatterns = [
    path('', TransactionViewSet.as_view({'get': 'list', 'post': 'create'}), name='transaction-list-create'),
    path('/supplier/<uuid:supplier_id>/products', TransactionViewSet.as_view({'get': 'supplier_products'}), name='transaction-supplier-products'),
    path('/supplier/<uuid:supplier_id>/products/export', TransactionViewSet.as_view({'post': 'export_supplier_products'}), name='transaction-supplier-products-export'),
    path('/supplier/export', TransactionViewSet.as_view({'post': 'export_supplier_sales_report'}), name='transaction-supplier-export'),
    path('/products/categories/export', TransactionViewSet.as_view({'post': 'export_product_category_sales'}), name='transaction-product-category-export'),
    path('/<uuid:pk>', TransactionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='transaction-detail'),
]

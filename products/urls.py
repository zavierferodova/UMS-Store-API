from django.urls import path

from products.views.category import CategoryViewSet
from products.views.image import ProductImageViewSet
from products.views.product import ProductViewSet
from products.views.sku import ProductSKUViewSet

urlpatterns = [
    path('/sku', ProductSKUViewSet.as_view({'get': 'list', 'post': 'create'}), name='sku-list'),
    path('/sku/<str:sku>/check', ProductSKUViewSet.as_view({'get': 'check'}), name='sku-check'),
    path('/sku/<str:sku>', ProductSKUViewSet.as_view({'patch': 'partial_update'}), name='sku-update'),
    path('/categories', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
    path('/categories/<pk>', CategoryViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='category-detail'),
    path('/images', ProductImageViewSet.as_view({'post': 'create'}), name='product-image-list'),
    path('/images/<pk>', ProductImageViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-image-detail'),
    path('', ProductViewSet.as_view({'get': 'list', 'post': 'create'}), name='product-list'),
    path('/<pk>', ProductViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='product-detail'),
]

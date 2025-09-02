from django.urls import path
from . import views

urlpatterns = [
    path('', views.SupplierViewSet.as_view({'get': 'list', 'post': 'create'}), name='supplier-list'),
    path('/<pk>', views.SupplierViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='supplier-detail'),
]

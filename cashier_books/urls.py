from django.urls import path

from .views import CashierBookViewSet

urlpatterns = [
    path('', CashierBookViewSet.as_view({'get': 'list', 'post': 'create'}), name='cashier-book-list-create'),
    path('/active', CashierBookViewSet.as_view({'get': 'get_active_book'}), name='cashier-book-active'),
    path('/active-stats', CashierBookViewSet.as_view({'get': 'active_stats'}), name='cashier-book-active-stats'),
    path('/<uuid:pk>', CashierBookViewSet.as_view({'get': 'retrieve'}), name='cashier-book-detail'),
    path('/<uuid:pk>/stats', CashierBookViewSet.as_view({'get': 'stats'}), name='cashier-book-stats'),
    path('/<uuid:pk>/transactions', CashierBookViewSet.as_view({'get': 'transactions'}), name='cashier-book-transactions'),
    path('/close', CashierBookViewSet.as_view({'patch': 'close_book'}), name='cashier-book-close'),
]

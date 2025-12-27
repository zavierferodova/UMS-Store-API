from django.urls import include, path

urlpatterns = [
    path('/auth', include('authentication.urls')),
    path('/users', include('users.urls')),
    path('/suppliers', include('suppliers.urls')),
    path('/products', include('products.urls')),
    path('/purchase-orders', include('purchase_orders.urls')),
    path('/transactions', include('transactions.urls')),
    path('/store', include('store.urls')),
    path('/coupons', include('coupons.urls')),
]

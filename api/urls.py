from django.urls import include, path

urlpatterns = [
    path('/auth', include('authentication.urls')),
    path('/users', include('users.urls')),
    path('/suppliers', include('suppliers.urls')),
    path('/products', include('products.urls'))
]

from django.urls import path, include

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('users/', include('users.urls')),
    path('suppliers/', include('suppliers.urls')),
]




from django.urls import path

from .views import StoreViewSet

urlpatterns = [
    path('', StoreViewSet.as_view({'get': 'list', 'patch': 'partial_update'}), name='store-detail'),
]

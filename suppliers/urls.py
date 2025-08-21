from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'list/?', views.supplier_list),
    re_path(r'add/?', views.add_supplier),
    path('<str:pk>', views.supplier_detail, name='supplier_detail')
]

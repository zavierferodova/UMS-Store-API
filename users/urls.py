from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list),
    path('<str:pk>', views.user_detail),
]

from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'list/?', views.user_list),
    path('<str:pk>', views.UserDetailView.as_view()),
]

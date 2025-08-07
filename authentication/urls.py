from django.urls import re_path
from .views import GoogleLogin
from dj_rest_auth.views import LoginView, PasswordChangeView, UserDetailsView
from dj_rest_auth.jwt_auth import get_refresh_view
from rest_framework_simplejwt.views import TokenVerifyView

urlpatterns = [
    re_path(r'login/?$', LoginView.as_view(), name='rest_login'),
    re_path(r'google/?$', GoogleLogin.as_view(), name='google_login'),
    re_path(r'user/?$', UserDetailsView.as_view(), name='rest_user_details'),
    re_path(r'password/change/?$', PasswordChangeView.as_view(), name='rest_password_change'),
    re_path(r'token/refresh/?$', get_refresh_view().as_view(), name='token_refresh')
    # path('registration/', include('dj_rest_auth.registration.urls')),
]

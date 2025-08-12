from django.urls import re_path
from .views import CustomGoogleLogin, CustomLoginView, CustomTokenRefreshView, CustomPasswordChangeView, CustomUserDetailsView, UserProfileImageView

urlpatterns = [
    re_path(r'login/?', CustomLoginView.as_view(), name='rest_login'),
    re_path(r'google/?', CustomGoogleLogin.as_view(), name='google_login'),
    re_path(r'user/profile-image/?', UserProfileImageView.as_view(), name='user_profile_image'),
    re_path(r'user/?', CustomUserDetailsView.as_view(), name='rest_user_details'),
    re_path(r'password/change/?', CustomPasswordChangeView.as_view(), name='rest_password_change'),
    re_path(r'token/refresh/?', CustomTokenRefreshView.as_view(), name='token_refresh')
    # path('registration/', include('dj_rest_auth.registration.urls')),
]

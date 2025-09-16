from django.urls import path

from .views import (
    CustomGoogleLogin,
    CustomLoginView,
    CustomPasswordChangeView,
    CustomTokenRefreshView,
    CustomUserDetailsView,
    UserProfileImageView,
)

urlpatterns = [
    path('/login', CustomLoginView.as_view(), name='rest_login'),
    path('/google', CustomGoogleLogin.as_view(), name='google_login'),
    path('/user/profile-image', UserProfileImageView.as_view(), name='user_profile_image'),
    path('/user', CustomUserDetailsView.as_view(), name='rest_user_details'),
    path('/password/change', CustomPasswordChangeView.as_view(), name='rest_password_change'),
    path('/token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh')
    # path('registration/', include('dj_rest_auth.registration.urls')),
]

from dj_rest_auth.registration.serializers import SocialLoginSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import CustomSocialLoginSerializer
from dj_rest_auth.views import LoginView, PasswordChangeView, UserDetailsView
from api.utils import api_response
from rest_framework import status
from dj_rest_auth.jwt_auth import get_refresh_view
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import CustomTokenRefreshSerializer

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer

class CustomGoogleLogin(GoogleLogin):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Google login successful",
            data=response.data
        )

class CustomLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data)
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()

    def get_response(self):
        response = super().get_response()
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Login successful",
            data=response.data
        )

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Token refreshed successfully",
            data=response.data
        )

class CustomPasswordChangeView(PasswordChangeView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Password changed successfully",
            data=response.data
        )

class CustomUserDetailsView(UserDetailsView):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="User details retrieved successfully",
            data=response.data
        )

    def patch(self, request, *args, **kwargs):
        response = super().patch(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="User details updated successfully",
            data=response.data
        )

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="User details updated successfully",
            data=response.data
        )

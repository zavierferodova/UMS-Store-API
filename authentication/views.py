from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LoginView, PasswordChangeView, UserDetailsView
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from api.utils import api_response
from users.serializers import UserSerializer

from .serializers import CustomSocialLoginSerializer, CustomTokenRefreshSerializer, UserProfileImageSerializer


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

class UserProfileImageView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        serializer = UserProfileImageSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.profile_image = request.data['profile_image']
            user.save()
            serializer = UserSerializer(user)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Profile image updated successfully",
                data=serializer.data
            )
        return api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            data=serializer.errors
        )

from dj_rest_auth.registration.serializers import SocialLoginSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from .serializers import CustomSocialLoginSerializer

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    serializer_class = CustomSocialLoginSerializer
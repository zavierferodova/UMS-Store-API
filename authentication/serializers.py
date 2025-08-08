from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timezone

class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField()

class CustomSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']

        if not user.name:
            user.name = user.socialaccount_set.filter(provider='google').first().extra_data.get('name')
            user.save()

        return attrs

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        access_token_expiration_timestamp = refresh.access_token.get('exp')
        if access_token_expiration_timestamp:
            dt_object = datetime.fromtimestamp(access_token_expiration_timestamp, tz=timezone.utc)
            data['access_expiration'] = dt_object.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return data

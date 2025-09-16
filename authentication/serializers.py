from datetime import UTC, datetime

from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class CustomSocialLoginSerializer(SocialLoginSerializer):
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        # Ensure username is None instead of empty string
        if 'username' in data and data['username'] == '':
            data['username'] = None
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']

        # Set name from Google if not already set
        if not user.name:
            user.name = user.socialaccount_set.filter(provider='google').first().extra_data.get('name')

        user.save()  # Single save call after all modifications
        return attrs

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs['refresh'])
        access_token_expiration_timestamp = refresh.access_token.get('exp')
        if access_token_expiration_timestamp:
            dt_object = datetime.fromtimestamp(access_token_expiration_timestamp, tz=UTC)
            data['access_expiration'] = dt_object.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return data

class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']

    def update(self, instance, validated_data):
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance

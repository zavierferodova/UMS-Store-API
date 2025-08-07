from dj_rest_auth.registration.serializers import SocialLoginSerializer

class CustomSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']

        if not user.name:
            user.name = user.socialaccount_set.filter(provider='google').first().extra_data.get('name')
            user.save()

        return attrs
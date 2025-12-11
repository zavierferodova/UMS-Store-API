from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'profile_image', 'email', 'username', 'role', 'gender', 'phone', 'address', 'last_login')
        read_only_fields = ('id', 'profile_image', 'last_login')

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None

class CustomUserDetailsSerializer(UserSerializer):
    pass

from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'username', 'role', 'gender', 'phone', 'address']

    def get_role(self, obj):
        if obj.groups.exists():
            return obj.groups.first().name
        return None

class CustomUserDetailsSerializer(UserSerializer):
    pass

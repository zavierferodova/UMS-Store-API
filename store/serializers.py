from rest_framework import serializers
from .models import Store

class StoreUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['name', 'address', 'phone', 'email', 'site']

from rest_framework import serializers
from products.models.category import ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['name'] = validated_data['name']
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'name' in validated_data:
            validated_data['name'] = validated_data['name']
        return super().update(instance, validated_data)
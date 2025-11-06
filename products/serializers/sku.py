from rest_framework import serializers

from products.models.product import Product
from products.models.sku import ProductSKU


class ProductSKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSKU
        fields = ['id', 'sku', 'stock']
        read_only_fields = ['id']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

class ProductSKUCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product'
    )

    class Meta:
        model = ProductSKU
        fields = ['id', 'sku', 'stock', 'product_id']
        read_only_fields = ['id']

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class ProductSKUListSerializer(serializers.ModelSerializer):
    """
    Serializer for SKU list that includes product information.
    Unlike ProductSerializer, this shows a single SKU instead of a list.
    """
    id = serializers.UUIDField(source='product.id', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    description = serializers.CharField(source='product.description', read_only=True)
    price = serializers.IntegerField(source='product.price', read_only=True)
    category = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    stock = serializers.IntegerField(read_only=True)
    additional_info = serializers.JSONField(source='product.additional_info', read_only=True)
    is_deleted = serializers.BooleanField(source='product.is_deleted', read_only=True)
    created_at = serializers.DateTimeField(source='product.created_at', read_only=True)
    updated_at = serializers.DateTimeField(source='product.updated_at', read_only=True)

    class Meta:
        model = ProductSKU
        fields = ['id', 'images', 'name', 'description', 'price', 'category', 'sku', 'stock', 'additional_info', 'is_deleted', 'created_at', 'updated_at']

    def get_category(self, obj):
        if obj.product.category:
            from products.serializers.category import ProductCategorySerializer
            return ProductCategorySerializer(obj.product.category).data
        return None

    def get_images(self, obj):
        from products.serializers.image import ProductImageNestedOutputSerializer
        return ProductImageNestedOutputSerializer(obj.product.productimage_set.all(), many=True).data

    def get_sku(self, obj):
        return ProductSKUSerializer(obj).data

from rest_framework import serializers

from products.models.image import ProductImage
from products.models.product import Product


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True, source='filename')

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product_id', 'order_number', 'created_at', 'updated_at']
        extra_kwargs = {
            'product_id': {'required': True, 'source': 'product'}
        }

class ProductImageNestedOutputSerializer(ProductImageSerializer):
    class Meta(ProductImageSerializer.Meta):
        fields = ['id', 'image', 'order_number', 'created_at', 'updated_at']
        extra_kwargs = {}

class ProductImageBulkSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(), max_length=10, required=True)
    product_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        images = attrs.get('images')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError({'product_id': 'Product not found'})

        if product.productimage_set.count() + len(images) > 10:
            raise serializers.ValidationError(f'Maximum of 10 images per product. This product already has {product.productimage_set.count()} images')

        attrs['product'] = product
        return attrs

    def create(self, validated_data):
        product = validated_data.get('product')
        images = validated_data.get('images')

        last_order = product.productimage_set.order_by('-order_number').first()
        last_order_number = last_order.order_number if last_order else -1

        product_images = [
            ProductImage(
                product=product,
                filename=image,
                order_number=last_order_number + i + 1
            ) for i, image in enumerate(images)
        ]

        return ProductImage.objects.bulk_create(product_images)

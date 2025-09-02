from rest_framework import serializers
from products.models.product import Product
from products.models.category import ProductCategory
from products.serializers.category import ProductCategorySerializer
from products.serializers.image import ProductImageNestedOutputSerializer
from products.models.sku import ProductSKU
from django.core.validators import RegexValidator
from products.serializers.sku import ProductSKUNestedSerializer

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        allow_null=True,
        required=False
    )
    images = ProductImageNestedOutputSerializer(many=True, read_only=True, source='productimage_set')
    skus = serializers.ListField(
        child=serializers.CharField(
            max_length=50,
            validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed for SKU.')]
        ),
        write_only=True,
        required=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'additional_info', 'category', 'images', 'created_at', 'updated_at', 'skus']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        skus_data = validated_data.pop('skus', [])
        product = super().create(validated_data)

        try:
            for sku_string in skus_data:
                product_sku, created = ProductSKU.objects.get_or_create(
                    sku=sku_string,
                    defaults={'product': product}
                )
                if not created and product_sku.product != product:
                    raise serializers.ValidationError({"skus": f"SKU '{sku_string}' is already associated with another product."})
                elif not created and product_sku.product == product:
                    pass
                else:
                    product_sku.product = product
                    product_sku.save()
        except Exception as e:
            product.delete()
            raise e

        return product

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = ProductCategorySerializer(instance.category).data
        
        # Return all SKUs associated with the product
        representation['skus'] = ProductSKUNestedSerializer(instance.skus.all(), many=True).data
        return representation
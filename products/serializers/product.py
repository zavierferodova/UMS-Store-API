from django.core.validators import RegexValidator
from rest_framework import serializers

from products.models.category import ProductCategory
from products.models.product import Product
from products.models.sku import ProductSKU
from products.serializers.category import ProductCategorySerializer
from products.serializers.image import ProductImageNestedOutputSerializer
from products.serializers.sku import ProductSKUSerializer
from suppliers.models.supplier import Supplier


class ProductSKUInputSerializer(serializers.Serializer):
    sku = serializers.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed for SKU.')]
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(),
        required=False,
        allow_null=True
    )


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        allow_null=True,
        required=False
    )
    images = ProductImageNestedOutputSerializer(many=True, read_only=True, source='productimage_set')
    skus = serializers.ListField(
        child=ProductSKUInputSerializer(),
        write_only=True,
        required=True
    )
    price = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = Product
        fields = ['id', 'images', 'name', 'description', 'price', 'category', 'skus', 'additional_info', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_price(self, value):
        if value == "" or value is None:
            return 0
        return value

    def validate_additional_info(self, value):
        if value is None:
            return value

        if not isinstance(value, list):
            raise serializers.ValidationError("This field must be a list of objects.")

        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Each item in the list must be an object.")
            if 'label' not in item or 'value' not in item:
                raise serializers.ValidationError("Each object must have 'label' and 'value' keys.")
            if not isinstance(item['label'], str) or not isinstance(item['value'], str):
                raise serializers.ValidationError("The 'label' and 'value' must be strings.")

        return value

    def create(self, validated_data):
        skus_data = validated_data.pop('skus', [])
        product = super().create(validated_data)

        try:
            for sku_data in skus_data:
                sku_string = sku_data.get('sku')
                supplier = sku_data.get('supplier')

                product_sku, created = ProductSKU.objects.get_or_create(
                    sku=sku_string,
                    defaults={
                        'product': product,
                        'supplier': supplier
                    }
                )
                if not created and product_sku.product != product:
                    raise serializers.ValidationError({"skus": f"SKU '{sku_string}' is already associated with another product."})
                elif not created and product_sku.product == product:
                    if supplier:
                        product_sku.supplier = supplier
                        product_sku.save()
                else:
                    pass
        except Exception as e:
            product.delete()
            raise e

        return product

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.category:
            representation['category'] = ProductCategorySerializer(instance.category).data

        representation['skus'] = ProductSKUSerializer(instance.skus.all().order_by('created_at'), many=True).data
        return representation


class ProductSingleSKUSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        allow_null=True,
        required=False
    )
    images = ProductImageNestedOutputSerializer(many=True, read_only=True, source='productimage_set')
    sku = serializers.CharField(
        max_length=50,
        validators=[RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed for SKU.')],
        write_only=True,
        required=True
    )

    class Meta:
        model = Product
        fields = ['id', 'images', 'name', 'description', 'price', 'category', 'sku', 'additional_info', 'is_deleted', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.category:
            representation['category'] = ProductCategorySerializer(instance.category).data

        # Check if a specific SKU is provided in the context
        product_sku = self.context.get('product_sku')
        representation['sku'] = ProductSKUSerializer(product_sku).data
        
        return representation


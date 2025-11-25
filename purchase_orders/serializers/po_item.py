from rest_framework import serializers

from products.models.sku import ProductSKU
from products.serializers.product import ProductSingleSKUSerializer
from purchase_orders.models.po_item import PoItem
from purchase_orders.models.purchase_order import PurchaseOrder


class PoItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(read_only=True)
    product_sku = serializers.SlugRelatedField(
        queryset=ProductSKU.objects.all(),
        slug_field='sku',
        write_only=True
    )
    purchase_order = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseOrder.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = PoItem
        fields = [
            "id",
            "purchase_order",
            "product_sku",
            "product",
            "price",
            "amounts",
            "supplier_discount",
            "return_status",
            "remain_stock",
            "created_at",
            "updated_at",
        ]

    def get_product(self, obj):
        """Get product with the specific SKU from this PO item"""
        return ProductSingleSKUSerializer(
            obj.product_sku.product,
            context={'product_sku': obj.product_sku}
        ).data

    def _validate_purchase_order_status(self, purchase_order):
        """Validate that purchase order is in draft status"""
        if purchase_order.status != PurchaseOrder.Status.DRAFT:
            raise serializers.ValidationError(
                "The purchase order item only can be modified if purchase order is in draft status"
            )

    def create(self, validated_data):
        view = self.context.get('view')
        if view and hasattr(view, 'kwargs'):
            purchase_order_id = view.kwargs.get('purchase_order_pk')
            if purchase_order_id:
                purchase_order = PurchaseOrder.objects.get(pk=purchase_order_id)
                self._validate_purchase_order_status(purchase_order)
                validated_data['purchase_order'] = purchase_order
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._validate_purchase_order_status(instance.purchase_order)
        return super().update(instance, validated_data)

class NestedPoItemSerializer(serializers.Serializer):
    """Serializer for creating items when creating a purchase order"""
    product_sku = serializers.SlugRelatedField(
        queryset=ProductSKU.objects.all(),
        slug_field='sku'
    )
    price = serializers.IntegerField()
    amounts = serializers.IntegerField()
    supplier_discount = serializers.FloatField(required=False, allow_null=True)

    def create(self, validated_data):
        return PoItem.objects.create(**validated_data)

class ReplacePoItemsSerializer(serializers.Serializer):
    """Serializer for replacing all items in a purchase order"""
    items = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=False
    )

    def validate_items(self, value):
        """Validate each item in the list"""
        validated_items = []
        for item_data in value:
            item_serializer = NestedPoItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            validated_items.append(item_serializer.validated_data)
        return validated_items

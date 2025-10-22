from rest_framework import serializers
from purchase_orders.models.po_item import PoItem
from products.models.sku import ProductSKU
from purchase_orders.models.purchase_order import PurchaseOrder
from products.serializers.product import ProductSerializer

class PoItemSerializer(serializers.ModelSerializer):
    product_sku = serializers.SlugRelatedField(
        queryset=ProductSKU.objects.all(),
        slug_field='sku'
    )
    product = ProductSerializer(source='product_sku.product', read_only=True)
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

    def create(self, validated_data):
        view = self.context.get('view')
        if view and hasattr(view, 'kwargs'):
            purchase_order_id = view.kwargs.get('purchase_order_pk')
            if purchase_order_id:
                validated_data['purchase_order'] = PurchaseOrder.objects.get(pk=purchase_order_id)
        return super().create(validated_data)
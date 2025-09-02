from rest_framework import viewsets, status
from rest_framework.decorators import action
from products.models.sku import ProductSKU
from products.serializers.sku import ProductSKUStockUpdateSerializer
from api.utils import api_response

class ProductSKUViewSet(viewsets.ModelViewSet):
    queryset = ProductSKU.objects.all()
    serializer_class = ProductSKUStockUpdateSerializer
    lookup_field = 'sku'

    @action(detail=True, methods=['get'])
    def check(self, request, sku=None):
        try:
            sku_instance = self.get_object()
            # If SKU exists, availability is false as per user's request
            is_available = False
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="SKU availability checked successfully",
                data={'sku': sku_instance.sku, 'is_available': is_available}
            )
            return response_obj
        except ProductSKU.DoesNotExist:
            # If SKU does t exist, availability is true as per user's request
            is_available = True
            response_obj = api_response(
                status=status.HTTP_200_OK, # Changed to 200 OK as it's a valid check result
                success=True,
                message="SKU availability checked successfully",
                data={'sku': sku, 'is_available': is_available}
            )
            return response_obj

    def partial_update(self, request, *args, **kwargs):
        try:
            sku_instance = self.get_object()
        except ProductSKU.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="SKU not found.",
                error="SKU not found."
            )
            return response_obj

        serializer = self.get_serializer(sku_instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="SKU stock updated successfully",
                data=serializer.data
            )
            return response_obj
        response_obj = api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data provided for SKU stock update.",
            error=serializer.errors
        )
        return response_obj

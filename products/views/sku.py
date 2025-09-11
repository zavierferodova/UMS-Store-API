from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from products.models.sku import ProductSKU
from products.serializers.sku import ProductSKUSerializer, ProductSKUCreateSerializer
from api.utils import api_response

class ProductSKUViewSet(viewsets.ModelViewSet):
    queryset = ProductSKU.objects.all()
    serializer_class = ProductSKUSerializer
    lookup_field = 'sku'

    def get_serializer_class(self):
        if self.action == 'create':
            return ProductSKUCreateSerializer
        return ProductSKUSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            response_obj = api_response(
                status=status.HTTP_201_CREATED,
                success=True,
                message="SKU created successfully",
                data=serializer.data
            )
            return response_obj
        response_obj = api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data provided for SKU creation.",
            error=serializer.errors
        )
        return response_obj

    @action(detail=True, methods=['get'])
    def check(self, request, sku=None):
        try:
            sku_instance = self.get_object()
            is_available = False
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="SKU availability checked successfully",
                data={'sku': sku_instance.sku, 'is_available': is_available}
            )
            return response_obj
        except (Http404, ProductSKU.DoesNotExist):
            is_available = True
            response_obj = api_response(
                status=status.HTTP_200_OK,
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
                message="SKU updated successfully",
                data=serializer.data
            )
            return response_obj
        response_obj = api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data provided for SKU update.",
            error=serializer.errors
        )
        return response_obj

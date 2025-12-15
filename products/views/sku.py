from uuid import UUID

from django.db.models import Q
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from products.models.sku import ProductSKU
from products.serializers.sku import ProductSKUCreateSerializer, ProductSKUListSerializer, ProductSKUSerializer


class ProductSKUViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = ProductSKU.objects.select_related('product', 'product__category').prefetch_related('product__productimage_set').all()
    serializer_class = ProductSKUSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['sku', 'product__name']
    lookup_field = 'sku'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductSKUListSerializer
        elif self.action == 'create':
            return ProductSKUCreateSerializer
        return ProductSKUSerializer

    def list(self, request, *args, **kwargs):
        """
        List all SKUs with pagination and filtering.
        Supports search by SKU number and product name via the 'search' query parameter.
        Supports pagination via 'page' and 'limit' query parameters.
        Supports status filter (active/deleted) via 'status' query parameter.
        Supports filtering by supplier via 'supplier_id' query parameter.
        Supports filtering by categories via 'categories' query parameter (comma-separated UUIDs).
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Handle status filter parameter (comma-separated values: active,deleted)
        status_param = request.query_params.get('status', '').lower()
        if status_param:
            status_values = [v.strip() for v in status_param.split(',')]
            status_filter = Q()
            if 'active' in status_values:
                status_filter |= Q(product__is_deleted=False)
            if 'deleted' in status_values:
                status_filter |= Q(product__is_deleted=True)
            if status_filter:
                queryset = queryset.filter(status_filter)
        else:
            # Default to showing only active (non-deleted) products
            queryset = queryset.filter(product__is_deleted=False)

        # Filter by supplier if provided
        supplier_id = request.query_params.get('supplier_id')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
        # Apply category filter if categories parameter is provided
        categories_param = request.query_params.get('categories')
        if categories_param:
            try:
                category_uuids = []
                for cid in categories_param.split(','):
                    try:
                        category_uuids.append(UUID(cid.strip()))
                    except (ValueError, AttributeError):
                        continue
                if category_uuids:
                    queryset = queryset.filter(product__category_id__in=category_uuids)
            except (ValueError, AttributeError):
                pass

        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="SKUs retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        response_obj = api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="SKUs retrieved successfully",
            data=serializer.data
        )
        return Response(response_obj.data, status=response_obj.status_code)

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

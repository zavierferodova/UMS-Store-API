from uuid import UUID

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsProcurement
from products.models.product import Product
from products.serializers.product import ProductSerializer


class ProductViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'skus__sku']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply category filter if categories parameter is provided
        categories_param = self.request.query_params.get('categories')
        if categories_param:
            try:
                category_uuids = []
                for cid in categories_param.split(','):
                    try:
                        category_uuids.append(UUID(cid.strip()))
                    except (ValueError, AttributeError):
                        continue
                if category_uuids:
                    queryset = queryset.filter(category_id__in=category_uuids)
            except (ValueError, AttributeError):
                pass

        # Only apply deletion status filtering for list requests
        if self.action == 'list':
            status_param = self.request.query_params.get('deletion', '').lower()
            if status_param:
                status_list = [s.strip() for s in status_param.split(',')]
                status_filter = Q()
                if 'active' in status_list:
                    status_filter |= Q(is_deleted=False)
                if 'deleted' in status_list:
                    status_filter |= Q(is_deleted=True)
                if status_filter:
                    queryset = queryset.filter(status_filter)
            else:
                # Default to showing only active products for list view
                queryset = queryset.filter(is_deleted=False)

        return queryset.order_by('-updated_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Products retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        response_obj = api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Products retrieved successfully",
            data=serializer.data
        )
        return Response(response_obj.data, status=response_obj.status_code)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Product retrieved successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except Product.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Product not found"
            )
            return Response(response_obj.data, status=response_obj.status_code)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_obj = api_response(
                status=status.HTTP_201_CREATED,
                success=True,
                message="Product created successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code, headers=headers)
        response_obj = api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            error=serializer.errors
        )
        return Response(response_obj.data, status=response_obj.status_code)

    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Product updated successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code)
        response_obj = api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            error=serializer.errors
        )
        return Response(response_obj.data, status=response_obj.status_code)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted'])
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Product deleted successfully",
                data=None
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except Product.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Product not found"
            )
            return Response(response_obj.data, status=response_obj.status_code)

from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from api.mixins import CustomPaginationMixin
from api.utils import api_response
from products.serializers.product import ProductSerializer
from products.models.product import Product
from api.pagination import CustomPagination
from rest_framework.filters import SearchFilter
from authentication.permissions import IsAdminGroup, IsProcurementGroup

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
            permission_classes = [permissions.IsAuthenticated, (IsAdminGroup | IsProcurementGroup)]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
        
    def get_queryset(self):
        """
        Returns the queryset with optional ordering.
        Default ordering is by name (A-Z).
        """
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', 'name')  # Default ordering by name
        
        # Apply ordering
        if ordering.startswith('-'):
            queryset = queryset.order_by(ordering[1:]).reverse()  # Descending order
        else:
            queryset = queryset.order_by(ordering)  # Ascending order
            
        return queryset

    def list(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
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
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )
            return Response(response_obj.data, status=response_obj.status_code)

    def create(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )
            return Response(response_obj.data, status=response_obj.status_code)

    def partial_update(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )
            return Response(response_obj.data, status=response_obj.status_code)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
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

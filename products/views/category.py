from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from api.mixins import CustomPaginationMixin
from api.utils import api_response
from products.serializers.category import ProductCategorySerializer
from products.models.product import Product
from products.models.category import ProductCategory
from api.pagination import CustomPagination
from rest_framework.filters import SearchFilter
from authentication.permissions import IsAdminGroup, IsProcurementGroup

class CategoryViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, (IsAdminGroup | IsProcurementGroup)]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data, message="Categories retrieved successfully")

            serializer = self.get_serializer(queryset, many=True)
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Categories retrieved successfully",
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
                message="Category retrieved successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except ProductCategory.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Category not found"
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
                    message="Category created successfully",
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
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except Exception as e:
            response_obj = api_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                success=False,
                message=str(e)
            )
            return Response(response_obj.data, status=response_obj.status_code)
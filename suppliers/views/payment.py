from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsProcurement
from suppliers.models.payment import SupplierPayment
from suppliers.serializers.payment import SupplierPaymentSerializer


class SupplierPaymentViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    serializer_class = SupplierPaymentSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
    filter_backends = [SearchFilter]
    search_fields = ['supplier__name', 'supplier__code', 'name', 'owner', 'account_number']

    def get_queryset(self):
        queryset = SupplierPayment.objects.all()

        if self.action == 'list':
            queryset = queryset.filter(supplier__is_deleted=False)

            supplier_id_param = self.request.query_params.get('supplier_id')
            if supplier_id_param:
                queryset = queryset.filter(supplier_id=supplier_id_param)

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
                # Default to showing only active payments for list view
                queryset = queryset.filter(is_deleted=False)

        return queryset.order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response_obj = api_response(
                status=status.HTTP_201_CREATED,
                success=True,
                message="Supplier payment created successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code, headers=headers)
        return api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            error=serializer.errors
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Supplier payments retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Supplier payments retrieved successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Supplier payment retrieved successfully",
                data=serializer.data
            )
        except SupplierPayment.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Supplier payment not found"
            )

    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Supplier payment updated successfully",
                data=serializer.data
            )
        return api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            error=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.is_deleted:
                return api_response(
                    status=status.HTTP_404_NOT_FOUND,
                    success=False,
                    message="Supplier payment not found"
                )
            
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted', 'updated_at'])
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Supplier payment deleted successfully"
            )
        except SupplierPayment.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Supplier payment not found"
            )
        

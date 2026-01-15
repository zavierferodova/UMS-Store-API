from django.db import models
from django.db.models import Q
from rest_framework import permissions, status, viewsets

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsChecker, IsProcurement
from purchase_orders.models.purchase_order import PurchaseOrder
from purchase_orders.serializers.purchase_order import PurchaseOrderSerializer


class PurchaseOrderViewSet(CustomPaginationMixin, viewsets.ModelViewSet):

    serializer_class = PurchaseOrderSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.role == 'checker':
            qs = PurchaseOrder.objects.exclude(
                status=PurchaseOrder.Status.DRAFT,
            ) | PurchaseOrder.objects.filter(
                status=PurchaseOrder.Status.DRAFT,
                requester=user
            )

            return qs.order_by('-updated_at')
        elif user.role == 'procurement':
            qs = PurchaseOrder.objects.filter(requester=user)
            return qs.order_by('-updated_at')

        return PurchaseOrder.objects.none()

    def get_permissions(self):
        user = self.request.user

        if user.role == 'checker':
            if self.action in ['list', 'update', 'partial_update', 'retrieve']:
                permission_classes = [permissions.IsAuthenticated, IsChecker]
        else:
            permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
            
        # Handle search query parameter
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(code__icontains=search_query) |
                models.Q(name__icontains=search_query) |
                models.Q(requester__name__icontains=search_query) |
                models.Q(approver__name__icontains=search_query) |
                models.Q(supplier__name__icontains=search_query)
            )
            
        # Handle status filter parameter (comma-separated values: draft,waiting_approval,approved,rejected,completed)
        status_filter_param = request.query_params.get('po_status', '').lower()
        if status_filter_param:
            status_values = [v.strip() for v in status_filter_param.split(',')]
            status_query_filter = Q()
            
            for status_value in status_values:
                if status_value in ['draft', 'waiting_approval', 'approved', 'rejected', 'completed']:
                    status_query_filter |= Q(status=status_value)
                    
            if status_query_filter:
                queryset = queryset.filter(status_query_filter)
                
        # Handle payment_option filter parameter (comma-separated values: cash,partnership)
        payment_option_param = request.query_params.get('payment_option', '').lower()
        if payment_option_param:
            payment_option_values = [v.strip() for v in payment_option_param.split(',')]
            payment_option_filter = Q()
            
            if 'cash' in payment_option_values:
                payment_option_filter |= Q(payment_option='cash')
            if 'partnership' in payment_option_values:
                payment_option_filter |= Q(payment_option='partnership')
                
            if payment_option_filter:
                queryset = queryset.filter(payment_option_filter)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                serializer.data,
                message=f"{len(serializer.data)} purchase orders found" if search_query
                        else "Purchase orders retrieved successfully"
            )

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message=f"{len(serializer.data)} purchase orders found" if search_query
                    else "Purchase orders retrieved successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            status=status.HTTP_201_CREATED,
            success=True,
            message="Purchase order created successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Purchase order retrieved successfully",
                data=serializer.data
            )
        except PurchaseOrder.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Purchase order not found",
                data=None
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            old_status = instance.status

            # Constraint: If already approved, can only transition to completed
            if old_status == PurchaseOrder.Status.APPROVED:
                new_status = request.data.get('status')
                if new_status and new_status != PurchaseOrder.Status.COMPLETED and new_status != PurchaseOrder.Status.APPROVED:
                    return api_response(
                        status=status.HTTP_400_BAD_REQUEST,
                        success=False,
                        message="Approved purchase orders can only be updated to Completed status",
                        data=None
                    )

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Purchase order updated successfully",
                data=serializer.data
            )
        except PurchaseOrder.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Purchase order not found",
                data=None
            )

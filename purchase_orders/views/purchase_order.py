from django.db import models
from django.db.models import Q
from rest_framework import permissions, status, viewsets

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdminGroup, IsProcurementGroup
from purchase_orders.models.purchase_order import PurchaseOrder
from purchase_orders.serializers.purchase_order import PurchaseOrderSerializer


class PurchaseOrderViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [permissions.IsAuthenticated, (IsAdminGroup | IsProcurementGroup)]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Handle status filter parameter (comma-separated values: active,deleted)
        status_param = request.query_params.get('status', '').lower()
        if status_param:
            status_values = [v.strip() for v in status_param.split(',')]
            status_filter = Q()
            
            if 'active' in status_values:
                status_filter |= Q(is_deleted=False)
            if 'deleted' in status_values:
                status_filter |= Q(is_deleted=True)
                
            if status_filter:
                queryset = queryset.filter(status_filter)
        else:
            # Default to showing only active (non-deleted) purchase orders
            queryset = queryset.filter(is_deleted=False)
            
        # Handle search query parameter
        search_query = request.query_params.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                models.Q(code__icontains=search_query) |
                models.Q(user__name__icontains=search_query) |
                models.Q(supplier__name__icontains=search_query)
            )
            
        # Handle draft filter parameter (comma-separated values: true,false)
        draft_param = request.query_params.get('draft', '').lower()
        if draft_param:
            draft_values = [v.strip() for v in draft_param.split(',')]
            draft_filter = Q()
            
            if 'true' in draft_values:
                draft_filter |= Q(draft=True)
            if 'false' in draft_values:
                draft_filter |= Q(draft=False)
                
            if draft_filter:
                queryset = queryset.filter(draft_filter)
                
        # Handle completed filter parameter (comma-separated values: true,false)
        completed_param = request.query_params.get('completed', '').lower()
        if completed_param:
            completed_values = [v.strip() for v in completed_param.split(',')]
            completed_filter = Q()
            
            if 'true' in completed_values:
                completed_filter |= Q(completed=True)
            if 'false' in completed_values:
                completed_filter |= Q(completed=False)
                
            if completed_filter:
                queryset = queryset.filter(completed_filter)
                
        # Handle payout filter parameter (comma-separated values: cash,partnership)
        payout_param = request.query_params.get('payout', '').lower()
        if payout_param:
            payout_values = [v.strip() for v in payout_param.split(',')]
            payout_filter = Q()
            
            if 'cash' in payout_values:
                payout_filter |= Q(payout='cash')
            if 'partnership' in payout_values:
                payout_filter |= Q(payout='partnership')
                
            if payout_filter:
                queryset = queryset.filter(payout_filter)
            
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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            if instance.is_deleted:
                return api_response(
                    status=status.HTTP_404_NOT_FOUND,
                    success=False,
                    message="Purchase order not found",
                    data=None
                )
                
            instance.is_deleted = True
            instance.save(update_fields=['is_deleted', 'updated_at'])
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Purchase order deleted successfully",
                data=None
            )
        except PurchaseOrder.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Purchase order not found",
                data=None
            )

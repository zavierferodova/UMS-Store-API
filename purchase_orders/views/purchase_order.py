from rest_framework import status, viewsets, permissions

from api.pagination import CustomPagination
from api.mixins import CustomPaginationMixin
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
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Purchase orders retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Purchase orders retrieved successfully",
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

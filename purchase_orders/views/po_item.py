from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdminGroup, IsProcurementGroup
from purchase_orders.models.po_item import PoItem
from purchase_orders.models.purchase_order import PurchaseOrder
from purchase_orders.serializers.po_item import PoItemSerializer, ReplacePoItemsSerializer


class PoItemViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows po items to be viewed or edited.
    """

    serializer_class = PoItemSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        permission_classes = [permissions.IsAuthenticated, (IsAdminGroup | IsProcurementGroup)]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        purchase_order_pk = self.kwargs['purchase_order_pk']
        return PoItem.objects.filter(purchase_order__pk=purchase_order_pk)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view'] = self
        return context
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="PO items retrieved successfully")
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="PO items retrieved successfully",
            data=serializer.data
        )
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(
            status=status.HTTP_201_CREATED,
            success=True,
            message="PO item created successfully",
            data=serializer.data
        )
    
    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="PO item retrieved successfully",
                data=serializer.data
            )
        except PoItem.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="PO item not found"
            )
    
    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="PO item updated successfully",
                data=serializer.data
            )
        except PoItem.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="PO item not found"
            )

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check if purchase order is in draft status
            if instance.purchase_order.status != PurchaseOrder.Status.DRAFT:
                return api_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    success=False,
                    message="The purchase order item only can be deleted if purchase order is in draft status"
                )
            
            self.perform_destroy(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="PO item deleted successfully"
            )
        except PoItem.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="PO item not found"
            )

    @action(detail=False, methods=['post'], url_path='replace')
    def replace_items(self, request, purchase_order_pk=None):
        """
        Replace all PO items for a purchase order.
        Deletes all existing items and creates new ones from the provided list.
        """
        try:
            # Get the purchase order
            purchase_order = PurchaseOrder.objects.get(pk=purchase_order_pk)
            
            # Check if purchase order is in draft status
            if purchase_order.status != PurchaseOrder.Status.DRAFT:
                return api_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    success=False,
                    message="The purchase order items only can be replaced if purchase order is in draft status"
                )
            
            # Validate the request data
            serializer = ReplacePoItemsSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Delete all existing items for this purchase order
            PoItem.objects.filter(purchase_order=purchase_order).delete()
            
            # Create new items
            items_data = serializer.validated_data['items']
            created_items = []
            
            for item_data in items_data:
                item_data['purchase_order'] = purchase_order
                po_item = PoItem.objects.create(**item_data)
                created_items.append(po_item)
            
            # Serialize the created items for response
            response_serializer = PoItemSerializer(created_items, many=True, context={'request': request})
            
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="PO items replaced successfully",
                data=response_serializer.data
            )
            
        except PurchaseOrder.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Purchase order not found"
            )

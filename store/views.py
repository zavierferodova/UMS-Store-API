from rest_framework import permissions, status, viewsets

from api.utils import api_response
from authentication.permissions import IsAdminGroup, IsCashierGroup

from .models import Store
from .serializers import StoreUpdateSerializer


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminGroup | IsCashierGroup]
    queryset = Store.objects.all()

    def list(self, request, *args, **kwargs):
        instance = Store.objects.filter(pk=1).first()
        if not instance:
            return api_response(status=status.HTTP_404_NOT_FOUND, success=False, message="Store not found.")
        serializer = self.get_serializer(instance)
        return api_response(status=status.HTTP_200_OK, success=True, message="Store details retrieved successfully.", data=serializer.data)

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = Store.objects.get(pk=1)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return api_response(status=status.HTTP_200_OK, success=True, message="Store updated successfully.", data=serializer.data)
        except Store.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(id=1)
            return api_response(status=status.HTTP_201_CREATED, success=True, message="Store created successfully.", data=serializer.data)

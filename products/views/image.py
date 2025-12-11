from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from api.utils import api_response
from authentication.permissions import IsAdmin, IsProcurement
from products.models.image import ProductImage
from products.serializers.image import ProductImageBulkSerializer, ProductImageSerializer


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Product image retrieved successfully",
                data=serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except ProductImage.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Product image not found"
            )
            return Response(response_obj.data, status=response_obj.status_code)

    def create(self, request, *args, **kwargs):
        serializer = ProductImageBulkSerializer(data=request.data)
        if serializer.is_valid():
            images = serializer.save()
            response_serializer = ProductImageSerializer(images, many=True, context={'request': request})
            response_obj = api_response(
                status=status.HTTP_201_CREATED,
                success=True,
                message="Product images uploaded successfully",
                data=response_serializer.data
            )
            return Response(response_obj.data, status=response_obj.status_code)
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
                message="Product image updated successfully",
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
            product_id = instance.product_id
            self.perform_destroy(instance)

            # Reorder the remaining images
            remaining_images = ProductImage.objects.filter(product_id=product_id).order_by('order_number')
            for i, image in enumerate(remaining_images):
                image.order_number = i
                image.save()

            response_obj = api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Product image deleted successfully",
                data=None
            )
            return Response(response_obj.data, status=response_obj.status_code)
        except ProductImage.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Product image not found"
            )
            return Response(response_obj.data, status=response_obj.status_code)

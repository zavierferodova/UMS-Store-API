from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsProcurement

from .models import User
from .serializers import UserSerializer


class UserViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['email', 'username', 'name']

    def get_permissions(self):
        """
        Rules:
        - List / Retrieve → Admin OR Procurement
        - Update (partial_update) → Admin only
        """
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
        elif self.action == 'retrieve':
            permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsProcurement)]
        elif self.action in ['partial_update', 'update']:
            permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        roles = self.request.query_params.get('role')

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )

        if roles:
            try:
                role_list = [role.strip().lower() for role in roles.split(',')]
                queryset = queryset.filter(role__in=role_list).distinct()
            except Exception:
                pass

        return queryset.order_by('name')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Users retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        response_obj = api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Users retrieved successfully",
            data=serializer.data
        )
        return Response(response_obj.data, status=response_obj.status_code)

    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")
            instance = User.objects.get(Q(id__iexact=pk) | Q(username__iexact=pk))
        except User.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message=f"User with id or username {kwargs.get('pk')} not found."
            )
            return Response(response_obj.data, status=response_obj.status_code)

        serializer = self.get_serializer(instance)
        response_obj = api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="User retrieved successfully",
            data=serializer.data
        )
        return Response(response_obj.data, status=response_obj.status_code)

    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        try:
            instance = User.objects.get(Q(id__iexact=pk) | Q(username__iexact=pk))
        except User.DoesNotExist:
            response_obj = api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message=f"User with id or username {pk} not found."
            )
            return Response(response_obj.data, status=response_obj.status_code)

        # Handle role update
        role_name = request.data.get("role")
        if role_name:
            valid_roles = ["admin", "procurement", "cashier", "checker"]
            if role_name not in valid_roles:
                response_obj = api_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    success=False,
                    message=f"Invalid role provided. Role must be one of {valid_roles}."
                )
                return Response(response_obj.data, status=response_obj.status_code)
            
            instance.role = role_name
            instance.save()

        # Pass data to serializer (excluding role)
        mutable_data = request.data.copy()
        mutable_data.pop("role", None)

        serializer = self.get_serializer(instance, data=mutable_data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_obj = api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="User updated successfully",
            data=serializer.data
        )
        return Response(response_obj.data, status=response_obj.status_code)

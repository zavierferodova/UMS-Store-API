from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AND, OR
from authentication.permissions import IsAdminGroup, IsProcurementGroup
from .models import User
from .serializers import UserSerializer
from api.utils import api_response
from api.pagination import CustomPagination
from django.db.models import Q
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from django.contrib.auth.models import Group

class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminGroup | IsProcurementGroup]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=200,
            success=True,
            message='Users retrieved successfully.',
            data=serializer.data
        )

user_list = UserListView.as_view()

class UserDetailView(RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), OR(IsAdminGroup(), IsProcurementGroup())]
        elif self.request.method == 'PATCH':
            return [IsAuthenticated(), IsAdminGroup()]
        return [IsAuthenticated()]

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            if pk.isdigit():
                obj = User.objects.get(pk=pk)
            else:
                obj = User.objects.get(Q(email__iexact=pk) | Q(username__iexact=pk))
            self.check_object_permissions(self.request, obj)
            return obj
        except User.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return api_response(
                status=404,
                success=False,
                message=f'User with id or username {self.kwargs.get("pk")} not found.',
                error=[{'message': f'User with id or username {self.kwargs.get("pk")} not found.'}]
            )
        serializer = self.get_serializer(instance)
        return api_response(
            status=200,
            success=True,
            message='User retrieved successfully.',
            data=serializer.data
        )
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance is None:
            return api_response(
                status=404,
                success=False,
                message=f'User with id or username {self.kwargs.get("pk")} not found.',
                error=[{'message': f'User with id or username {self.kwargs.get("pk")} not found.'}]
            )
        
        role_name = request.data.get('role')
        if role_name:
            valid_roles = ['admin', 'procurement', 'cashier']
            if role_name not in valid_roles:
                return api_response(
                    status=400,
                    success=False,
                    message='Invalid role provided.',
                    error=[{'message': f'Role must be one of {valid_roles}.'}]
                )
            
            # Remove user from existing role groups
            groups_to_remove = instance.groups.filter(name__in=valid_roles)
            instance.groups.remove(*groups_to_remove)

            # Add user to the new role group
            try:
                group = Group.objects.get(name=role_name)
                instance.groups.add(group)
            except Group.DoesNotExist:
                return api_response(
                    status=400,
                    success=False,
                    message=f'Role group {role_name} does not exist.',
                    error=[{'message': f'Role group {role_name} does not exist.'}]
                )
        
        # Create a mutable copy of request.data to remove 'role' before passing to serializer
        mutable_data = request.data.copy()
        if 'role' in mutable_data:
            del mutable_data['role']

        serializer = self.get_serializer(instance, data=mutable_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(
            status=200,
            success=True,
            message='User updated successfully.',
            data=serializer.data
        )

user_detail = UserDetailView.as_view()

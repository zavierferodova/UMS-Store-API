from rest_framework.permissions import IsAuthenticated, OR
from authentication.permissions import IsAdminGroup, IsProcurementGroup
from .models import Supplier
from .serializers import SupplierSerializer
from api.utils import api_response
from api.pagination import CustomPagination
from django.db.models import Q
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView

class SupplierView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminGroup | IsProcurementGroup]
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return api_response(
                status=201,
                success=True,
                message='Supplier created successfully.',
                data=serializer.data
            )
        return api_response(
            status=400,
            success=False,
            message='Invalid data.',
            data=serializer.errors
        )

class SupplierListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminGroup | IsProcurementGroup]
    serializer_class = SupplierSerializer
    pagination_class = CustomPagination
    
    def get_queryset(self):
        queryset = Supplier.objects.all()
        status = self.request.query_params.get('status', '').lower()
        search = self.request.query_params.get('search')
        
        # Handle status filter
        if status:
            status_list = [s.strip() for s in status.split(',')]
            status_filter = Q()
            
            if 'active' in status_list:
                status_filter |= Q(is_deleted=False)
            if 'deleted' in status_list:
                status_filter |= Q(is_deleted=True)
                
            if status_filter:
                queryset = queryset.filter(status_filter)
        else:
            queryset = queryset.filter(is_deleted=False)
            
        # Handle search
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search) |
                Q(address__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
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
            message='Suppliers retrieved successfully.',
            data=serializer.data
        )

class SupplierDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), OR(IsAdminGroup(), IsProcurementGroup())]
        elif self.request.method == 'PATCH':
            return [IsAuthenticated(), OR(IsAdminGroup(), IsProcurementGroup())]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), OR(IsAdminGroup(), IsProcurementGroup())]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                status=200,
                success=True,
                message='Supplier retrieved successfully.',
                data=serializer.data
            )
        except Exception as e:
            return api_response(
                status=404,
                success=False,
                message='Supplier not found.'
            )

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return api_response(
                status=200,
                success=True,
                message='Supplier updated successfully.',
                data=serializer.data
            )
        except Exception as e:
            return api_response(
                status=400,
                success=False,
                message='Invalid data.',
                data=serializer.errors
            )

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.is_deleted = True
            instance.save()
            return api_response(
                status=200,
                success=True,
                message='Supplier deleted successfully.'
            )
        except Exception as e:
            return api_response(
                status=404,
                success=False,
                message='Supplier not found.'
            )

supplier_list = SupplierListView.as_view()
add_supplier = SupplierView.as_view()
supplier_detail = SupplierDetailView.as_view()

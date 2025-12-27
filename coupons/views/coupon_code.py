from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsCashier
from coupons.models.coupon_code import CouponCode
from coupons.serializers.coupon_code import CouponCodeSerializer


class CouponCodeViewSet(viewsets.ModelViewSet):
    queryset = CouponCode.objects.all()
    serializer_class = CouponCodeSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, (IsAdmin | IsCashier)]
    lookup_field = 'code'

    @action(detail=False, methods=['get'], url_path='(?P<code>[^/.]+)/check')
    def check_availability(self, request, code=None):
        is_available = not CouponCode.objects.filter(code=code).exists()
        data = {
            "code": code,
            "is_available": is_available
        }
        return api_response(200, True, "Check availability success", data)

    @action(detail=True, methods=['get'], url_path='usage')
    def check_usage(self, request, code=None):
        instance = self.get_object()
        used_count = instance.transactions.count()
        
        can_use = True
        if instance.coupon.disabled:
            can_use = False
        elif instance.disabled:
            can_use = False
        elif instance.stock <= used_count:
            can_use = False
        
        data = {
            "code": instance.code,
            "stock": instance.stock,
            "can_use": can_use
        }
        return api_response(200, True, "Check usage success", data)

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by disabled status
        disabled_param = self.request.query_params.get('disabled')
        if disabled_param:
            statuses = disabled_param.split(',')
            q_objects = Q()
            if 'active' in statuses:
                q_objects |= Q(disabled=False)
            if 'disabled' in statuses:
                q_objects |= Q(disabled=True)
            if q_objects:
                queryset = queryset.filter(q_objects)

        # Search by coupon name or code
        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(Q(code__icontains=search_param))

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(200, True, "Coupon codes retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(201, True, "Coupon code created successfully", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(200, True, "Coupon code retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(200, True, "Coupon code updated successfully", serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(204, True, "Coupon code deleted successfully")

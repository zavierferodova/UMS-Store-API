from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsCashier
from coupons.models.coupon import Coupon
from coupons.models.coupon_code import CouponCode
from coupons.serializers.coupon import CouponSerializer
from coupons.serializers.coupon_code import CouponCodeSerializer


class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, (IsAdmin | IsCashier)]

    @action(detail=True, methods=['get'], url_path='coupons')
    def get_coupons(self, request, pk=None):
        queryset = CouponCode.objects.filter(coupon_id=pk)
        
        # Filter by disabled status
        disabled_param = request.query_params.get('disabled')
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
        search_param = request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(Q(coupon__name__icontains=search_param) | Q(code__icontains=search_param))

        queryset = queryset.order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CouponCodeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CouponCodeSerializer(queryset, many=True)
        return api_response(200, True, "Coupon codes retrieved successfully", serializer.data)

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

        # Filter by type
        type_param = self.request.query_params.get('type')
        if type_param:
            types = type_param.split(',')
            queryset = queryset.filter(type__in=types)

        # Search by name
        search_param = self.request.query_params.get('search')
        if search_param:
            queryset = queryset.filter(name__icontains=search_param)

        # Filter by start_time
        start_time = self.request.query_params.get('start_time')
        if start_time:
            queryset = queryset.filter(start_time__gte=start_time)

        # Filter by end_time
        end_time = self.request.query_params.get('end_time')
        if end_time:
            queryset = queryset.filter(end_time__lte=end_time)

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(200, True, "Coupons retrieved successfully", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return api_response(201, True, "Coupon created successfully", serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(200, True, "Coupon retrieved successfully", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return api_response(200, True, "Coupon updated successfully", serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return api_response(204, True, "Coupon deleted successfully")

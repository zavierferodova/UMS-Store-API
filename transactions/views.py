from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status, viewsets

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsCashier
from transactions.models.transaction import Transaction
from transactions.serializers.transaction import TransactionSerializer, TransactionUpdateSerializer


class TransactionViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticated, (IsAdmin | IsCashier)]

    def get_queryset(self):
        queryset = Transaction.objects.all().order_by('-updated_at')
        user = self.request.user

        if getattr(user, 'role', None) == 'admin':
            queryset = queryset.filter(
                Q(is_saved=False) |
                Q(cashier_book_transactions__cashier_book__cashier=user)
            ).distinct()
        elif getattr(user, 'role', None) == 'cashier':
            queryset = queryset.filter(cashier_book_transactions__cashier_book__cashier=user)
        
        if self.action == 'list':
            search = self.request.query_params.get('search')
            cashier_id = self.request.query_params.get('cashier_id')
            start_date = self.request.query_params.get('start_date')
            end_date = self.request.query_params.get('end_date')
            transaction_status = self.request.query_params.get('transaction_status')
            payment = self.request.query_params.get('payment')

            if search:
                queryset = queryset.filter(
                    Q(code__icontains=search)
                )

            if cashier_id:
                queryset = queryset.filter(cashier_book_transactions__cashier_book__cashier_id=cashier_id)

            if start_date:
                queryset = queryset.filter(created_at__date__gte=start_date)

            if end_date:
                queryset = queryset.filter(created_at__date__lte=end_date)

            if transaction_status:
                status_list = [s.strip().lower() for s in transaction_status.split(',')]
                status_filter = []
                if 'saved' in status_list:
                    status_filter.append(True)
                if 'paid' in status_list:
                    status_filter.append(False)
                if status_filter:
                    queryset = queryset.filter(is_saved__in=status_filter)

            if payment:
                payment_list = [p.strip().lower() for p in payment.split(',')]
                queryset = queryset.filter(payment__in=payment_list)

        return queryset

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return TransactionUpdateSerializer
        return TransactionSerializer

    def perform_create(self, serializer):
        pay = serializer.validated_data.get('pay')
        if pay and pay != 0:
            serializer.save(paid_time=timezone.now())
        else:
            serializer.save()

    def perform_update(self, serializer):
        pay = serializer.validated_data.get('pay')
        
        if pay and pay != 0:
            serializer.save(paid_time=timezone.now())
        else:
            serializer.save()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Transactions retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Transactions retrieved successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return api_response(
            status=status.HTTP_201_CREATED,
            success=True,
            message="Transaction created successfully",
            data=response.data
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Transaction retrieved successfully",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        serializer = TransactionSerializer(instance)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Transaction updated successfully",
            data=serializer.data
        )

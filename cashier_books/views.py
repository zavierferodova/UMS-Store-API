from django.db.models import BigIntegerField, Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsCashier
from transactions.models.transaction import Transaction
from transactions.models.transaction_coupon import TransactionCoupon
from transactions.serializers.transaction import TransactionSerializer

from .models import CashierBook
from .serializers import CashierBookSerializer


class CashierBookViewSet(CustomPaginationMixin, viewsets.ModelViewSet):
    queryset = CashierBook.objects.all()
    serializer_class = CashierBookSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, (IsAdmin | IsCashier)]

    def get_queryset(self):
        queryset = CashierBook.objects.all().order_by('-time_open')
        user = self.request.user

        if getattr(user, 'role', None) == 'cashier':
            queryset = queryset.filter(cashier=user)

        if self.action == 'list':
            search = self.request.query_params.get('search')
            time_open = self.request.query_params.get('time_open')
            time_closed = self.request.query_params.get('time_closed')
            status_param = self.request.query_params.get('status')
            cashier_id = self.request.query_params.get('cashier_id') or self.request.query_params.get('cashier')

            if search:
                queryset = queryset.filter(
                    Q(code__icontains=search)
                )

            if time_open:
                queryset = queryset.filter(time_open__date=time_open)

            if time_closed:
                queryset = queryset.filter(time_closed__date=time_closed)

            if cashier_id:
                queryset = queryset.filter(cashier_id=cashier_id)

            if status_param:
                status_list = [s.strip().lower() for s in status_param.split(',')]
                status_q = Q()
                if 'open' in status_list:
                    status_q |= Q(time_closed__isnull=True)
                if 'closed' in status_list:
                    status_q |= Q(time_closed__isnull=False)
                
                if status_q:
                    queryset = queryset.filter(status_q)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Cashier books retrieved successfully")

        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Cashier books retrieved successfully",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return api_response(
                status=status.HTTP_201_CREATED,
                success=True,
                message="Cashier book created successfully",
                data=serializer.data
            )
        return api_response(
            status=status.HTTP_400_BAD_REQUEST,
            success=False,
            message="Invalid data",
            error=serializer.errors
        )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Cashier book retrieved successfully",
                data=serializer.data
            )
        except Exception:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Cashier book not found"
            )

    @action(detail=False, methods=['get'])
    def get_active_book(self, request):
        active_book = CashierBook.objects.filter(cashier=request.user, time_closed__isnull=True).order_by('-time_open').first()
        if active_book:
            serializer = self.get_serializer(active_book)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Active cashier book retrieved successfully",
                data=serializer.data
            )
        return api_response(
            status=status.HTTP_404_NOT_FOUND,
            success=False,
            message="No active cashier book found"
        )

    @action(detail=False, methods=['get'], url_path='active-stats')
    def active_stats(self, request):
        active_book = CashierBook.objects.filter(cashier=request.user, time_closed__isnull=True).order_by('-time_open').first()
        
        if not active_book:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="No active cashier book found"
            )

        transactions = Transaction.objects.filter(
            cashier_book_transactions__cashier_book=active_book,
            is_saved=False,
            paid_time__isnull=False
        )

        cash_stats = transactions.filter(payment='cash').aggregate(
            cnt=Count('id'),
            val=Coalesce(Sum(F('total')), 0, output_field=BigIntegerField())
        )

        cashless_stats = transactions.filter(payment='cashless').aggregate(
            cnt=Count('id'),
            val=Coalesce(Sum(F('total')), 0, output_field=BigIntegerField())
        )

        voucher_stats = TransactionCoupon.objects.filter(
            transaction__in=transactions,
            coupon_code__coupon__type='voucher'
        ).aggregate(
            cnt=Coalesce(Sum('amount'), 0),
            val=Coalesce(Sum(F('item_voucher_value') * F('amount')), 0, output_field=BigIntegerField())
        )

        discount_stats = TransactionCoupon.objects.filter(
            transaction__in=transactions,
            coupon_code__coupon__type='discount'
        ).aggregate(
            cnt=Coalesce(Sum('amount'), 0),
            val=Coalesce(Sum(F('item_discount_value') * F('amount')), 0, output_field=BigIntegerField())
        )

        data = {
            "cash": {
                "count": cash_stats['cnt'],
                "value": cash_stats['val']
            },
            "cashless": {
                "count": cashless_stats['cnt'],
                "value": cashless_stats['val']
            },
            "voucher": {
                "count": voucher_stats['cnt'],
                "value": voucher_stats['val']
            },
            "discount": {
                "count": discount_stats['cnt'],
                "value": discount_stats['val']
            }
        }

        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Active stats retrieved successfully",
            data=data
        )

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        try:
            book = CashierBook.objects.get(pk=pk)
        except CashierBook.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Cashier book not found"
            )

        transactions = Transaction.objects.filter(
            cashier_book_transactions__cashier_book=book,
            is_saved=False,
            paid_time__isnull=False
        )

        cash_stats = transactions.filter(payment='cash').aggregate(
            cnt=Count('id'),
            val=Coalesce(Sum(F('total')), 0, output_field=BigIntegerField())
        )

        cashless_stats = transactions.filter(payment='cashless').aggregate(
            cnt=Count('id'),
            val=Coalesce(Sum(F('total')), 0, output_field=BigIntegerField())
        )

        voucher_stats = TransactionCoupon.objects.filter(
            transaction__in=transactions,
            coupon_code__coupon__type='voucher'
        ).aggregate(
            cnt=Coalesce(Sum('amount'), 0),
            val=Coalesce(Sum(F('item_voucher_value') * F('amount')), 0, output_field=BigIntegerField())
        )

        discount_stats = TransactionCoupon.objects.filter(
            transaction__in=transactions,
            coupon_code__coupon__type='discount'
        ).aggregate(
            cnt=Coalesce(Sum('amount'), 0),
            val=Coalesce(Sum(F('item_discount_value') * F('amount')), 0, output_field=BigIntegerField())
        )

        data = {
            "cash": {
                "count": cash_stats['cnt'],
                "value": cash_stats['val']
            },
            "cashless": {
                "count": cashless_stats['cnt'],
                "value": cashless_stats['val']
            },
            "voucher": {
                "count": voucher_stats['cnt'],
                "value": voucher_stats['val']
            },
            "discount": {
                "count": discount_stats['cnt'],
                "value": discount_stats['val']
            }
        }

        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Stats retrieved successfully",
            data=data
        )

    @action(detail=False, methods=['patch'])
    def close_book(self, request):
        try:
            instance = CashierBook.objects.get(cashier=request.user, time_closed__isnull=True)
            instance.time_closed = timezone.now()
            instance.save()
            serializer = self.get_serializer(instance)
            return api_response(
                status=status.HTTP_200_OK,
                success=True,
                message="Cashier book closed successfully",
                data=serializer.data
            )
        except CashierBook.DoesNotExist:
            return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="No active cashier book found"
            )
        except Exception:
            return api_response(
                status=status.HTTP_400_BAD_REQUEST,
                success=False,
                message="Error closing cashier book"
            )

    def transactions(self, request, pk=None):
        try:
            cashier_book = CashierBook.objects.get(pk=pk)
        except CashierBook.DoesNotExist:
             return api_response(
                status=status.HTTP_404_NOT_FOUND,
                success=False,
                message="Cashier book not found"
            )
        
        queryset = Transaction.objects.filter(cashier_book_transactions__cashier_book=cashier_book).order_by('-updated_at')

        user = request.user
        if getattr(user, 'role', None) == 'admin':
            queryset = queryset.filter(
                Q(is_saved=False) |
                Q(cashier_book_transactions__cashier_book__cashier=user)
            ).distinct()

        search = self.request.query_params.get('search')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        transaction_status = self.request.query_params.get('transaction_status')
        payment = self.request.query_params.get('payment')

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
            )

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

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TransactionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data, message="Transactions retrieved successfully")

        serializer = TransactionSerializer(queryset, many=True, context={'request': request})
        return api_response(
            status=status.HTTP_200_OK,
            success=True,
            message="Transactions retrieved successfully",
            data=serializer.data
        )



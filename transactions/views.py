import openpyxl
from django.db.models import F, Q, Sum
from django.http import HttpResponse
from django.utils import timezone
from openpyxl.styles import Alignment, Border, Font, Side
from rest_framework import permissions, status, viewsets

from api.mixins import CustomPaginationMixin
from api.pagination import CustomPagination
from api.utils import api_response
from authentication.permissions import IsAdmin, IsCashier
from suppliers.models.supplier import Supplier
from transactions.models.transaction import Transaction
from transactions.models.transaction_item import TransactionItem
from transactions.serializers.transaction import TransactionSerializer, TransactionUpdateSerializer
from transactions.serializers.transaction_item import SupplierTransactionItemSerializer


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

    def supplier_products(self, request, supplier_id=None):
        user = request.user
        if getattr(user, 'role', None) != 'admin':
             return api_response(status=status.HTTP_403_FORBIDDEN, success=False, message="You do not have permission to access this resource.")
        
        if not supplier_id:
            return api_response(status=status.HTTP_400_BAD_REQUEST, success=False, message="Supplier ID is required.")

        queryset = TransactionItem.objects.filter(product_sku__supplier_id=supplier_id).select_related('transaction', 'product_sku__product', 'product_sku__product__category').order_by('-transaction__created_at')

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(transaction__paid_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction__paid_time__date__lte=end_date)
            
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_sku__product__name__icontains=search) |
                Q(product_sku__sku__icontains=search) |
                Q(transaction__code__icontains=search)
            )
            
        categories = request.query_params.get('categories')
        if categories:
            category_list = [c.strip() for c in categories.split(',')]
            queryset = queryset.filter(product_sku__product__category__id__in=category_list)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SupplierTransactionItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data, message="Supplier products transactions retrieved successfully")

        serializer = SupplierTransactionItemSerializer(queryset, many=True)
        return api_response(status=status.HTTP_200_OK, success=True, message="Supplier products transactions retrieved successfully", data=serializer.data)

    def export_supplier_products(self, request, supplier_id=None):
        user = request.user
        if getattr(user, 'role', None) != 'admin':
             return api_response(status=status.HTTP_403_FORBIDDEN, success=False, message="You do not have permission to access this resource.")
        
        if not supplier_id:
            return api_response(status=status.HTTP_400_BAD_REQUEST, success=False, message="Supplier ID is required.")
            
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            return api_response(status=status.HTTP_404_NOT_FOUND, success=False, message="Supplier not found.")

        queryset = TransactionItem.objects.filter(product_sku__supplier_id=supplier_id)

        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        if start_date:
            queryset = queryset.filter(transaction__paid_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(transaction__paid_time__date__lte=end_date)
            
        search = request.data.get('search')
        if search:
            queryset = queryset.filter(
                Q(product_sku__product__name__icontains=search) |
                Q(product_sku__sku__icontains=search) |
                Q(transaction__code__icontains=search)
            )
            
        categories = request.data.get('categories')
        if categories:
            if isinstance(categories, str):
                category_list = [c.strip() for c in categories.split(',')]
                queryset = queryset.filter(product_sku__product__category__id__in=category_list)
            elif isinstance(categories, list):
                queryset = queryset.filter(product_sku__product__category__id__in=categories)

        aggregated_data = queryset.values(
            sku=F('product_sku__sku'),
            product_name=F('product_sku__product__name'),
            category=F('product_sku__product__category__name')
        ).annotate(
            total_amount=Sum('amount'),
            total_sales=Sum(F('amount') * F('unit_price'))
        ).order_by('product_name')

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="supplier_products_export.xlsx"'

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Supplier Products"
        
        # Styles
        title_font = Font(bold=True, size=14)
        header_font = Font(bold=True)
        bold_font = Font(bold=True)
        center_alignment = Alignment(horizontal='center')
        border = Border(left=Side(style='thin'),
                        right=Side(style='thin'),
                        top=Side(style='thin'),
                        bottom=Side(style='thin'))

        # Title
        ws.merge_cells('A1:F1')
        ws['A1'] = "SALES REPORT"
        ws['A1'].font = title_font
        ws['A1'].alignment = center_alignment

        ws.merge_cells('A2:F2')
        ws['A2'] = supplier.name.upper()
        ws['A2'].font = title_font
        ws['A2'].alignment = center_alignment

        # Metadata
        ws['E4'] = "Start Date :"
        ws['E4'].font = bold_font
        ws['F4'] = start_date if start_date else "-"
        
        ws['E5'] = "End Date :"
        ws['E5'].font = bold_font
        ws['F5'] = end_date if end_date else "-"
        
        ws['E6'] = "Supplier ID :"
        ws['E6'].font = bold_font
        ws['F6'] = supplier.code

        # Headers
        headers = ['No', 'SKU', 'Product Name', 'Category', 'Total Amount', 'Total Sales']
        for col_num, header_title in enumerate(headers, 1):
            cell = ws.cell(row=8, column=col_num, value=header_title)
            cell.font = header_font
            cell.border = border
            if header_title == 'No':
                 cell.alignment = center_alignment

        # Data
        row_num = 9
        total_amount_sum = 0
        total_sales_sum = 0
        
        for idx, item in enumerate(aggregated_data, 1):
            ws.cell(row=row_num, column=1, value=idx).border = border
            ws.cell(row=row_num, column=2, value=item['sku']).border = border
            ws.cell(row=row_num, column=3, value=item['product_name']).border = border
            ws.cell(row=row_num, column=4, value=item['category']).border = border
            ws.cell(row=row_num, column=5, value=item['total_amount']).border = border
            ws.cell(row=row_num, column=6, value=item['total_sales']).border = border
            
            total_amount_sum += item['total_amount']
            total_sales_sum += item['total_sales']
            row_num += 1

        # Total Row
        ws.merge_cells(f'C{row_num}:D{row_num}')
        
        total_cell = ws.cell(row=row_num, column=3, value="TOTAL")
        total_cell.font = bold_font
        total_cell.alignment = center_alignment
        
        # Border for total row (empty cells too?)
        # Let's border all cells in the total row
        for col in range(1, 7):
             ws.cell(row=row_num, column=col).border = border

        # Set values
        amount_cell = ws.cell(row=row_num, column=5, value=total_amount_sum)
        amount_cell.font = bold_font
        amount_cell.border = border
        
        sales_cell = ws.cell(row=row_num, column=6, value=total_sales_sum)
        sales_cell.font = bold_font
        sales_cell.border = border

        # Adjust column widths (approximate)
        ws.column_dimensions['A'].width = 5
        ws.column_dimensions['B'].width = 15
        ws.column_dimensions['C'].width = 30
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 15

        wb.save(response)
        return response

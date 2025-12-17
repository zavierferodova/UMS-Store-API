from products.views.sku import ProductSKUViewSet


class CatalogueViewSet(ProductSKUViewSet):
    """
    View for listing product SKUs in the catalogue.
    Filters out SKUs with 0 stock.
    """
    def get_queryset(self):
        return super().get_queryset().filter(stock__gt=0).order_by('product__name')

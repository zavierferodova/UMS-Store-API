from rest_framework.pagination import PageNumberPagination
from .utils import api_response

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data, message: str = "Data retrieved successfully"):
        return api_response(
            status=200,
            success=True,
            message=message,
            data=data,
            meta={
                'total': self.page.paginator.count,
                'page': self.page.number,
                'limit': self.get_page_size(self.request),
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            }
        )

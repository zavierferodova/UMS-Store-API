from rest_framework.response import Response

class CustomPaginationMixin:
    def get_paginated_response(self, data, message: str):
        """
        Return a paginated serializer response with a custom message.
        """
        assert self.paginator is not None
        # Call the paginator's get_paginated_response with the message
        return self.paginator.get_paginated_response(data, message=message)

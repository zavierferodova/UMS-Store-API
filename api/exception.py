from rest_framework.views import exception_handler
from api.utils import api_response

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response = api_response(
            status=response.status_code,
            success=False,
            message="An error occurred",
            error=response.data
        )

    return response

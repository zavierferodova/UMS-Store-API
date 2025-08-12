from rest_framework.views import exception_handler
from api.utils import api_response
from api.serializers import ErrorResponseSerializer

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_data = []
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    for item in value:
                        error_data.append({"message": f"{key}: {item}"})
                else:
                    error_data.append({"message": f"{key}: {value}"})
        else:
            for message in response.data:
                error_data.append({"message": message})

        serializer = ErrorResponseSerializer(data=error_data, many=True)
        serializer.is_valid(raise_exception=True)

        response = api_response(
            status=response.status_code,
            success=False,
            message="An error occurred",
            error=serializer.data
        )

    return response
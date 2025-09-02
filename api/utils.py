from rest_framework.response import Response
from .serializers import HttpResponseBodySerializer, HttpErrorBodySerializer

def api_response(
    status: int,
    success: bool,
    message: str,
    data: dict | list | None = None,
    error: any = None,
    meta: dict | None = None
):
    response = {
        'success': success,
        'message': message,
        'data': data
    }

    if error:
        errors = []
        if isinstance(error, dict):
            for field, value in error.items():
                if isinstance(value, list):
                    errors.extend([f"{field}: {v}" for v in value])
                else:
                    errors.append(f"{field}: {value}")
        elif isinstance(error, list):
            errors.extend(error)
        else:
            errors.append(str(error))

        error_data = [{"message": str(error)} for error in errors]

        serializer = HttpErrorBodySerializer(data=error_data, many=True)
        serializer.is_valid(raise_exception=True)
        response['error'] = serializer.data

    if meta:
        response['meta'] = meta

    serialzer =  HttpResponseBodySerializer(response)
    return Response(serialzer.data, status=status)
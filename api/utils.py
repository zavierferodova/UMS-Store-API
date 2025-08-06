from rest_framework.response import Response
from .serializers import HttpResponseBodySerializer

def api_response(
    success: bool,
    message: str,
    data: dict | list | None = None,
    errors: list | None = None,
    meta: dict | None = None):

    response = {
        'success': success,
        'message': message,
        'data': data
    }

    if errors:
        response['errors'] = errors

    if meta:
        response['meta'] = meta

    serialzer =  HttpResponseBodySerializer(response)
    return Response(serialzer.data)
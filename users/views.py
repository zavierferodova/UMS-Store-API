from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from api.utils import api_response
from api.pagination import CustomPagination
from django.db.models import Q
from rest_framework.generics import ListAPIView

class UserListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(username__icontains=search) |
                Q(name__icontains=search)
            )
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(
            status=200,
            success=True,
            message='Users retrieved successfully.',
            data=serializer.data
        )

user_list = UserListView.as_view()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request, pk):
    """
    Retrieve a single user by ID or username.
    """
    try:
        if pk.isdigit():
            user = User.objects.get(pk=pk)
        else:
            user = User.objects.get(Q(email__iexact=pk) | Q(username__iexact=pk))
        serializer = UserSerializer(user)
        return api_response(
            status=200,
            success=True,
            message='User retrieved successfully.',
            data=serializer.data
        )
    except User.DoesNotExist:
        return api_response(
            status=404,
            success=False,
            message=f'User with id or username {pk} not found.',
            error=[{'message': f'User with id or username {pk} not found.'}]
        )

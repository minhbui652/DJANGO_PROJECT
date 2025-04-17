from django.contrib.auth.models import Permission
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import permission_required
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.response import Response
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user.models import User

@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    openapi.Parameter('page_number', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.view_permission'], raise_exception=True)
def view_permissions(request):
    try:
        permissions = Permission.objects.all()
        page_size = int(request.query_params.get('page_size', 10))
        page_number = int(request.query_params.get('page_number', 1))
        paginator = Paginator(permissions, page_size)
        permission_page = paginator.get_page(page_number) if paginator.num_pages >= page_number else []
        result = {
            'page': page_number,
            'page_size': page_size,
            'result': [
                {
                    'id': permission.id,
                    'name': permission.name,
                    'codename': permission.codename,
                    'content_type': permission.content_type.all_label,
                } for permission in permission_page
            ],
        }
        return Response(result, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.view_permission'], raise_exception=True)
def view_permissions_by_id(request, id):
    try:
        user = User.objects.prefetch_related('user_permissions').get(id=id)
        permissions = user.user_permissions.all()
        if not permissions:
            return Response([], status=200)
        result = [
            {
                'id': permission.id,
                'name': permission.name,
                'codename': permission.codename,
            } for permission in permissions
        ]
        return Response(result, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
from django.contrib.auth.models import Permission, Group
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.decorators import permission_required
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.response import Response
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from user.models import User
from user.serializers import AddPermissionDto, DeletePermissionDto, AddGroupDto, UpdateGroupDto


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

@swagger_auto_schema(methods=['post', 'put'], request_body=AddPermissionDto)
@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.add_permission'], raise_exception=True)
def add_permission(request):    #đăng ký quyền cho user
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.data['id'])

            for permission_id in request.data['permission_ids']:
                permission = Permission.objects.get(id=permission_id)
                if permission in request.user.user_permissions.all():
                    pass
                else:
                    user.user_permissions.add(permission)
            user.save()
        return Response({'message': 'Permission added successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@swagger_auto_schema(method='delete', request_body=DeletePermissionDto)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.delete_permission'], raise_exception=True)
def delete_permission(request):
    try:
        with transaction.atomic():
            user = User.objects.get(id=request.data['id'])
            for permission_id in request.data['permission_ids']:
                permission = Permission.objects.get(id=permission_id)
                if permission in user.user_permissions.all():
                    user.user_permissions.remove(permission)
            user.save()
        return Response({'message': 'Permission deleted successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    openapi.Parameter('page_number', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
])
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.view_group'], raise_exception=True)
def view_group(request):
    try:
        group = Group.objects.prefetch_related('permissions').all()
        page_size = int(request.query_params.get('page_size', 10))
        page_number = int(request.query_params.get('page_number', 1))
        paginator = Paginator(group, page_size)
        group_page = paginator.get_page(page_number) if paginator.num_pages >= page_number else []
        result = {
            'page': page_number,
            'page_size': page_size,
            'result': [
                {
                    'id': group.id,
                    'name': group.name,
                    'permissions': [
                        {
                            'id': permission.id,
                            'name': permission.name,
                            'codename': permission.codename,
                        } for permission in group.permissions.all()
                    ],
                } for group in group_page
            ],
        }
        return Response(result, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.view_group'], raise_exception=True)
def view_group_by_user_id(request, id):
    try:
        user = User.objects.get(id=id)
        groups = user.groups.all()
        return Response(
            [
                {
                    'id': group.id,
                    'name': group.name,
                    'permissions': [
                        {
                            'id': permission.id,
                            'name': permission.name,
                            'codename': permission.codename,
                        } for permission in group.permissions.all()
                    ],
                } for group in groups
            ],
            status=200
        )
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@swagger_auto_schema(method='post', request_body=AddGroupDto)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.add_group'], raise_exception=True)
def add_group(request):
    try:
        with transaction.atomic():
            group = Group.objects.create(name=request.data['name'])
            for permission_id in request.data['permission_ids']:
                permission = Permission.objects.get(id=permission_id)
                group.permissions.add(permission)
            group.save()
        return Response({'message': 'Group created successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@swagger_auto_schema(method='put', request_body=UpdateGroupDto)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.change_group'], raise_exception=True)
def update_group(request):
    try:
        with transaction.atomic():
            group = Group.objects.get(id=request.data['id'])
            group.name = request.data['name']
            group.permissions.clear()
            for permission_id in request.data['permission_ids']:
                permission = Permission.objects.get(id=permission_id)
                group.permissions.add(permission)
            group.save()
        return Response({'message': 'Group updated successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@permission_required(['auth.delete_group'], raise_exception=True)
def delete_group(request, id):
    try:
        group = Group.objects.get(id=id)
        group.delete()
        return Response({'message': 'Group deleted successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


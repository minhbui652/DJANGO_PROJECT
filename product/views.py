from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Product, Cart
from user.models import User
from .serializer import ProductSerializer, CartSerializer, ProductCreateDto, ProductUpdateDto
from rest_framework.response import Response
from django.core.paginator import Paginator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
@swagger_auto_schema(method='post', request_body=ProductCreateDto)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_create(request):
    if int(request.data['stock']) < 0:
        return Response({'error': 'Stock cannot be negative'}, status=400)
    if float(request.data['price']) <= 0:
        return Response({'error': 'Price cannot be negative'}, status=400)
    # serialize = ProductSerializer(data=request.data, context=({'request': request}))
    serialize = ProductCreateDto(data=request.data, context=({'request': request}))
    if serialize.is_valid():
        serialize.save()
        return Response(serialize.data, status=201)
    return Response(serialize.errors, status=400)

@swagger_auto_schema(method='put', request_body=ProductUpdateDto)
@api_view(['PUT'])
def product_update(request):
    product = Product.objects.filter(id=request.data['id']).first()
    if product is None:
        return Response({'error': 'Product does not exist'}, status=400)
    if int(request.data['stock']) < 0:
        return Response({'error': 'Stock cannot be negative'}, status=400)
    if float(request.data['price']) <= 0:
        return Response({'error': 'Price cannot be negative'}, status=400)
    serialize = ProductUpdateDto(product, data=request.data, context=({'request': request}))
    if serialize.is_valid():
        serialize.save()
        return Response(serialize.data, status=200)
    return Response(serialize.errors, status=400)

@api_view(['DELETE'])
def product_delete(request, id):
    product = Product.objects.filter(id=id).first()
    if product is None:
        return Response({'error': 'Product does not exist'}, status=400)
    product.delete()
    return Response({'message': 'Product deleted successfully'}, status=200)

@api_view(['GET'])
def product_get_by_id(request, id):
    product = Product.objects.filter(id=id).first()
    if product is None:
        return Response({'error': 'Product does not exist'}, status=400)
    serialize = ProductSerializer(product)
    return Response(serialize.data, status=200)

@swagger_auto_schema(method='get', manual_parameters=[
    openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
    openapi.Parameter('page_number', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER)
])
@api_view(['GET'])
def product_get_all(request):
    products = Product.objects.all()
    page_size = request.GET.get('page_size', 1)
    page_number = request.GET.get('page_number', 10)
    paginator = Paginator(products, page_size)
    result = paginator.get_page(page_number)
    serialize = ProductSerializer(result, many=True, context=({'request': request}))
    response = {
        'page': page_number,
        'page_size': page_size,
        'result': serialize.data,
    }
    return Response(response, status=200)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        if int(request.data['stock']) < 0:
            return Response({'error': 'Stock cannot be negative'}, status=400)
        if float(request.data['price']) <= 0:
            return Response({'error': 'Price cannot be negative'}, status=400)
        serialize = ProductSerializer(data=request.data, context={'request': request})
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=201)
        return Response(serialize.errors, status=400)

    def update(self, request, pk):
        if int(request.data['stock']) < 0:
            return Response({'error': 'Stock cannot be negative'}, status=400)
        if float(request.data['price']) <= 0:
            return Response({'error': 'Price cannot be negative'}, status=400)

        product = Product.objects.filter(id=pk).first()
        if product is None:
            return Response({'error': 'Product does not exist'}, status=400)
        serialize = ProductSerializer(product, data=request.data, partial=True)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=200)
        return Response(serialize.errors, status=400)

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        if not User.objects.filter(id=request.data['user']):
            return Response({'error': 'User does not exist'}, status=400)
        if not Product.objects.filter(id=request.data['product']):
            return Response({'error': 'Product does not exist'}, status=400)
        if int(request.data['quantity']) <= 0:
            return Response ({'error': 'Quantity cannot be negative'}, status=400)
        elif int(request.data['quantity']) > Product.objects.get(id=request.data['product']).stock:
            return Response({'error': 'Quantity cannot be greater than stock'}, status=400)

        serialize = CartSerializer(data=request.data, context={'request': request})
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=201)
        return Response(serialize.errors, status=400)

    def update(self, request, *args, **kwargs):
        if not Cart.objects.fiter(id=request.data['id']).exists():
            return Response({'error': 'Cart does not exist'}, status=400)
        if not User.objects.filter(id=request.data['user']):
            return Response({'error': 'User does not exist'}, status=400)
        if not Product.objects.filter(id=request.data['product']):
            return Response({'error': 'Product does not exist'}, status=400)
        if int(request.data['quantity']) <= 0:
            return Response({'error': 'Quantity cannot be negative'}, status=400)
        elif int(request.data['quantity']) > Product.objects.get(id=request.data['product']).stock:
            return Response({'error': 'Quantity cannot be greater than stock'}, status=400)

        serialize = CartSerializer(data=request.data, context={'request': request})
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=201)
        return Response(serialize.errors, status=400)

@api_view(['GET'])
def get_total_price(request, id):
    if not User.objects.filter(id=id).exists():
        return Response({'error': 'User does not exist'}, status=400)

    total_amount = 0
    cart = Cart.objects.filter(user=id)
    for item in cart:
        total_amount += item.product.price * item.quantity
    return Response({'user': id, 'total_amount': total_amount}, status=200)

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view

from .models import Product, Cart
from user.models import User
from .serializer import ProductSerializer, CartSerializer
from rest_framework.response import Response

# Create your views here.
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

from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):

    serializer_class   = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)

    def retrieve(self, request, *args, **kwargs):
        return Response(self.get_serializer(self.get_object()).data)


    @action(detail=False, methods=['post'], url_path='add-item')
    def add_item(self, request):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product  = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity},
            )
            if not created:
                new_qty = item.quantity + quantity
                if product.stock < new_qty:
                    return Response(
                        {'detail': f'Only {product.stock} units of {product.name} available.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                item.quantity = new_qty
                item.save()

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


    @action(detail=False, methods=['post'], url_path=r'update-item/(?P<item_id>\d+)')
    def update_item(self, request, item_id=None):
        cart = self.get_object()

        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'detail': 'quantity is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({'detail': 'quantity must be an integer.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({'detail': 'Quantity must be at least 1.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if item.product.stock < quantity:
            return Response(
                {'detail': f'Only {item.product.stock} units of {item.product.name} available.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item.quantity = quantity
        item.save(update_fields=['quantity'])
        return Response(CartSerializer(cart).data)


    @action(detail=False, methods=['delete'], url_path=r'remove-item/(?P<item_id>\d+)')
    def remove_item(self, request, item_id=None):
        cart = self.get_object()
        deleted, _ = cart.items.filter(id=item_id).delete()
        if not deleted:
            return Response({'detail': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(CartSerializer(cart).data)


    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)
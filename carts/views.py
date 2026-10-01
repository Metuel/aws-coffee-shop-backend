from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from .services import get_cart


def cart_response(cart, request, code=status.HTTP_200_OK):
    """Return the full cart, freshly loaded with related items."""
    cart = Cart.objects.prefetch_related("items__product").get(pk=cart.pk)
    return Response(
        CartSerializer(cart, context={"request": request}).data,
        status=code,
    )


class CartView(APIView):
    """
    GET    /api/cart/ --- the current user's cart
    DELETE /api/cart/ --- empty the cart
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return cart_response(get_cart(request.user), request)

    def delete(self, request):
        cart = get_cart(request.user)
        cart.items.all().delete()
        return cart_response(cart, request)


class CartItemViewSet(viewsets.GenericViewSet):
    """
    POST   /api/cart/items/ to add or increase an item
    PATCH  /api/cart/items/<id>/ to set quantity
    DELETE /api/cart/items/<id>/ to remove item
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "patch", "delete", "options"]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related("product")

    def create(self, request):
        cart = get_cart(request.user)

        serializer = AddToCartSerializer(
            data=request.data,
            context={"cart": cart},
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            item, _ = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": 0},
            )
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return cart_response(cart, request, status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        item = self.get_object()

        serializer = UpdateCartItemSerializer(
            data=request.data,
            context={"item": item},
        )
        serializer.is_valid(raise_exception=True)

        item.quantity = serializer.validated_data["quantity"]
        item.save(update_fields=["quantity"])

        return cart_response(item.cart, request)

    def destroy(self, request, pk=None):
        item = self.get_object()
        cart = item.cart
        item.delete()
        return cart_response(cart, request)


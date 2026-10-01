from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Order
from .serializers import (
    AddToCartSerializer, CartSerializer, CheckoutSerializer,
    OrderSerializer, UpdateCartItemSerializer,
)
from .services import cancel_order, create_order_from_cart, get_cart


def cart_response(cart, request, code=status.HTTP_200_OK):
    cart = Cart.objects.prefetch_related("items__product").get(pk=cart.pk)
    return Response(CartSerializer(cart, context={"request": request}).data, status=code)


class CartView(APIView):
    """GET the current user's cart, DELETE to empty it."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return cart_response(get_cart(request.user), request)

    def delete(self, request):
        cart = get_cart(request.user)
        cart.items.all().delete()
        return cart_response(cart, request)


class CartItemViewSet(viewsets.GenericViewSet):
    """
    POST   /cart/items/        {product_id, quantity}  -> add (or increase) an item
    PATCH  /cart/items/<id>/   {quantity}              -> set quantity
    DELETE /cart/items/<id>/                           -> remove item
    Each call returns the whole updated cart.
    """
    permission_classes = [IsAuthenticated]
    http_method_names = ["post", "patch", "delete", "options"]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related("product")

    def create(self, request):
        cart = get_cart(request.user)
        serializer = AddToCartSerializer(data=request.data, context={"cart": cart})
        serializer.is_valid(raise_exception=True)
        item, _ = CartItem.objects.get_or_create(
            cart=cart, product=serializer.validated_data["product"], defaults={"quantity": 0}
        )
        item.quantity += serializer.validated_data["quantity"]
        item.save(update_fields=["quantity"])
        return cart_response(cart, request, status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        item = self.get_object()
        serializer = UpdateCartItemSerializer(data=request.data, context={"item": item})
        serializer.is_valid(raise_exception=True)
        item.quantity = serializer.validated_data["quantity"]
        item.save(update_fields=["quantity"])
        return cart_response(item.cart, request)

    def destroy(self, request, pk=None):
        item = self.get_object()
        cart = item.cart
        item.delete()
        return cart_response(cart, request)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    GET  /orders/              your order history
    GET  /orders/<id>/         one order
    POST /orders/              place an order from your cart {delivery_address?, notes?}
    POST /orders/<id>/cancel/  cancel while still pending
    Status changes beyond cancelling are done by staff in the admin.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")

    def create(self, request):
        data = CheckoutSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        order = create_order_from_cart(request.user, **data.validated_data)
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = cancel_order(self.get_object())
        return Response(self.get_serializer(order).data)

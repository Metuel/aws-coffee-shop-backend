from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    AddToCartSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


def get_cart(request):
    """Find the guest cart from the X-Cart-Token header, or start a new one."""
    raw = request.headers.get("X-Cart-Token", "").strip()
    if raw:
        try:
            return Cart.objects.get(token=raw)
        except (Cart.DoesNotExist, DjangoValidationError, ValueError):
            pass  # unknown / malformed token -> fall through to a fresh cart
    return Cart.objects.create()


class CartView(APIView):
    """GET /api/cart/  -> the cart (includes `token` so the browser can save it)."""

    # No login needed. authentication_classes=[] also stops an old/expired
    # login token in the browser from causing a 401 here.
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        cart = get_cart(request)
        return Response(CartSerializer(cart).data)


class CartItemViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = CartItemSerializer

    def get_queryset(self):
        # Only ever this visitor's items, so nobody can touch another cart
        return CartItem.objects.filter(cart=get_cart(self.request)).select_related(
            "product"
        )

    def list(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    def create(self, request):
        cart = get_cart(request)
        serializer = AddToCartSerializer(data=request.data, context={"cart": cart})
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={"quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def partial_update(self, request, pk=None):
        item = self.get_object()
        serializer = UpdateCartItemSerializer(
            data=request.data, context={"item": item}
        )
        serializer.is_valid(raise_exception=True)
        item.quantity = serializer.validated_data["quantity"]
        item.save(update_fields=["quantity"])
        return Response(CartItemSerializer(item).data)

    def destroy(self, request, pk=None):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)







# from django.db import transaction
# from rest_framework import status, viewsets, permissions
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView

# from .models import Cart, CartItem
# from .serializers import (
#     AddToCartSerializer,
#     CartSerializer,
#     UpdateCartItemSerializer,
# )
# from .services import get_cart


# def cart_response(cart, request, code=status.HTTP_200_OK):
#     """Return the full cart, freshly loaded with related items."""
#     cart = Cart.objects.prefetch_related("items__product").get(pk=cart.pk)
#     return Response(
#         CartSerializer(cart, context={"request": request}).data,
#         status=code,
#     )


# class CartView(APIView):
#     """
#     GET    /api/cart/ --- the current user's cart
#     DELETE /api/cart/ --- empty the cart
#     """
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         return cart_response(get_cart(request.user), request)

#     def delete(self, request):
#         cart = get_cart(request.user)
#         cart.items.all().delete()
#         return cart_response(cart, request)


# class CartItemViewSet(viewsets.GenericViewSet):
#     """
#     POST   /api/cart/items/ to add or increase an item
#     PATCH  /api/cart/items/<id>/ to set quantity
#     DELETE /api/cart/items/<id>/ to remove item
#     """
#     permission_classes = [permissions.AllowAny]
#     http_method_names = ["post", "patch", "delete", "options"]

#     def get_queryset(self):
#         return CartItem.objects.filter(
#             cart__user=self.request.user
#         ).select_related("product")

#     def create(self, request):
#         cart = get_cart(request.user)

#         serializer = AddToCartSerializer(
#             data=request.data,
#             context={"cart": cart},
#         )
#         serializer.is_valid(raise_exception=True)

#         product = serializer.validated_data["product"]
#         quantity = serializer.validated_data["quantity"]

#         with transaction.atomic():
#             item, _ = CartItem.objects.select_for_update().get_or_create(
#                 cart=cart,
#                 product=product,
#                 defaults={"quantity": 0},
#             )
#             item.quantity += quantity
#             item.save(update_fields=["quantity"])

#         return cart_response(cart, request, status.HTTP_201_CREATED)

#     def partial_update(self, request, pk=None):
#         item = self.get_object()

#         serializer = UpdateCartItemSerializer(
#             data=request.data,
#             context={"item": item},
#         )
#         serializer.is_valid(raise_exception=True)

#         item.quantity = serializer.validated_data["quantity"]
#         item.save(update_fields=["quantity"])

#         return cart_response(item.cart, request)

#     def destroy(self, request, pk=None):
#         item = self.get_object()
#         cart = item.cart
#         item.delete()
#         return cart_response(cart, request)


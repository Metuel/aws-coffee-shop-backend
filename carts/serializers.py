from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSummarySerializer

from .models import Cart, CartItem


def _check_stock(product, wanted):
    if not product.is_available:
        raise serializers.ValidationError(
            f"'{product.name}' is not available."
        )

    if wanted > product.stock:
        raise serializers.ValidationError(
            f"Only {product.stock} of '{product.name}' left in stock."
        )


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSummarySerializer(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "subtotal",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        many=True,
        read_only=True,
    )
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total",
        ]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_available=True),
        source="product",
    )
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
        default=1,
    )

    def validate(self, attrs):
        cart = self.context["cart"]
        product = attrs["product"]

        existing = (
            CartItem.objects
            .filter(cart=cart, product=product)
            .values_list("quantity", flat=True)
            .first()
            or 0
        )

        _check_stock(
            product,
            existing + attrs["quantity"],
        )

        return attrs


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(
        min_value=1,
        max_value=100,
    )

    def validate_quantity(self, value):
        _check_stock(
            self.context["item"].product,
            value,
        )
        return value


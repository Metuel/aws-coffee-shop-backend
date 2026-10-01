from decimal import Decimal

from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from products.models import Product
from carts.models import Cart
from .models import Order, OrderItem


@transaction.atomic
def create_order_from_cart(user, delivery_address="", notes=""):
    """
    Turn the user's cart into an order, decrement stock and empty the cart.

    Everything runs in one transaction: any failure rolls back completely.
    """
    cart, _ = Cart.objects.get_or_create(user=user)
    items = list(cart.items.all())

    if not items:
        raise ValidationError({"detail": "Your cart is empty."})

    # Lock the product rows so concurrent checkouts cannot oversell.
    products = {
        product.id: product
        for product in Product.objects.select_for_update().filter(
            id__in=[item.product_id for item in items]
        )
    }

    order = Order.objects.create(
        user=user,
        delivery_address=delivery_address,
        notes=notes,
    )

    total = Decimal("0.00")

    for item in items:
        product = products[item.product_id]

        if not product.is_available:
            raise ValidationError({
                "detail": f"'{product.name}' is no longer available."
            })

        if item.quantity > product.stock:
            raise ValidationError({
                "detail": (
                    f"Only {product.stock} of "
                    f"'{product.name}' left in stock."
                )
            })

        product.stock -= item.quantity
        product.save(update_fields=["stock"])

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=item.quantity,
        )

        total += product.price * item.quantity

    order.total = total
    order.save(update_fields=["total"])

    cart.items.all().delete()

    return order


@transaction.atomic
def cancel_order(order):
    order = Order.objects.select_for_update().get(pk=order.pk)

    if order.status != OrderStatus.PENDING:
        raise ValidationError({
            "detail": "Only pending orders can be cancelled."
        })

    for item in order.items.all():
        if item.product_id:
            Product.objects.filter(pk=item.product_id).update(
                stock=F("stock") + item.quantity
            )

    order.status = OrderStatus.CANCELLED
    order.save(update_fields=["status", "updated_at"])

    return order
from .models import Cart


def get_cart(user):
    """Return the user's cart, creating it if it doesn't exist."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

def cart_context(request):
    """
    Global context processor making the total count of cart items
    available across all templates in the navbar and UI.
    """
    cart = request.session.get('cart', {})
    total_items = sum(cart.values()) if isinstance(cart, dict) else 0
    return {
        'cart_count': total_items,
    }

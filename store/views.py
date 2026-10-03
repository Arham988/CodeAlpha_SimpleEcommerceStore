from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Product, Order, OrderItem
from .forms import UserRegistrationForm, UserLoginForm, CheckoutForm

def home(request):
    """
    Product listing homepage view.
    Fetches all Product objects from SQLite and passes them to the template.
    """
    products = Product.objects.all().order_by('-created_at')
    context = {
        'products': products,
    }
    return render(request, 'store/home.html', context)

def product_detail(request, pk):
    """
    Product detail view.
    Retrieves a single Product object by primary key (pk) or raises HTTP 404.
    """
    product = get_object_or_404(Product, pk=pk)
    context = {
        'product': product,
    }
    return render(request, 'store/product_detail.html', context)

def cart_detail(request):
    """
    Shopping cart page view.
    Retrieves product IDs and quantities from session, fetches fresh product details
    and prices from SQLite, and computes subtotals and grand total server-side.
    """
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')

    # Fetch products present in cart from database
    if cart:
        product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
        products = Product.objects.filter(id__in=product_ids)

        for product in products:
            str_id = str(product.id)
            qty = cart.get(str_id, 0)

            # Cap quantity if it exceeds current inventory stock
            if qty > product.stock:
                qty = product.stock
                cart[str_id] = qty

            if qty > 0:
                subtotal = product.price * qty
                total += subtotal
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'subtotal': subtotal,
                })
            else:
                if str_id in cart:
                    del cart[str_id]

        request.session['cart'] = cart
        request.session.modified = True

    context = {
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/cart.html', context)

def cart_add(request, product_id):
    """
    Adds a product to the session cart or increments its quantity.
    """
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        messages.warning(request, f"Sorry, {product.name} is currently out of stock.")
        return redirect('store:cart_detail')

    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    cart = request.session.get('cart', {})
    str_id = str(product_id)
    current_qty = cart.get(str_id, 0)
    new_qty = current_qty + quantity

    if new_qty > product.stock:
        new_qty = product.stock
        messages.warning(request, f"Quantity adjusted to {product.stock} (maximum available stock).")
    else:
        messages.success(request, f"Added {product.name} to your cart.")

    cart[str_id] = new_qty
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('store:cart_detail')

def cart_update(request, product_id):
    """
    Increases or decreases quantity for an existing cart item via POST.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = request.session.get('cart', {})
        str_id = str(product_id)

        if str_id in cart:
            action = request.POST.get('action')
            if action == 'increase':
                if cart[str_id] < product.stock:
                    cart[str_id] += 1
                    messages.success(request, f"Increased quantity for {product.name}.")
                else:
                    messages.warning(request, f"Cannot add more. Only {product.stock} items in stock.")
            elif action == 'decrease':
                if cart[str_id] > 1:
                    cart[str_id] -= 1
                    messages.success(request, f"Decreased quantity for {product.name}.")
                else:
                    del cart[str_id]
                    messages.info(request, f"Removed {product.name} from your cart.")

            request.session['cart'] = cart
            request.session.modified = True

    return redirect('store:cart_detail')

def cart_remove(request, product_id):
    """
    Removes a product completely from the session cart.
    """
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    str_id = str(product_id)

    if str_id in cart:
        del cart[str_id]
        request.session['cart'] = cart
        request.session.modified = True
        messages.info(request, f"Removed {product.name} from your cart.")

    return redirect('store:cart_detail')

# ==============================================================================
# Authentication Views
# ==============================================================================

def user_register(request):
    """
    User registration view.
    Validates user credentials, creates a new User with hashed password,
    logs the user in automatically, and preserves active cart session data.
    """
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Preserve existing cart across session regeneration
            cart = request.session.get('cart', {})

            # Create user safely (hashes password with PBKDF2)
            user = User.objects.create_user(username=username, email=email, password=password)

            # Log the new user in
            login(request, user)

            # Restore cart
            request.session['cart'] = cart
            request.session.modified = True

            messages.success(request, f"Welcome to ShopAlpha, {user.username}! Your account has been created.")
            return redirect('store:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'store/register.html', {'form': form})

def user_login(request):
    """
    User login view.
    Authenticates username and password against database, starts user session,
    and preserves cart session data.
    """
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Preserve existing cart across session rotation
                cart = request.session.get('cart', {})

                login(request, user)

                # Restore cart
                request.session['cart'] = cart
                request.session.modified = True

                messages.success(request, f"Welcome back, {user.username}!")

                next_url = request.GET.get('next')
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('store:home')
            else:
                messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'store/login.html', {'form': form})

def user_logout(request):
    """
    User logout view.
    Terminates user authentication session, retains guest shopping cart,
    and redirects to the homepage with a friendly notification.
    """
    cart = request.session.get('cart', {})

    logout(request)

    request.session['cart'] = cart
    request.session.modified = True

    messages.info(request, "You have been logged out.")
    return redirect('store:home')

# ==============================================================================
# Checkout and Order Processing Views
# ==============================================================================

@login_required(login_url='store:login')
def checkout(request):
    """
    Checkout view.
    Ensures user is authenticated and cart is not empty.
    Validates customer shipping info, verifies live inventory stock, calculates total
    with database prices, and atomics creates Order + OrderItems, then decrements stock.
    """
    cart = request.session.get('cart', {})
    if not cart or not any(qty > 0 for qty in cart.values()):
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('store:cart_detail')

    product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
    products = Product.objects.filter(id__in=product_ids)

    # Calculate current review items and total
    cart_items = []
    total = Decimal('0.00')
    for product in products:
        qty = cart.get(str(product.id), 0)
        if qty > 0:
            subtotal = product.price * qty
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': qty,
                'subtotal': subtotal,
            })

    if not cart_items:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('store:cart_detail')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Acquire row-level locks on ordered products to prevent race conditions
                    locked_products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}

                    # Verify that inventory is sufficient for all items
                    for product in products:
                        locked_p = locked_products.get(product.id)
                        qty = cart.get(str(product.id), 0)

                        if not locked_p or locked_p.stock < qty:
                            available = locked_p.stock if locked_p else 0
                            messages.error(
                                request,
                                f"Insufficient stock for '{product.name}'. Only {available} available, but {qty} requested."
                            )
                            # Roll back transaction automatically and send user back to cart
                            return redirect('store:cart_detail')

                    # Recompute final order total from locked database prices
                    order_total = Decimal('0.00')
                    for product in products:
                        locked_p = locked_products[product.id]
                        qty = cart[str(product.id)]
                        order_total += locked_p.price * qty

                    # Create the main Order
                    order = Order.objects.create(
                        user=request.user,
                        full_name=form.cleaned_data['full_name'],
                        email=form.cleaned_data['email'],
                        phone=form.cleaned_data['phone'],
                        address=form.cleaned_data['address'],
                        total_amount=order_total,
                        status='Pending'
                    )

                    # Create OrderItem records and decrement stock
                    for product in products:
                        locked_p = locked_products[product.id]
                        qty = cart[str(product.id)]

                        OrderItem.objects.create(
                            order=order,
                            product=locked_p,
                            quantity=qty,
                            price=locked_p.price  # Historic snapshot price
                        )

                        # Decrement available stock
                        locked_p.stock -= qty
                        locked_p.save()

                    # Clear the shopping cart session
                    request.session['cart'] = {}
                    request.session.modified = True

                    messages.success(request, f"Order #{order.id} placed successfully!")
                    return redirect('store:order_success', order_id=order.id)

            except Exception as e:
                messages.error(request, f"An unexpected error occurred during checkout: {str(e)}")
                return redirect('store:checkout')
    else:
        # Pre-fill contact details from current authenticated user
        initial_data = {
            'email': request.user.email or '',
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
        }
        form = CheckoutForm(initial=initial_data)

    context = {
        'form': form,
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'store/checkout.html', context)

@login_required(login_url='store:login')
def order_success(request, order_id):
    """
    Order confirmation view.
    Security: Strictly filters by user=request.user to ensure customers
    cannot inspect or view other users' order confirmations.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_success.html', {'order': order})

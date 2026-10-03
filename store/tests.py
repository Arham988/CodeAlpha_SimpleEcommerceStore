from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem

class StoreHomepageTests(TestCase):
    def test_home_page_status_code_and_templates(self):
        """Verify that the home page URL resolves, returns 200, and uses correct templates."""
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/home.html')
        self.assertTemplateUsed(response, 'store/base.html')

    def test_home_page_displays_products(self):
        """Verify that products created in the database are rendered dynamically on the homepage."""
        p1 = Product.objects.create(
            name='Alpha Gaming Keyboard',
            description='Mechanical RGB tactile keyboard.',
            price=Decimal('59.99'),
            stock=8
        )
        p2 = Product.objects.create(
            name='Alpha Precision Mouse',
            description='Wireless ergonomic gaming mouse.',
            price=Decimal('29.99'),
            stock=0  # Out of stock
        )

        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)

        # Verify product details appear in rendered HTML
        self.assertContains(response, 'Alpha Gaming Keyboard')
        self.assertContains(response, '$59.99')
        self.assertContains(response, 'In Stock')
        self.assertContains(response, 'Alpha Precision Mouse')
        self.assertContains(response, '$29.99')
        self.assertContains(response, 'Out of Stock')

        # Verify View Details links point to correct product detail URLs
        self.assertContains(response, reverse('store:product_detail', args=[p1.pk]))
        self.assertContains(response, reverse('store:product_detail', args=[p2.pk]))

    def test_empty_catalog_displays_empty_state(self):
        """Verify friendly message when no products exist."""
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No Products Found')

class ProductDetailTests(TestCase):
    def setUp(self):
        self.in_stock_product = Product.objects.create(
            name='Alpha Pro Monitor',
            description='27-inch 4K UHD 144Hz gaming monitor.',
            price=Decimal('299.99'),
            stock=5
        )
        self.out_of_stock_product = Product.objects.create(
            name='Alpha Webcam HD',
            description='1080p autofocus webcam.',
            price=Decimal('49.99'),
            stock=0
        )

    def test_product_detail_status_code_and_template(self):
        """Verify that product detail page loads with 200 OK and uses product_detail.html."""
        response = self.client.get(reverse('store:product_detail', args=[self.in_stock_product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product_detail.html')
        self.assertTemplateUsed(response, 'store/base.html')

    def test_product_detail_content(self):
        """Verify that product fields are properly rendered on the detail page."""
        response = self.client.get(reverse('store:product_detail', args=[self.in_stock_product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha Pro Monitor')
        self.assertContains(response, '$299.99')
        self.assertContains(response, '27-inch 4K UHD 144Hz gaming monitor.')
        self.assertContains(response, 'Available &mdash; 5 in stock')
        self.assertContains(response, 'Back to Products / Continue Shopping')

    def test_out_of_stock_product_detail(self):
        """Verify that out of stock product displays appropriate badges and disabled controls."""
        response = self.client.get(reverse('store:product_detail', args=[self.out_of_stock_product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Out of stock')
        self.assertContains(response, 'Sold Out')

    def test_invalid_product_id_returns_404(self):
        """Verify that accessing a non-existent product ID returns an HTTP 404 response."""
        response = self.client.get(reverse('store:product_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)

class ShoppingCartTests(TestCase):
    def setUp(self):
        self.keyboard = Product.objects.create(
            name='Mechanical Keyboard',
            description='Tactile switches with RGB lighting.',
            price=Decimal('100.00'),
            stock=4
        )
        self.mouse = Product.objects.create(
            name='Gaming Mouse',
            description='High precision optical sensor.',
            price=Decimal('50.00'),
            stock=10
        )
        self.out_of_stock_item = Product.objects.create(
            name='Sold Out Pad',
            description='Desk mousepad.',
            price=Decimal('20.00'),
            stock=0
        )

    def test_empty_cart_display(self):
        """Verify that empty cart page displays friendly message and continue shopping button."""
        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')
        self.assertContains(response, 'Your cart is empty')
        self.assertContains(response, 'Continue Shopping')
        self.assertEqual(response.context['total'], Decimal('0.00'))

    def test_add_to_cart_and_increment(self):
        """Verify adding a product stores it in session and adding again increments quantity."""
        # Add 1 item
        response = self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 1)
        self.assertContains(response, 'Added Mechanical Keyboard to your cart.')

        # Add same product again (should become 2)
        response = self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 1}, follow=True)
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 2)
        self.assertContains(response, 'Mechanical Keyboard')
        self.assertContains(response, '$200.00')

    def test_cannot_add_out_of_stock(self):
        """Verify that out of stock items cannot be added to cart."""
        response = self.client.post(reverse('store:cart_add', args=[self.out_of_stock_item.id]), {'quantity': 1}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(str(self.out_of_stock_item.id), self.client.session.get('cart', {}))
        self.assertContains(response, 'is currently out of stock')

    def test_stock_limit_enforced_on_add(self):
        """Verify quantity is capped to available inventory."""
        response = self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 10}, follow=True)
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 4)
        self.assertContains(response, 'Quantity adjusted to 4')

    def test_cart_update_increase_and_decrease(self):
        """Verify increasing and decreasing quantity via cart_update view."""
        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 2})

        # Increase quantity
        self.client.post(reverse('store:cart_update', args=[self.keyboard.id]), {'action': 'increase'})
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 3)

        # Decrease quantity
        self.client.post(reverse('store:cart_update', args=[self.keyboard.id]), {'action': 'decrease'})
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 2)

        # Decrease down to 1
        self.client.post(reverse('store:cart_update', args=[self.keyboard.id]), {'action': 'decrease'})
        self.assertEqual(self.client.session['cart'][str(self.keyboard.id)], 1)

        # Decrease again should remove item from cart
        self.client.post(reverse('store:cart_update', args=[self.keyboard.id]), {'action': 'decrease'})
        self.assertNotIn(str(self.keyboard.id), self.client.session.get('cart', {}))

    def test_cart_remove(self):
        """Verify removing a product completely from cart."""
        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 1})
        self.client.post(reverse('store:cart_add', args=[self.mouse.id]), {'quantity': 2})

        response = self.client.post(reverse('store:cart_remove', args=[self.keyboard.id]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(str(self.keyboard.id), self.client.session.get('cart', {}))
        self.assertIn(str(self.mouse.id), self.client.session.get('cart', {}))
        self.assertContains(response, 'Removed Mechanical Keyboard from your cart.')

    def test_server_side_total_and_subtotal(self):
        """Verify subtotals and grand total are accurately computed on server."""
        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 2})
        self.client.post(reverse('store:cart_add', args=[self.mouse.id]), {'quantity': 3})

        response = self.client.get(reverse('store:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], Decimal('350.00'))
        self.assertContains(response, '$350.00')

    def test_cart_count_in_navbar(self):
        """Verify global context processor displays correct cart item count in navbar across pages."""
        response = self.client.get(reverse('store:home'))
        self.assertEqual(response.context['cart_count'], 0)
        self.assertContains(response, '<span class="cart-badge">0</span>')

        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 2})
        self.client.post(reverse('store:cart_add', args=[self.mouse.id]), {'quantity': 1})

        home_res = self.client.get(reverse('store:home'))
        self.assertEqual(home_res.context['cart_count'], 3)
        self.assertContains(home_res, '<span class="cart-badge">3</span>')

        detail_res = self.client.get(reverse('store:product_detail', args=[self.keyboard.pk]))
        self.assertEqual(detail_res.context['cart_count'], 3)
        self.assertContains(detail_res, '<span class="cart-badge">3</span>')

class UserAuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='johndoe',
            email='john@example.com',
            password='secretpassword123'
        )
        self.sample_product = Product.objects.create(
            name='Test Headset',
            description='Test description',
            price=Decimal('49.99'),
            stock=10
        )

    def test_register_new_user_success(self):
        """Verify registering a new user creates record in DB and logs the user in."""
        response = self.client.post(reverse('store:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertContains(response, 'Welcome to ShopAlpha, newuser!')
        self.assertContains(response, 'Welcome, <strong>newuser</strong>')
        self.assertContains(response, 'Logout')

    def test_register_duplicate_username_fails(self):
        """Verify attempting to register with an existing username shows validation error."""
        response = self.client.post(reverse('store:register'), {
            'username': 'johndoe',
            'email': 'different@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This username is already taken.')

    def test_register_mismatched_passwords_fails(self):
        """Verify password confirmation mismatch displays error."""
        response = self.client.post(reverse('store:register'), {
            'username': 'mismatchuser',
            'email': 'mismatch@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword456!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')

    def test_login_success(self):
        """Verify valid login authenticates user and updates navbar."""
        response = self.client.post(reverse('store:login'), {
            'username': 'johndoe',
            'password': 'secretpassword123'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, johndoe!')
        self.assertContains(response, 'Welcome, <strong>johndoe</strong>')
        self.assertContains(response, 'Logout')

    def test_login_invalid_credentials(self):
        """Verify invalid credentials show error banner and keep user logged out."""
        response = self.client.post(reverse('store:login'), {
            'username': 'johndoe',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')

    def test_logout(self):
        """Verify logging out ends session and updates navbar to Login/Register."""
        self.client.login(username='johndoe', password='secretpassword123')
        response = self.client.get(reverse('store:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You have been logged out.')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')

    def test_cart_persists_across_login_and_logout(self):
        """Verify cart items are retained when logging in and logging out."""
        # Add item as guest
        self.client.post(reverse('store:cart_add', args=[self.sample_product.id]), {'quantity': 2})
        self.assertEqual(self.client.session['cart'][str(self.sample_product.id)], 2)

        # Log in
        self.client.post(reverse('store:login'), {
            'username': 'johndoe',
            'password': 'secretpassword123'
        })
        # Cart should still be 2 after login!
        self.assertEqual(self.client.session['cart'][str(self.sample_product.id)], 2)

        # Log out
        self.client.get(reverse('store:logout'))
        # Cart should still be 2 after logout!
        self.assertEqual(self.client.session['cart'][str(self.sample_product.id)], 2)

class ProductModelTests(TestCase):
    def test_create_product(self):
        """Verify that a Product model can be created and saved to the database."""
        product = Product.objects.create(
            name='Alpha Wireless Headphones',
            description='Noise cancelling over-ear headphones with superior audio clarity.',
            price=Decimal('79.99'),
            stock=15
        )
        self.assertEqual(product.name, 'Alpha Wireless Headphones')
        self.assertEqual(product.price, Decimal('79.99'))
        self.assertEqual(product.stock, 15)
        self.assertEqual(str(product), 'Alpha Wireless Headphones ($79.99)')
        self.assertIsNotNone(product.created_at)
        self.assertIsNotNone(product.updated_at)

    def test_admin_login_page_accessible(self):
        """Verify that the Django Admin login page loads successfully."""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django administration')

class CheckoutAndOrderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='Password123!'
        )
        self.other_user = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='Password123!'
        )
        self.keyboard = Product.objects.create(
            name='Alpha Mechanical Keyboard',
            description='Tactile switches',
            price=Decimal('100.00'),
            stock=5
        )
        self.mouse = Product.objects.create(
            name='Alpha Gaming Mouse',
            description='Optical sensor',
            price=Decimal('50.00'),
            stock=10
        )

    def test_unauthenticated_checkout_redirects_to_login(self):
        """Verify that guest users accessing checkout are redirected to login."""
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('store:login')))

    def test_empty_cart_checkout_redirects_to_cart(self):
        """Verify that logged-in users with empty cart are redirected to cart page."""
        self.client.login(username='alice', password='Password123!')
        response = self.client.get(reverse('store:checkout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')
        self.assertContains(response, 'Your cart is empty.')

    def test_complete_checkout_and_order_flow(self):
        """
        Verify complete order workflow:
        1. Login user
        2. Add products to cart
        3. Access checkout page
        4. Place order
        5. Verify Order and OrderItems created
        6. Verify inventory stock reduced
        7. Verify cart cleared
        8. Verify order confirmation page displayed
        """
        self.client.login(username='alice', password='Password123!')

        # Add 2 keyboards ($100 each) and 1 mouse ($50) = $250 total
        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 2})
        self.client.post(reverse('store:cart_add', args=[self.mouse.id]), {'quantity': 1})

        # Check GET checkout page
        checkout_get = self.client.get(reverse('store:checkout'))
        self.assertEqual(checkout_get.status_code, 200)
        self.assertTemplateUsed(checkout_get, 'store/checkout.html')
        self.assertContains(checkout_get, 'Alpha Mechanical Keyboard')
        self.assertContains(checkout_get, '$250.00')

        # Submit Checkout Form
        checkout_post = self.client.post(reverse('store:checkout'), {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '+1 555-0199',
            'address': '742 Evergreen Terrace, Springfield',
        }, follow=True)

        self.assertEqual(checkout_post.status_code, 200)
        self.assertTemplateUsed(checkout_post, 'store/order_success.html')

        # Verify Order in DB
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.full_name, 'Alice Smith')
        self.assertEqual(order.total_amount, Decimal('250.00'))
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.items.count(), 2)

        # Verify OrderItems in DB with snapshot price
        item_kb = order.items.get(product=self.keyboard)
        self.assertEqual(item_kb.quantity, 2)
        self.assertEqual(item_kb.price, Decimal('100.00'))
        self.assertEqual(item_kb.get_subtotal(), Decimal('200.00'))

        item_mouse = order.items.get(product=self.mouse)
        self.assertEqual(item_mouse.quantity, 1)
        self.assertEqual(item_mouse.price, Decimal('50.00'))

        # Verify inventory stock was properly reduced!
        self.keyboard.refresh_from_db()
        self.mouse.refresh_from_db()
        self.assertEqual(self.keyboard.stock, 3)  # 5 - 2 = 3
        self.assertEqual(self.mouse.stock, 9)     # 10 - 1 = 9

        # Verify cart session was cleared
        self.assertEqual(self.client.session.get('cart', {}), {})

        # Verify confirmation receipt content
        self.assertContains(checkout_post, f'Order #{order.id}')
        self.assertContains(checkout_post, 'Alice Smith')
        self.assertContains(checkout_post, '$250.00')
        self.assertContains(checkout_post, '742 Evergreen Terrace')

    def test_stock_exceeded_at_checkout_prevents_order(self):
        """Verify that if stock is depleted before placing order, transaction aborts."""
        self.client.login(username='alice', password='Password123!')
        # Add 3 keyboards to cart
        self.client.post(reverse('store:cart_add', args=[self.keyboard.id]), {'quantity': 3})

        # Another customer buys all remaining stock in the meantime!
        self.keyboard.stock = 1
        self.keyboard.save()

        # Try placing order
        response = self.client.post(reverse('store:checkout'), {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '+1 555-0199',
            'address': '742 Evergreen Terrace',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/cart.html')
        self.assertContains(response, 'Insufficient stock')
        # Ensure no order was created
        self.assertEqual(Order.objects.count(), 0)
        # Ensure stock remained unchanged
        self.keyboard.refresh_from_db()
        self.assertEqual(self.keyboard.stock, 1)

    def test_order_security_user_isolation(self):
        """Verify that a user cannot access another user's order confirmation."""
        # Create order for Alice
        order = Order.objects.create(
            user=self.user,
            full_name='Alice Smith',
            email='alice@example.com',
            phone='1234567890',
            address='Alice Address',
            total_amount=Decimal('100.00'),
            status='Pending'
        )

        # Login as Bob
        self.client.login(username='bob', password='Password123!')

        # Bob attempts to view Alice's order receipt
        response = self.client.get(reverse('store:order_success', args=[order.id]))
        self.assertEqual(response.status_code, 404)


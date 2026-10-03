from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Product(models.Model):
    """
    Represents an item available for purchase in the e-commerce store.
    """
    name = models.CharField(
        max_length=200,
        help_text="Product title or name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed product description"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Price of the product (minimum 0.01)"
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="Product image uploaded to media/products/"
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Quantity currently available in inventory"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the product was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the product was last modified"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} (${self.price})"


class Order(models.Model):
    """
    Represents a customer's placed order.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="The customer who placed the order"
    )
    full_name = models.CharField(
        max_length=150,
        help_text="Customer recipient full name"
    )
    email = models.EmailField(
        help_text="Contact email address"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Contact telephone number"
    )
    address = models.TextField(
        help_text="Shipping and delivery street address"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final grand total amount of the order"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Current fulfillment status"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when order was submitted"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when order was last updated"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} - {self.full_name} (${self.total_amount})"


class OrderItem(models.Model):
    """
    Represents a single product line item inside an Order.
    Stores the historic purchase price at checkout time.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent order this item belongs to"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        help_text="The purchased product"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of this product ordered"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Snapshot unit price at the time of purchase"
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def get_subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product.name} @ ${self.price}"

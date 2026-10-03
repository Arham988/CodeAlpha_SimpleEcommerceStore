from django.contrib import admin
from .models import Product, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administration configuration for the Product model.
    """
    list_display = ('name', 'price', 'stock', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at', 'stock')
    ordering = ('-created_at',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Administration configuration for the Order model.
    """
    list_display = ('id', 'full_name', 'email', 'phone', 'total_amount', 'status', 'created_at')
    search_fields = ('id', 'full_name', 'email', 'phone')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Administration configuration for individual OrderItem line items.
    """
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')

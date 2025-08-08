from django.db import models
import datetime
from django.contrib.auth.models import User



class Watch(models.Model):
    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('kids', 'Kids'),
    ]

    MODEL_CHOICES = [
        ('Aion', 'Aion'),
        ('Arc', 'Arc'),
        ('Asset', 'Asset'),
    ]

    PRICE_RANGE_CHOICES = [
        ('under-10000', 'Under ₹10,000'),
        ('10000-25000', '₹10,000 to ₹25,000'),
        ('25000-50000', '₹25,000 to ₹50,000'),
    ]

    CASE_SIZE_CHOICES = [
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ]

    DIAL_COLOR_CHOICES = [
        ('black', 'Black'),
        ('blue', 'Blue'),
        ('white', 'White'),
    ]

    STRAP_COLOR_CHOICES = [
        ('brown', 'Brown'),
        ('black', 'Black'),
        ('silver', 'Silver'),
    ]

    DIAL_SHAPE_CHOICES = [
        ('round', 'Round'),
        ('square', 'Square'),
        ('rectangular', 'Rectangular'),
    ]

    MOVEMENT_CHOICES = [
        ('quartz', 'Quartz'),
        ('automatic', 'Automatic'),
        ('mechanical', 'Mechanical'),
    ]
    WRIST_SIZE_CHOICES = [
    ('xs', 'Extra Small (5-6 inches)'),
    ('s', 'Small (6-6.5 inches)'),
    ('m', 'Medium (6.5-7 inches)'),
    ('l', 'Large (7-7.5 inches)'),
    ('xl', 'Extra Large (7.5+ inches)'),
    ]

    name = models.CharField(max_length=200)
    model = models.CharField(max_length=20, choices=MODEL_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_range = models.CharField(max_length=20, choices=PRICE_RANGE_CHOICES, blank=True)
    case_size = models.CharField(max_length=20, choices=CASE_SIZE_CHOICES)
    dial_color = models.CharField(max_length=20, choices=DIAL_COLOR_CHOICES)
    strap_color = models.CharField(max_length=20, choices=STRAP_COLOR_CHOICES)
    dial_shape = models.CharField(max_length=20, choices=DIAL_SHAPE_CHOICES)
    movement = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    image = models.ImageField(upload_to='watches/')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='men')
    created_at = models.DateTimeField(default=datetime.datetime.now, blank=True)
    quantity = models.PositiveIntegerField(default=10)
    wrist_size = models.CharField(max_length=20, choices=WRIST_SIZE_CHOICES, blank=True, null=True)
    case_diameter = models.PositiveIntegerField(help_text="Diameter in mm", blank=True, null=True)
    band_width = models.PositiveIntegerField(help_text="Width in mm", blank=True, null=True)
    band_length = models.PositiveIntegerField(help_text="Length in mm", blank=True, null=True)
    adjustable = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class WatchImage(models.Model):
    watch = models.ForeignKey(Watch, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='watch_images/')

    def __str__(self):
        return f"Image for {self.watch.name}"
# models.py
from django.db import models
from django.contrib.auth.models import User

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.watch.name}"
from django.db import models
from django.contrib.auth.models import User

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_buy_now = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart of {self.user.username}"
    
    @property
    def total_price(self):
        return sum(item.watch.price * item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_buy_now = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity}x {self.watch.name} (Cart: {self.cart.id})"
from django.db import models
from django.contrib.auth.models import User

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.address}"
from django.contrib import admin
from .models import Watch, WatchImage, Wishlist, Cart, CartItem
from django.utils.html import format_html

class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'watch', 'created_at')
    search_fields = ('user__username', 'watch__name')
    list_filter = ('created_at',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('created_at',)
    filter_horizontal = ('watches',)  # If using ManyToManyField for watches

admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(Cart, CartAdmin)
class WatchDescription(models.Model):
    watch = models.ForeignKey(Watch, related_name='descriptions', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"{self.watch.name} - {self.title}"
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('razorpay', 'Razorpay'),
        ('cod', 'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(default='No Address Provided')  # or any reasonable default

    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
    max_length=20,
    choices=PAYMENT_METHOD_CHOICES,
    default='cod'
)

    payment_id = models.CharField(max_length=100)
    razorpay_order_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.watch.name} (Order #{self.order.id})"
class Review(models.Model):
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.watch.name}"
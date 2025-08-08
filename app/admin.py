from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Watch, WatchImage, WatchDescription, Wishlist, Cart, CartItem, Order, OrderItem


# ===========================
# ✅ Inline Classes
# ===========================

# Inline class to add multiple images for each watch
class WatchImageInline(admin.TabularInline):
    model = WatchImage
    extra = 4  # Allows adding multiple images at once

# Inline class for multiple descriptions of a watch
class WatchDescriptionInline(admin.TabularInline):
    model = WatchDescription
    extra = 3  # Allows adding multiple descriptions at once

# ===========================
# ✅ WatchAdmin - Includes Images & Descriptions
# ===========================

class WatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'model', 'price','quantity','case_size', 'dial_color', 'strap_color', 'movement','wrist_size', 'case_diameter')
    list_filter = ('model', 'price_range', 'case_size', 'dial_color', 'strap_color', 'dial_shape', 'movement','wrist_size', 'category')
    search_fields = ('name', 'model')
    inlines = [WatchImageInline, WatchDescriptionInline]  # ✅ Includes descriptions
    fieldsets = (
        (None, {
            'fields': ('name', 'model', 'price', 'category','quantity')
        }),
        ('Size Information', {
            'fields': ('wrist_size', 'case_diameter', 'band_width', 'band_length', 'adjustable')
        }),
        # ... rest of your fieldsets
    )


# ===========================
# ✅ Wishlist Inline - Shows Wishlist in User Admin
# ===========================

class WishlistInline(admin.TabularInline):
    model = Wishlist
    extra = 0  # No empty rows
    readonly_fields = ('watch_image_preview', 'watch_details', 'created_at')

    def watch_image_preview(self, obj):
        if obj.watch.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.watch.image.url)
        return "(No Image)"
    
    watch_image_preview.short_description = "Watch Image"

    def watch_details(self, obj):
        return f"{obj.watch.name} | {obj.watch.category} | {obj.watch.dial_color} {obj.watch.dial_shape} Dial | {obj.watch.movement} Watch"
    
    watch_details.short_description = "Product Details"


# ===========================
# ✅ Cart & CartItem Admin
# ===========================

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('watch_image_preview', 'watch_details', 'quantity')

    def watch_image_preview(self, obj):
        if obj.watch.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.watch.image.url)
        return "(No Image)"
    
    watch_image_preview.short_description = "Watch Image"

    def watch_details(self, obj):
        return f"{obj.watch.name} | {obj.watch.category} | {obj.watch.dial_color} {obj.watch.dial_shape} Dial | {obj.watch.movement} Watch"
    
    watch_details.short_description = "Product Details"

class CartInline(admin.StackedInline):
    model = Cart
    can_delete = False
    extra = 0
    # OrderItem Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('watch', 'quantity', 'price')

# Order Admin
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_amount', 'payment_method', 'status')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('user__username', 'payment_id', 'razorpay_order_id')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at') 
    inlines = [CartItemInline]  # Attach CartItems inside Cart


# ===========================
# ✅ Custom UserAdmin - Includes Wishlist & Cart
# ===========================

class CustomUserAdmin(UserAdmin):
    inlines = [WishlistInline, CartInline]  # Attach Wishlist & Cart to UserAdmin


# ===========================
# ✅ Register Models in Django Admin
# ===========================

# Unregister default UserAdmin and register custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ✅ Unregister Cart first to avoid duplicate registration
try:
    admin.site.unregister(Cart)
except admin.sites.NotRegistered:
    pass

# ✅ Register Cart properly
admin.site.register(Cart, CartAdmin)

# ✅ Unregister Watch first if already registered
try:
    admin.site.unregister(Watch)
except admin.sites.NotRegistered:
    pass

# ✅ Register Watch with updated WatchAdmin (Includes Images & Descriptions)
admin.site.register(Watch, WatchAdmin)
admin.site.register(Order, OrderAdmin)

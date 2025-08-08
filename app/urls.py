from django.urls import path
from . import views
from django.urls import path
from .views import order_confirmation
from django.conf.urls.static import static
from django.conf import settings

 # Import views from the same app

app_name = 'app'  # Namespace for reverse lookups

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('detail/', views.detail, name='detail'),  # Fix incorrect mapping
    path('men/', views.men, name='men'),
    path('women/', views.women, name='women'),
    path('kid/', views.kid, name='kid'),
    path('men-loggedin/', views.men_loggedin, name='men_loggedin'),
    path('women-loggedin/', views.women_loggedin, name='women_loggedin'),
    path('kid-loggedin/', views.kid_loggedin, name='kid_loggedin'), 
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('product/<int:watch_id>/', views.product_detail, name='product_detail'),
    path('product_login/<int:watch_id>/', views.product_detail_login, name='product_detail_login'),
    path('wishlist/',views. wishlist, name='wishlist'),
    path('toggle-wishlist/<int:watch_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('add_to_cart/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:cart_item_id>/<str:action>/', views.update_cart, name='update_cart'),  # FIXED
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-summary/', views.order_summary, name='order_summary'),
    path('save-address/', views.save_address, name='save_address'),
    path("order/", views.order_payment, name="order_payment"),
    path("paymenthandler/", views.paymenthandler, name="paymenthandler"),
    path('buy-now/<int:watch_id>/', views.buy_now, name='buy_now'),
    path('update-buy-now/<int:cart_item_id>/<str:action>/', views.update_buy_now, name='update_buy_now'),
    
    path('process-buy-now-payment/', views.process_buy_now_payment, name='process_buy_now_payment'),
    path("order-confirmation/", order_confirmation, name="order_confirmation"),
    path('wrist-size-guide/', views.wrist_size_guide, name='wrist_size_guide'),
    path('measure-wrist/', views.measure_wrist, name='measure_wrist'),
    path('process_cod_order/', views.process_cod_order, name='process_cod_order'),
    path('order-history/', views.order_history, name='order_history'),
    path("submit_review/<int:watch_id>/", views.submit_review, name="submit_review"),

    

    
     

    

    
    
     

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


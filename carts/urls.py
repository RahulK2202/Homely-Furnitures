from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


app_name = 'carts'

urlpatterns = [
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('productdetail/<int:id>/', views.productDetail, name='productdetail'),
    path('addCartItem/<int:product_id>/',views.addCartItem,name='addCartItem'),
    path('removeCartItem/<int:product_id>/',views.removeCartItem,name='removeCartItem'),
    path('removeCartProducts/<int:product_id>/',views.removeCartProduct,name='removeCartProduct'),

    path('addtocart/<int:product_id>/',views.addToCart,name="addtocart"),
    path('wishlist',views.wishlist,name='wishlist'),
    path('add_to_wish/<int:product_id>/',views.addToWish,name='addToWish'),
    path('remove_wish_item/<int:product_id>/',views.removeWishItem,name='removeWishItem'),
]
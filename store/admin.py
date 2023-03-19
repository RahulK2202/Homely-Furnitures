from django.contrib import admin
from .models import Product
from .models import  CartItem
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields = {'slug':('product_name',)}

admin.site.register(Product,ProductAdmin)







class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'quantity', 'created_date', 'is_active')

admin.site.register(CartItem, CartItemAdmin)
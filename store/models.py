from django.db import models
from category.models import Category
from userapp.models import Customer
# Create your models here.


class Product(models.Model):
        product_name    = models.CharField(max_length=200, unique=True)
        slug            = models.SlugField(max_length=200, unique=True)
        description     = models.TextField(max_length=500, blank=True)
        price           = models.IntegerField()
        images          = models.ImageField(upload_to ='photos/products')
        stock           = models.IntegerField()
        is_available    = models.BooleanField(default=True) 
        category        = models.ForeignKey(Category, on_delete=models.CASCADE)
        created_date    = models.DateTimeField(auto_now_add=True)
        modified_date   = models.DateTimeField(auto_now=True)


        def str(self):
            return self.product_name 
        




class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.quantity} x {self.product}"
    
    def sub_total(self):
        return self.product.price * self.quantity

 
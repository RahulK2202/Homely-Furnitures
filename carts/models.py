from django.db import models
from store.models import Product

from userapp.models import Customer

# Create your models here.


class wishlistTable(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
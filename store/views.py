from django.shortcuts import render, get_object_or_404,redirect
from category.models import Category
from .models import Product
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator



def category(request, pid=0):
    if pid == 0:
        products = Product.objects.all()
        categories = Category.objects.all()
    else:
        category = get_object_or_404(Category, id=pid)
        products = Product.objects.filter(category=category)
        categories = Category.objects.all()

    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "shop/categories.html", {'categories': categories, 'products': products, 'page_obj': page_obj})




def search(request):
    keyword = request.GET.get('keyword')
    products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'categories': Category.objects.all(),
        'products': products,
        'keyword' : keyword,
        'page_obj': page_obj
    }
    return render(request, 'shop/categories.html', context)









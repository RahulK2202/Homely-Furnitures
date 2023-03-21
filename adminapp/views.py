from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models.functions import ExtractDay
from django.db.models import Count, Sum
from django.utils.text import slugify
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from store.models import Category, Product, CartItem
from userapp.models import Customer
from order.models import Order, Payment, Coupon,OrderProduct,UserCoupon
from .forms import CouponForm
from datetime import timedelta
from django.db.models import Q


def calculateNumberOfOrdersByPaymentMethod():
    payments = Payment.objects.all()
    payment_count = {}
    total_payments = len(payments)

    # Count the number of payments for each payment method
    for payment in payments:
        payment_count[payment.payment_method] = payment_count.get(payment.payment_method, 0) + 1
      
    # Calculate the percentage of payments for each payment method
    payment_percentages = {}
    for payment_method, count in payment_count.items():
        #key and values
        print(payment_method,count)
        if(payment_method=="Paid by Razorpay"):
            payment_method = "Razorpay"
        payment_percentages[payment_method] = round((count / total_payments) * 100)
        print( payment_percentages[payment_method])
    return payment_percentages


def revenue():
    today = timezone.now().date()
    payments_today = Payment.objects.filter(paid=True, created_at=today)
    total_income_today = payments_today.aggregate(total=Sum('amount_paid'))['total'] or 0
    return total_income_today

def orderStat():
    today = timezone.now().date()
    orders_today = Payment.objects.filter(created_at=today)
    count_today = orders_today.count()
    return count_today

@never_cache
def adminLogin(request):
    msg = None
    if request.user.is_authenticated:
        return redirect ('adminapp:adminhome')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        try:
            if user.is_superuser:
                login(request, user)
                return redirect('adminapp:adminhome')
            else:
                msg = "Invalid Credentials"
        except:
            msg = "Invalid Credentials"
    dic = {'msg': msg}
    return render(request, 'admin/adminlogin.html', dic)


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def adminHome(request):
    return render(request, 'admin/adminbase.html')


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def adminDashboard(request):
    numberOfOrders = Order.objects.all().count()
    numberOfUsers = Customer.objects.all().count()
    numberOfProducts = Product.objects.all().count()
    numberOfCategories = Category.objects.all().count()
    total_income = Payment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum']
    last_orders = Order.objects.all().order_by('-created_at')[:5]

    # Calculate the payment sum for COD
    cod_sum = Payment.objects.filter(payment_method='COD').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    cod_sum= round(cod_sum)
    # Calculate the payment sum for Razorpay
    razorpay_sum = Payment.objects.filter(payment_method='Paid by Razorpay').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    razorpay_sum = round(razorpay_sum)
    payment_percentages = calculateNumberOfOrdersByPaymentMethod()
    total_income_today=revenue()
    total_income_today = round(total_income_today)
    count_today =orderStat()
    products_out_of_stock = Product.objects.filter(stock__lte=0)
    print(products_out_of_stock)
    total_income = round(total_income)
    context={
        'numberOfOrders': numberOfOrders,
        'numberOfUsers': numberOfUsers,
        'numberOfProducts': numberOfProducts,
        'numberOfCategories': numberOfCategories,
        'total_income':total_income,
        'last_orders':last_orders,
        'payment_percentages': payment_percentages,
        'cod_sum':cod_sum,
        'razorpay_sum':razorpay_sum,
        'total_income_today':total_income_today,
        'count_today':count_today,
        'products_out_of_stock':products_out_of_stock

    }
    return render(request, 'admin/admindashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
@never_cache
def addCategory(request):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        cat_image = request.FILES.get('cat_image')

        slug = slugify(name)

        category = Category(category_name=name, description=description, cat_image= cat_image, slug=slug)
        category.save()

        msg = "Category added"
        return redirect('adminapp:viewcategory')

    return render(request, 'admin/addcategory.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def viewCategory(request):
    category = Category.objects.all()
    paginator = Paginator(category, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewcategory.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def editCategory(request, pid):
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        if('name' in request.POST):
            print("1")
            name = request.POST['name']
            category.category_name = name
            category.save()

        if('description' in request.POST):
            print("2")
            description = request.POST['description']
            category.description = description
            category.save()

        if('cat_image' in request.FILES):
            print("3")
            cat_image = request.FILES.get('cat_image')
            category.cat_image = cat_image
            category.save()

        msg = "Category Updated"
        return redirect('adminapp:viewcategory')

    return render(request, 'admin/editcategory.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def deleteCategory(request, pid):
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('adminapp:viewcategory')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def addProduct(request):
    category = Category.objects.all()
    if request.method == "POST":
        name = request.POST['name']
        price = request.POST['price']
        stock= request.POST['stock']
        cat = request.POST['category']

        desc = request.POST['desc']
        image = request.FILES['image']
        slug = slugify(name)

        catobj = Category.objects.get(id=cat)
        Product.objects.create( product_name=name, price=price,  category=catobj, description=desc, stock=stock, images=image)
        messages.success(request, "Product added")
        return redirect('adminapp:viewproduct')
    return render(request, 'admin/addproduct.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def viewProduct(request):
    products = Product.objects.all()
    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print(page_obj)
    return render(request, 'admin/viewproduct.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def editProduct(request, pid):
    product = Product.objects.get(id=pid)
    category = Category.objects.all()
    if request.method == "POST":

        if('name' in request.POST):
            name = request.POST['name']
            product.save()

        if('price' in request.POST):
            price = request.POST['price']
            product.save()

        if('category' in request.POST):
            cat = request.POST['category']
            product.save()

        if('stock' in request.POST):
            stock= request.POST['stock']
            product.save()

        if('desc' in request.POST):
            desc = request.POST['desc']
            product.save()

        try:
            image = request.FILES['image']
            product.images = image
            product.save()

        except:
            pass
        catobj = Category.objects.get(id=cat)
        Product.objects.filter(id=pid).update(product_name=name, price=price, category=catobj, stock=stock, description=desc)
        messages.success(request, "Product Updated")
        return redirect('adminapp:viewproduct')
    return render(request, 'admin/editproduct.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def deleteProduct(request, pid):
    product = Product.objects.get(id=pid)
    product.delete()
    messages.success(request, "Product Deleted")
    return redirect('adminapp:viewproduct')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def manageUser(request):
    users = Customer.objects.all()
    paginator = Paginator(users, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'admin/manageuser.html',locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def userBlock(request,u_id) :
    users=Customer.objects.get(id=u_id)
    if users.is_active == True :
        users.is_active= False
        users.save()
        return redirect('adminapp:manageuser')
    else:

        users.is_active= True
        users.save()
        return redirect('adminapp:manageuser')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def viewUsers(request):
    users = Customer.objects.all()
    paginator = Paginator(users, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewusers.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def manageOrder(request):
    orders=Order.objects.all().order_by('id')
    paginator = Paginator(orders, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin/manageorder.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def adminLogout(request):
    auth.logout(request)
    if 'username' in request.session:
        request.session.flush()
    return redirect('adminapp:adminlogin')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def updateOrder(request, id):
    if request.method == 'POST':
        order = Order.objects.get(id=id)
        status = request.POST.get('status')

        print(status)
        if(status):
            order.status = status
            order.save()
        if status  == "Delivered":
            try:
                payment = Payment.objects.get(payment_id = order.order_number, status = False)
                print(payment)
                if payment.payment_method == 'Cash on Delivery':
                    payment.paid = True
                    payment.save()
            except:
                pass
    return redirect('adminapp:manageorder')




@user_passes_test(lambda u: u.is_superuser)
@never_cache
def addCoupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('adminapp:viewcoupon')
    else:
        form = CouponForm()
    return render(request, 'admin/addcoupon.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def viewCoupon(request):
    coupons = Coupon.objects.all()
    paginator = Paginator(coupons, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewcoupon.html', locals())



@user_passes_test(lambda u: u.is_superuser)
@never_cache
def editCoupon(request, pid):
    coupon = Coupon.objects.get(id=pid)

    if request.method == "POST":
        form = CouponForm(request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, "Coupon Updated")
            return redirect('adminapp:viewcoupon')
    else:
        form = CouponForm(instance=coupon)
        messages.error(request, "fill all fields")

    return render(request, 'admin/editcoupon.html', {'form': form, 'coupon': coupon})

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def deleteCoupon(request, pid):
    coupon = Coupon.objects.get(id=pid)
    coupon.delete()
    messages.success(request, "Coupon Deleted")
    return redirect('adminapp:viewcoupon')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def trigerEmail(request):
    user = Customer.objects.all()
    for user in user:
        if user.is_superuser:
            pass
        else:
            cart_item=CartItem.objects.filter(customer=user)
            if cart_item:
                subject = 'Homely Furnictures'
                message = ' Dear customer, You still have items abandoned in your cart that you have not purchased. Please log in to your account and complete your purchase.\n\nThank you for shopping with us!'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email,]
                send_mail(subject, message, email_from, recipient_list)
    return redirect('adminapp:adminhome')

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchUser(request):
    keyword = request.GET.get('keyword')
    users = Customer.objects.filter(Q(email__icontains=keyword))
    paginator = Paginator(users, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewusers.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchManageUser(request):
    keyword = request.GET.get('keyword')
    users = Customer.objects.filter(Q(username__icontains=keyword) | Q(email__icontains=keyword))
    # users = Customer.objects.filter(Q(email__icontains=keyword))
    paginator = Paginator(users, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/manageuser.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchOrder(request):
    keyword = request.GET.get('keyword')
    print(keyword)
    orders = Order.objects.filter( Q(status__icontains=keyword)|Q(order_number__icontains=keyword))
    print(orders)
    paginator = Paginator(orders, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/manageorder.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchProduct(request):
    keyword = request.GET.get('keyword')
    products = Product.objects.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword)).order_by('-created_date')
    paginator = Paginator(products, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewproduct.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchCoupon(request):
    keyword = request.GET.get('keyword')
    coupons = Coupon.objects.filter(Q(code__icontains=keyword)).order_by('-valid_from')
    paginator = Paginator(coupons, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewcoupon.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def searchCategory(request):
    keyword = request.GET.get('keyword')
    categories = Category.objects.filter(Q(description__icontains=keyword) | Q(category_name__icontains=keyword))
    paginator = Paginator(categories, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin/viewcategory.html', locals())

@user_passes_test(lambda u: u.is_superuser)
@never_cache
def viewOrder(request, id):
    order = Order.objects.get(id=id)
    print(order)

    # order =Order.objects.filter(id=id,user=request.user).first()
    print(order)
    orderitems = OrderProduct.objects.filter(order=order)
    print(orderitems)

    try:
     userCoupon = UserCoupon.objects.get(order=order)
     print(userCoupon)
    except:
      userCoupon={"used":False}
    context={
        'order': order,
        'orderitems':orderitems,
        'userCoupon':userCoupon
    }
    return render(request, 'admin/vieworder.html', context)


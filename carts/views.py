from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from store.models import  CartItem
from userapp.models import Customer, Address
from store.models import Product
from .models import wishlistTable
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_protect
from order.models import Coupon, UserCoupon
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
@login_required(login_url='userapp:login')
def addToCart(request, product_id):
    if request.user.is_authenticated :
        current_user=request.user
        quantity = request.POST.get('quantity')
        if quantity is None:
            product_quantity = 1
        else:
            product_quantity= int(quantity)

        product = get_object_or_404(Product, id=product_id)

        item_exists = CartItem.objects.filter(customer_id=current_user.id,product_id=product.id).exists()
        if (item_exists):
            item=CartItem.objects.get(product_id=product.id,customer_id=current_user.id)
            quantity_expected=item.quantity + product_quantity
            print(product.stock,item.quantity,quantity_expected)
            if product.stock>quantity_expected:

                item.quantity = item.quantity + product_quantity
                item.save()
                messages.success(request,  f"{product.product_name} are added to Cart.")
            else:

                item.quantity = product.stock
                item.save()
                messages.info(request,  f"{product.stock} items left. All of them are added to Cart.")
        else:
            if(product.stock>=product_quantity):
                item = CartItem.objects.create(customer_id=current_user.id, product_id=product.id,quantity=product_quantity)
                messages.success(request, f"{product.product_name} added to cart!")
            else:
                product_quantity = product.stock
                item = CartItem.objects.create(customer_id=current_user.id, product_id=product.id,quantity=product_quantity)
                messages.info(request,  f"{product.stock} items left. All of them are added to Cart.")

        return redirect('carts:cart')
    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('userapp:login')



@login_required(login_url='userapp:login')
def cart(request):
    if request.user.is_authenticated :
        current_user=request.user

        items=CartItem.objects.filter(customer_id=current_user.id)
        cart_items = []
        total = 0
        addresses=Address.objects.filter(user_id=current_user.id)
        for cart_item in items:
            print(cart_item.product_id)
            product = get_object_or_404(Product, id=cart_item.product_id)
            quantity = cart_item.quantity
            print(quantity, product.stock)
            if(quantity>0):
                if(quantity<product.stock):
                    price = product.price * quantity
                    total += price
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'price': price
                    })
                elif (quantity==product.stock):
                    cart_item.quantity =product.stock
                    cart_item.save()
                    messages.info(request,  f"{product.stock} items left. All of them are added to Cart & Cart updated.")
                    quantity = cart_item.quantity
                    price = product.price * quantity
                    total += price
                    cart_items.append({
                        'product': product,
                        'quantity': quantity,
                        'price': price
                    })
                else:
                    messages.info(request,  f"{product.product_name} is out of Stock. Item removed from cart.")
                    cart_item.delete()
            else:
                cart_item.delete()


        print(cart_items)
        context = {
            'cart_items': cart_items,
            'total': total,
        'AllAddress': addresses
        }
        return render(request, 'shop/cart.html', context)
    
@never_cache
@login_required(login_url='userapp:login')
def addCartItem(request,product_id):
    if request.user.is_authenticated :
        current_user=request.user
        product = get_object_or_404(Product, id=product_id)
        print(product)
        item=CartItem.objects.get(customer_id=current_user.id, product=product)
        print(item)
        item.quantity = item.quantity + 1
        if (product.stock>item.quantity):
            item.save()
            return redirect('carts:cart')
        else:
            messages.warning(request,"Product Out Of Stock...! Can't be added to cart")
            return redirect('carts:cart')

    else:
        messages.warning(request, "Please log in to add items to cart.")
        return redirect('carts:cart')

@never_cache
@login_required(login_url='userapp:login')
def removeCartItem(request,product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)

    cart_items = CartItem.objects.filter(customer_id=current_user.id, product=product)
    print(cart_items)
    for cart_item in cart_items:
        if cart_item.quantity == 1:
            cart_item.delete()  # remove the item from the cart if the quantity is 1
        else:
            cart_item.quantity -= 1
            cart_item.save()  # decrement the quantity by 1
    return redirect('carts:cart')

@never_cache
@login_required(login_url='userapp:login')
def removeCartProduct(request,product_id):
    current_user = request.user
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(customer_id=current_user.id,product_id=product.id)
    cart_item.delete()
    return redirect('carts:cart')


@login_required(login_url='userapp:login')
def wishlist(request):
    user = request.user
    witems=wishlistTable.objects.filter(customer_id=user.id)
    print(witems)
    witem_count = witems.count()
    context={
        'witems':witems,
        'witem_count':witem_count,
    }
    return render(request,'shop/wishlist.html',context)

@never_cache
@login_required(login_url='userapp:login')
def addToWish(request,product_id):
    if request.user.is_authenticated:
        product = Product.objects.get(pk=product_id)
        user = request.user
        if wishlistTable.objects.filter(product=product,customer_id=user.id).exists():
            return redirect('carts:wishlist')
        else:
            wishlistTable.objects.create(product=product,customer_id=user.id)
            return redirect('carts:wishlist')
    else:
        return redirect('userapp:login')
    
@never_cache
@login_required(login_url='userapp:login')
def removeWishItem(request,product_id):
    user = request.user
    wishItem=wishlistTable.objects.get(product_id=product_id,customer_id=user.id)
    wishItem.delete()
    return redirect('carts:wishlist')

@login_required(login_url='userapp:login')
@csrf_protect
@never_cache
def checkout(request):
    total=0
    quantity=0
    amountToBePaid =0
    cart_items=None
    msg=''
    coupon_discount = 0
    coupon_code = ''
    discount = False
    coupon = ''
    try:
        newAddress_id = request.POST.get('addressSelected')
        if(newAddress_id == None):
            messages.error(request,'Select An Address to Proceed to Checkout.')
            return redirect('carts:cart')
        else:
            address  = Address.objects.get(id = newAddress_id)
        current_user=request.user
        user=Customer.objects.get(id=current_user.id)
        cart_items=CartItem.objects.filter(customer_id=current_user.id)
        for cart_item in cart_items:
            total+=(cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(5 * total)/100
        grand_total=total+tax
        amountToBePaid = grand_total
        if ('couponCode' in request.POST):
            print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
            coupon_code = request.POST.get('couponCode')
            try:
                coupon = Coupon.objects.get(code = coupon_code)
                
                grand_total = request.POST['grand_total']
                coupon_discount = 0
                if (coupon.active):
                    try:
                        instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
                        print(instance)
                        print('dddddddddddddddddddddddddddddd')
                    except ObjectDoesNotExist:
                        instance = None
                        print('oooooooooooooooooooooooooooooooooooo')
                    # instance = UserCoupon.objects.get(user = request.user ,coupon = coupon)
                    if(instance):
                        pass
                    else:
                        instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
                        print('hhhhhhhhhhhhhhhhhhhhhhhhhhh')
                        print(instance)
                    if(not instance.used):
                        if float(grand_total) >= float(instance.coupon.min_value):
                            coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                            amountToBePaid = float(grand_total) - coupon_discount
                            amountToBePaid = format(amountToBePaid, '.2f')
                            coupon_discount = format(coupon_discount, '.2f')
                            msg = 'Coupon Applied successfully'
                            discount=True
                        else:
                            msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
                    else:
                        msg = 'Coupon is already used'
                else:
                    msg="Coupon is not Active!"
            except:
                msg="Invalid Coupon Code!"
        else:
            try:
                instance = UserCoupon.objects.get(user=request.user, used= False)
                instance.delete()
            except ObjectDoesNotExist:
                instance = None
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'user':user,
        'addressSelected':address,
        'amountToBePaid': amountToBePaid,
        'msg':msg,
        'coupon':coupon,
        'coupon_discount': coupon_discount,
        'discount': discount
    }
    return render(request,'shop/checkout.html',context) 


def productDetail(request,id):

     s_pro=Product.objects.get(id=id)

     return render(request, 'shop/productdetail.html',locals())
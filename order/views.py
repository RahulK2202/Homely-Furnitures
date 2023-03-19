from django.shortcuts import render,redirect
from store.models import  CartItem
from userapp.models import Customer, Address
from .models import Order, OrderProduct, Payment,Coupon,UserCoupon
import datetime
from store.models import Product
from django.http import JsonResponse
import json
from django.contrib import messages
import random
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import razorpay
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail
import homely.settings

# Create your views here.

def calculateCartTotal(request):
   cart_items   = CartItem.objects.filter(customer=request.user)
   if not cart_items:
      return redirect('category')
   total = 0
   for cart_item in cart_items:
      total    += (cart_item.product.price * cart_item.quantity)
      tax = (5 * total) / 100
      grand_total = tax + total
   return total, tax, grand_total

def checkCoupon(request):
   try:
      coupon_code = request.POST.get('couponCode')
      coupon = Coupon.objects.get(code = coupon_code)
      try:
         instance = UserCoupon.objects.get(user=request.user, coupon=coupon)
      except ObjectDoesNotExist:
         instance = None
         if(instance):
            pass
         else:
            instance = UserCoupon.objects.create(user = request.user ,coupon = coupon)
   except:
      instance = None
   return instance

@csrf_protect
@login_required(login_url='userapp:login')
@never_cache
def placeOrder(request):
   if request.method =='POST':
         if ('couponCode' in request.POST):
            instance = checkCoupon(request)

         cart_items   = CartItem.objects.filter(customer=request.user)
         if not cart_items:
            return redirect('category')
         newAddress_id = request.POST.get('addressSelected')
         print('newAddress_id')
         address  = Address.objects.get(id = newAddress_id)
         newOrder =Order()
         newOrder.user=request.user
         newOrder.address = address
         yr = int(datetime.date.today().strftime('%Y'))
         dt = int(datetime.date.today().strftime('%d'))
         mt = int(datetime.date.today().strftime('%m'))
         d = datetime.date(yr,mt,dt)
         current_date = d.strftime("%Y%m%d")
         rand = str(random.randint(1111111,9999999))
         order_number = current_date + rand
         newPayment = Payment()
         if('payment_id' in request.POST ):
            newPayment.payment_id = request.POST.get('payment_id')
            newPayment.paid = True
         else:
            newPayment.payment_id = order_number
            payment_id  =order_number
         newPayment.payment_method = request.POST.get('payment_method')
         newPayment.customer = request.user
         newPayment.save()
         newOrder.payment = newPayment
         total, tax, grand_total = calculateCartTotal(request)
         newOrder.order_total = grand_total
         if(instance):
            if(instance.used == False):
                if float(grand_total) >= float(instance.coupon.min_value):
                    coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
                    amountToBePaid = float(grand_total) - coupon_discount
                    amountToBePaid = format(amountToBePaid, '.2f')
                    coupon_discount = format(coupon_discount, '.2f')
                    newOrder.order_discount = coupon_discount
                    newOrder.paid_amount = amountToBePaid
                    instance.used = True
                    newOrder.paid_amount = amountToBePaid
                    newPayment.amount_paid = amountToBePaid
                    instance.save()
                else:
                    msg='This coupon is only applicable for orders more than ₹'+ str(instance.coupon.min_value)+ '\- only!'
            else:
                newOrder.paid_amount = grand_total
                newPayment.amount_paid = grand_total
                newOrder.discount=0
                msg = 'Coupon is not valid'
         else:
            newOrder.paid_amount = grand_total
            newPayment.amount_paid = grand_total
            msg = 'Coupon not Added'
         newPayment.save()
         newOrder.payment = newPayment
         order_number = 'home'+ order_number
         newOrder.order_number =order_number
         #to making order number unique
         while Order.objects.filter(order_number=order_number) is None:
            order_number = 'brotoz'+order_number
         newOrder.tax=tax
         newOrder.save()
         newPayment.order_id = newOrder.id
         newPayment.save()
         newOrderItems = CartItem.objects.filter(customer=request.user)
         for item in newOrderItems:
            OrderProduct.objects.create(
                order = newOrder,
                customer=request.user,
                product=item.product,
                product_price=item.product.price,
                quantity=item.quantity
            )
            #TO DECRESE THE QUANTITY OF PRODUCT
            orderproduct = Product.objects.filter(id=item.product_id).first()
            if(orderproduct.stock<=0):
               messages.warning(request,'Sorry, Product out of stock!')
               orderproduct.is_available = False
               orderproduct.save()
               item.delete()
               return redirect('carts:cart')
            elif(orderproduct.stock < item.quantity):
               messages.success(request,  f"{orderproduct.stock} only left in cart.")
               return redirect('carts:cart')
            else:
               orderproduct.stock -=  item.quantity
            orderproduct.save()
         if(instance):
            instance.order = newOrder
            instance.save()
        # TO CLEAR THE USER'S CART
         cart_item=CartItem.objects.filter(customer=request.user)
         cart_item.delete()
         messages.success(request,'Order Placed Successfully')
         payMode =  request.POST.get('payment_method')
         if (payMode == "Paid by Razorpay" ):
            return JsonResponse ({'status':"Your order has been placed successfully"})
         elif (payMode == "COD" ):
            request.session['my_context'] = {'payment_id':payment_id}
            return redirect('order:order_complete')
   return redirect('carts:checkout')


def razorPayCheck(request):
   total=0
   coupon_discount =0
   amountToBePaid = 0
   current_user=request.user
   cart_items=CartItem.objects.filter(customer_id=current_user.id)
   if cart_items:
      for cart_item in cart_items:
         total+=(cart_item.product.price*cart_item.quantity)
      tax=(5 * total)/100
      grand_total=total+tax
      grand_total = round(grand_total,2)
      try:
         instance = UserCoupon.objects.get(user=request.user, used=False)
         coupon = instance.coupon.code
         if float(grand_total) >= float(instance.coupon.min_value):
            coupon_discount = ((float(grand_total) * float(instance.coupon.discount))/100)
            amountToBePaid = float(grand_total) - coupon_discount
            amountToBePaid = format(amountToBePaid, '.2f')
            coupon_discount = format(coupon_discount, '.2f')
      except ObjectDoesNotExist:
         instance = None
         amountToBePaid = grand_total
         coupon_discount = 0
         coupon =None
      return JsonResponse({
         'grand_total' : grand_total,
         'coupon': coupon,
         'coupon_discount':coupon_discount,
         'amountToBePaid':amountToBePaid
      })
   else:
      return redirect('category')



@never_cache
@login_required(login_url=('login'))
def myOrders(request):
    orders=Order.objects.filter(user=request.user).order_by('-created_at')
    for order in orders:
        order.created_at = order.created_at.date()
    context ={
        'orders':orders
    }
    return render(request,'order/myorders.html',context)



@never_cache
@login_required(login_url=('login'))
def viewOrder(request, id):
    order =Order.objects.filter(id=id,user=request.user).first()
    orderitems = OrderProduct.objects.filter(order=order)

    try:
     userCoupon = UserCoupon.objects.get(order=order)
    except:
      userCoupon={"used":False}
    context={
        'order': order,
        'orderitems':orderitems,
        'userCoupon':userCoupon
    }
    return render(request,'order/vieworder.html',context)



@login_required(login_url='userapp:login')
@never_cache
def cancelOrder(request,id):

   client = razorpay.Client(auth=(homely.settings.API_KEY, homely.settings.RAZORPAY_SECRET_KEY))
   # client = razorpay.Client(auth=("rzp_test_d8CuRUKczNyzCd", "8rt6NVn4AxDo7FCkDPmq9k8l"))
   order = Order.objects.get(id=id,user=request.user)
   payment=order.payment
   msg=''
   if (payment.payment_method == 'Paid by Razorpay'):
      payment_id = payment.payment_id
      amount = payment.amount_paid
      amount=amount*100
      try:
         captured_amount = client.payment.capture(payment_id,amount)
         if captured_amount['status'] == 'captured' :
            refund_data = {
               "payment_id": payment_id,
               "amount": amount,  # amount to be refunded in paise
               "currency": "INR",
            }
         else:
            msg = "Your bank has not completed the payment yet."
      except:
         refund_data = {
            "payment_id": payment_id,
            "amount": amount,  # amount to be refunded in paise
            "currency": "INR",
         }
      # payment = client.payment.fetch(payment_id)
      print(payment_id)
      refund = client.payment.refund(payment_id, refund_data)
      print(refund)
      if refund is not None:
         current_user=request.user
         order.refund_completed = True
         order.status = 'Cancelled'
         payment = order.payment
         payment.refund_id = refund['id']
         payment.save()
         order.save()
         msg ="Your order has been successfully cancelled and amount has been refunded!"
         mess=f'Hello\t{current_user.first_name},\nYour order has been canceled,Money will be refunded with in 1 hour\nThanks!'
         send_mail(
                        "Hoely Furnitures - Order Cancelled",
                        mess,
                        settings.EMAIL_HOST_USER,
                        [current_user.email],
                        fail_silently = False
                     )
      else :
         msg ="Your order is not cancelled because the refund couldnot be  completed now. Please try again later. If the issue continues, CONTACT THE SUPPORT TEAM!"
         pass
   else :
      if(payment.paid):
         order.refund_completed = True
         order.status = 'Cancelled'
         msg ="YOUR ORDER HAS BEEN SUCCESSFULLY CANCELLED!"
         order.save()
      else:
         order.status = 'Cancelled'
         order.save()
         msg ="Your payment has not been recieved yet. But the order has been cancelled.!"
   orderitems = OrderProduct.objects.filter(order=order)
   context={
        'order': order,
        'orderitems':orderitems,
        'msg':msg
    }
   return render(request,'order/vieworder.html',context)

@csrf_protect
@never_cache
def orderComplete(request):
    product_items = []
    total=0
    if ('payment_id' in request.GET):
      payment_id = request.GET.get('payment_id')
      payment = Payment.objects.get(payment_id=payment_id)

    else:
      try:
         my_context = request.session.get('my_context', {})
         payment_id = my_context['payment_id']
         payment = Payment.objects.get(payment_id=payment_id)
      except:
         user=request.user
         payment = Payment.objects.filter(customer=user, payment_method ='COD').order_by('-created_at').first()

    order_details = Order.objects.get(payment=payment)
    orderitems = OrderProduct.objects.filter(order=order_details.id)
    for order_item in orderitems:
            print(order_item.product_id)
            product = Product.objects.get(id=order_item.product.id)
            quantity = order_item.quantity
            price = order_item.product_price * quantity
            total += price
            product_items.append({
                'product': product,
                'quantity': quantity,
                'price': price
            })
    context={
        'total':total,
        'order': order_details,
        'orderitems':orderitems,
        'product_items': product_items,
    }

    return render(request, 'order/order_completed.html',context)

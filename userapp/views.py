from django.shortcuts import render,redirect,reverse
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .forms import CreateUserForm, Customer, UpdateUserForm
from .models import Address
from django.views.decorators.cache import never_cache
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from store.models import Product
from order.models import Order
import random
from .models import UserOTP
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from category.models import Category
from datetime import datetime
from order.models import Coupon
from django.views.decorators.cache import never_cache


# Create your views here.
@never_cache
def home(request):
    products = Product.objects.all().filter(is_available=True)
    category = Category.objects.all()
    products = Product.objects.order_by('-stock')

# Retrieve the first three products
    top3products = products[:3]
    now = datetime.now()
    remaining_time_array=[]
    valid_coupons = Coupon.objects.filter(valid_from__lte=now, valid_at__gte=now)
    for coupon in valid_coupons:
        formatted_date = coupon.valid_at.strftime('%d %m %Y %H %M')
        print(formatted_date)
        remaining_time_array.append({
                'coupon': coupon,
                'date': formatted_date

            })


# Retrieve coupons that are valid now
    print(remaining_time_array)
    context = {
        'products': products,
        'category' : category,
        'top3products':top3products,
        'valid_coupons':valid_coupons,
        'remaining_time_array':remaining_time_array
    }
    return render(request, 'index.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect(home)
    usr = None
    #Register Form
    if request.method=='POST':
        get_otp=request.POST.get('otp')
        # OTP Verification
        if get_otp:
            get_usr=request.POST.get('usr')
            usr=Customer.objects.get(username=get_usr)
            if int(get_otp)==UserOTP.objects.filter(user=usr).last().otp:
                usr.is_active=True
                usr.save()
                messages.success(request,f'Account is created for {usr.username}')
                return redirect('userapp:login')
            else:
                messages.warning(request,f'You Entered a wrong OTP')
                return render(request,'accounts/register.html',{'otp':True,'usr':usr})
        form = CreateUserForm(request.POST)
        #Form Validation
        if form.is_valid():
            form.save()
            email=form.cleaned_data.get('email')
            username=form.cleaned_data.get('username')
            usr=Customer.objects.get(username=username)
            print(usr)
            usr.email=email
            usr.username=username
            usr.is_active=False
            usr.save()
            usr_otp=random.randint(100000,999999)
            print(usr_otp)
            print(form.cleaned_data.get('password'))
            UserOTP.objects.create(user=usr,otp=usr_otp)
            mess=f'Hello\t{usr.username},\nYour OTP to verify your account for HOMELY is {usr_otp}\nThanks!'
            send_mail(
                    "welcome to HOMELY-Verify your Email",
                    mess,
                    settings.EMAIL_HOST_USER,
                    [usr.email],
                    fail_silently=False
                )
                # print("OTP sent to:", usr.email)
            return render(request,'accounts/register.html',{'otp':True,'usr':usr})
        else:
            errors = form.errors
            form=CreateUserForm()
            context = {'form': form, 'errors': errors}
            return render(request,'accounts/register.html',context)
    #Resend OTP
    elif (request.method == "GET" and 'username' in request.GET):
        get_usr = request.GET['username']
        if (Customer.objects.filter(username = get_usr).exists() and not Customer.objects.get(username = get_usr).is_active):
            usr = Customer.objects.get(username=get_usr)
            id = usr.id
            print (id)
            otp_usr = UserOTP.objects.get(user_id=id)
            usr_otp=otp_usr.otp
            mess = f"Hello, {usr.username},\nYour OTP is {usr_otp}\nThanks!"
            print(mess)
            send_mail(
        "Welcome to HOMELY Furnitures - Verify Your Email",
        mess,
        settings.EMAIL_HOST_USER,
        [usr.email],
        fail_silently = False
      )
            return render(request,'accounts/register.html',{'otp':True,'usr':usr})
    else:
            errors = ''
    form=CreateUserForm()
    context = {'form': form, 'errors': errors}
    return render(request,'accounts/register.html',context)



@never_cache
def login(request):
    if request.user.is_authenticated:
        return redirect('userapp:home')
    if request.method == 'POST':
        form_email = request.POST['email']
        form_password = request.POST['password']
        try:
            customer=Customer.objects.get(email=form_email)
            form_username = customer.username
            if(customer.is_active):
                user = auth.authenticate(username=form_username, password=form_password)
                if user is not None:
                    auth.login(request, user)
                    return redirect('userapp:home')
                else:
                    messages.info(request, 'Invalid username or password')
                    return redirect(reverse('userapp:login'))
            else:
                messages.info(request, 'You are blocked from logging in by admin. Please contact admin.')
                return redirect(reverse('userapp:login'))
        except:
            messages.info(request, 'Oops...!You are not registered with HOMELY..!')
            return redirect(reverse('userapp:login'))
    else:
        return render(request, 'accounts/login.html')

@never_cache
 
def editprofile(request):
    id = request.user.id
    user = Customer.objects.get(pk=id)
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('userapp:dashboard')
        else:
            messages.error(request, 'There was an error while updating your profile.')
    else:
        form = UpdateUserForm(instance=user)
        context = {'form': form}
        print(context)
    return render(request, 'accounts/editprofile.html', context)

@login_required(login_url='userapp:login')
def viewprofile(request):
    return render(request, 'accounts/viewprofile.html')

@never_cache
@login_required(login_url='userapp:login')
def changepassword(request):
    if request.method=='POST':
        current_password=request.POST["current_password"]
        new_password=request.POST["new_password"]
        confirm_password=request.POST["confirm_password"]

        user=Customer.objects.get(username__exact=request.user.username)

        if new_password==confirm_password:

            success=user.check_password(current_password)

            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request,"Password updated successfully")
                return redirect('userapp:login')

            messages.error(request,"Please enter valid current password")
            return redirect('userapp:changepassword')
        else:
            messages.error(request,"Password does not match")
            return redirect('userapp:changepassword')
    return render(request,"accounts/changepassword.html")

@never_cache
def forgotPassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email__exact=email)
           #reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,

                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                 # Generate a token for a user also
                'token':default_token_generator.make_token(user),
            })
            to_email = email
            send_email=EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            send_email.send()

            messages.success(request,"Password reset email has been sent to your email")

            return redirect('userapp:login')
        else:
            messages.error(request,'Account does not exists')
            return redirect('login')
    return render(request,'accounts/forgotPassword.html')

@never_cache
def resetPassword(request):
    if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password == confirm_password:
            uid=request.session.get('uid')
            user= Customer.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,"Password reset successful")
            return redirect('userapp:login')
        else:
          messages.error(request,"Password not match")
          return redirect('resetPassword')
    else:
     return render (request,'accounts/resetPassword.html')


@login_required(login_url='userapp:login')
def dashboard(request):
    user = request.user

    context = {'user': user}

    return render(request, 'accounts/dashboard.html', context)

@never_cache
def resetpassword_validate(request,uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Customer._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError,Customer.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid']=uid
        messages.success(request,"  Please reset ur password")
        return redirect('userapp:resetPassword')
    else:
        messages.error(request,"This link has been expired")
        return redirect('login')


@login_required(login_url='userapp:login')
def viewAddresses(request):
    current_user = request.user
    addresses=Address.objects.filter(user_id=current_user.id)
    return render(request, 'accounts/viewaddresses.html',{'AllAddress': addresses})

@never_cache
@login_required(login_url='userapp:login')
def deleteAddress(request, address_id):
    address=Address.objects.get(id = address_id)
    address.delete()
    return redirect('userapp:viewAddresses')

@never_cache
@login_required(login_url='userapp:login')
def editAddress(request, address_id):
    if request.method == 'POST':
        address=Address.objects.get(id = address_id)
        address.first_name = request.POST['first_name']
        address.last_name = request.POST['last_name']
        address.phone = request.POST['phone']
        address.email = request.POST['email']
        address.address_line_1 = request.POST['address_line_1']
        address.address_line_2 = request.POST['address_line_2']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.country = request.POST['country']
        address.zip_code = request.POST['zip_code']
        address.user = request.user
        try:
            address.save()
        except:
            messages.warning(request,f'There are some errors with the values you entered.')


        return redirect('userapp:viewAddresses')
    else:
        address=Address.objects.get(id = address_id)
        return render(request,'accounts/editaddress.html', {"address": address})

@never_cache
@login_required(login_url='userapp:login')
def addNewAddress(request, form_from):
    if request.method == 'POST':
        form_from = request.POST['form_from']
        address=Address()
        address.first_name = request.POST['first_name']
        address.last_name = request.POST['last_name']
        address.phone = request.POST['phone']
        address.email = request.POST['email']
        address.address_line_1 = request.POST['address_line_1']
        address.address_line_2 = request.POST['address_line_2']
        address.city = request.POST['city']
        address.state = request.POST['state']
        address.country = request.POST['country']
        address.zip_code = request.POST['zip_code']
        address.user = request.user
        try:
            address.save()
            if(form_from == "0"):

                return redirect('userapp:viewAddresses')
            else:

                return redirect('carts:cart')

        except:
            messages.warning(request,f'There are some errors with the values you entered.')
    else:
        return render(request,'accounts/addaddress.html',{ "form_from" : form_from})

@login_required(login_url='userapp:login')
def logout(request):
 auth.logout(request)
 if 'username' in request.session:
        request.session.flush()
 return redirect('userapp:home')


